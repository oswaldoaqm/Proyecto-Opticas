"""Optica paraxial con matrices ABCD (altura x y angulo respecto al eje y).

Supone luz que viaja en +y, objeto debajo de la lente y medio exterior de indice 1.
Los radios de vertice ya traen el signo correcto: R = 1/s''(0) (decision 0001).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .lente import Lente


def matriz_refraccion(n1: float, n2: float, R: float) -> np.ndarray:
    """Refraccion paraxial en una cara de radio R (R > 0: centro de curvatura del lado de salida)."""
    potencia = 0.0 if np.isinf(R) else (n2 - n1) / R
    return np.array([[1.0, 0.0], [-potencia / n2, n1 / n2]])


def matriz_traslacion(d: float) -> np.ndarray:
    """Avance una distancia d a lo largo del eje."""
    return np.array([[1.0, d], [0.0, 1.0]])


def matriz_sistema(lente: Lente) -> np.ndarray:
    """Matriz desde el vertice de la cara de abajo (g) hasta el vertice de la de arriba (f)."""
    return (matriz_refraccion(lente.n, 1.0, lente.arriba.radio_vertice)
            @ matriz_traslacion(lente.espesor)
            @ matriz_refraccion(1.0, lente.n, lente.abajo.radio_vertice))


def focal_efectiva(lente: Lente) -> float:
    """Distancia focal efectiva de la lente gruesa: f = -1 / C."""
    C = matriz_sistema(lente)[1, 0]
    return np.inf if C == 0 else -1.0 / C


def foco_imagen(lente: Lente) -> float:
    """Posicion (y) del foco imagen: donde cruzan el eje los rayos que llegan paralelos a el."""
    A, B, C, D = matriz_sistema(lente).ravel()
    return np.inf if C == 0 else lente.arriba.y_vertice - A / C


def planos_principales(lente: Lente) -> tuple[float, float]:
    """Posiciones (y) de los planos principales H (lado del objeto) y H' (lado de la imagen).

    Con s medida desde H hasta el objeto y s' desde H' hasta la imagen, la ecuacion de Gauss
    1/s + 1/s' = 1/f, con la focal efectiva f, da la imagen paraxial de la lente gruesa sin
    aproximar nada mas: el espesor queda en f y en la posicion de los planos.
    """
    A, B, C, D = matriz_sistema(lente).ravel()
    if C == 0:
        raise ValueError("una lente sin potencia no tiene planos principales")
    return lente.abajo.y_vertice + (D - 1.0) / C, lente.arriba.y_vertice + (1.0 - A) / C


@dataclass(frozen=True)
class ImagenParaxial:
    y: float          # posicion de la imagen sobre el eje
    x: float          # altura de la imagen
    aumento: float    # aumento lateral
    virtual: bool


def imagen_paraxial(lente: Lente, objeto) -> ImagenParaxial:
    """Imagen paraxial de un punto objeto (x_P, y_P) a traves de la lente gruesa."""
    xP, yP = float(objeto[0]), float(objeto[1])
    A, B, C, D = matriz_sistema(lente).ravel()
    s0 = lente.abajo.y_vertice - yP          # distancia objeto -> primer vertice
    den = C * s0 + D
    if den == 0:
        return ImagenParaxial(y=np.inf, x=np.inf, aumento=np.inf, virtual=False)
    si = -(A * s0 + B) / den                 # segundo vertice -> imagen
    m = A + si * C
    return ImagenParaxial(y=lente.arriba.y_vertice + si, x=m * xP, aumento=m, virtual=bool(si < 0))


def imagen_lente_delgada(lente: Lente, objeto) -> ImagenParaxial:
    """Prediccion de la ecuacion de lente delgada 1/s + 1/s' = 1/f, con la lente en su centro.

    1/f = (n - 1) (1/R1 - 1/R2), con los radios con signo de la decision 0001.
    """
    xP, yP = float(objeto[0]), float(objeto[1])
    R1, R2 = lente.abajo.radio_vertice, lente.arriba.radio_vertice
    inv_f = (lente.n - 1.0) * ((0.0 if np.isinf(R1) else 1.0 / R1) - (0.0 if np.isinf(R2) else 1.0 / R2))
    y_centro = 0.5 * (lente.abajo.y_vertice + lente.arriba.y_vertice)
    s = y_centro - yP
    inv_si = inv_f - 1.0 / s
    if inv_si == 0:
        return ImagenParaxial(y=np.inf, x=np.inf, aumento=np.inf, virtual=False)
    si = 1.0 / inv_si
    m = -si / s
    return ImagenParaxial(y=y_centro + si, x=m * xP, aumento=m, virtual=bool(si < 0))
