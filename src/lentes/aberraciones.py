"""Aberracion esferica medida con el trazado exacto (actividades 4 y 5).

Las funciones reciben y_objeto: la posicion de un objeto puntual sobre el eje (x = 0),
o None para un objeto en el infinito (rayos que llegan paralelos al eje).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize_scalar

from .lente import Lente
from .paraxial import foco_imagen, imagen_paraxial
from .trazado import rayo_hacia, trazar


def rayo_a_altura(lente: Lente, y_objeto: float | None, h: float) -> tuple[np.ndarray, np.ndarray]:
    """Punto de partida y direccion del rayo que entra a la cara g a la altura x = h."""
    if y_objeto is None:
        return np.array([h, lente.y_min - 1.0]), np.array([0.0, 1.0])
    P = np.array([0.0, float(y_objeto)])
    return P, rayo_hacia(lente, P, h)


def y_paraxial(lente: Lente, y_objeto: float | None) -> float:
    """Imagen paraxial sobre el eje (el foco imagen si el objeto esta en el infinito)."""
    return foco_imagen(lente) if y_objeto is None else imagen_paraxial(lente, (0.0, y_objeto)).y


@dataclass(frozen=True)
class Abanico:
    """Rayos emergentes de un abanico: el rayo i sale de (Qx[i], Qy[i]) con direccion (ex[i], ey[i])."""

    alturas: np.ndarray
    Qx: np.ndarray
    Qy: np.ndarray
    ex: np.ndarray
    ey: np.ndarray

    def x_en(self, y_plano: float) -> np.ndarray:
        """Altura a la que cada rayo corta el plano y = y_plano."""
        return self.Qx + (y_plano - self.Qy) * self.ex / self.ey

    def cruces(self) -> np.ndarray:
        """y donde cada rayo cruza el eje optico."""
        return self.Qy - self.Qx * self.ey / self.ex


def abanico(lente: Lente, y_objeto: float | None, alturas) -> Abanico:
    """Traza un rayo por cada altura de entrada y guarda los rayos emergentes (NaN si falla)."""
    alturas = np.asarray(alturas, dtype=float)
    datos = np.full((4, alturas.size), np.nan)
    for i, h in enumerate(alturas):
        tr = trazar(lente, *rayo_a_altura(lente, y_objeto, h))
        if tr.estado == "ok":
            Q, e = tr.salida
            datos[:, i] = Q[0], Q[1], e[0], e[1]
    return Abanico(alturas, *datos)


def aberracion_longitudinal(lente: Lente, y_objeto: float | None, alturas) -> np.ndarray:
    """dy(h): donde cruza el eje cada rayo, menos la imagen paraxial."""
    return abanico(lente, y_objeto, alturas).cruces() - y_paraxial(lente, y_objeto)


def aberracion_transversal(lente: Lente, y_objeto: float | None, alturas,
                           y_plano: float | None = None) -> np.ndarray:
    """Altura a la que cada rayo corta el plano y_plano (por defecto, el plano imagen paraxial)."""
    if y_plano is None:
        y_plano = y_paraxial(lente, y_objeto)
    return abanico(lente, y_objeto, alturas).x_en(y_plano)


def coeficiente_esferica_trazado(lente: Lente, y_objeto: float | None, h_max: float | None = None,
                                 puntos: int = 25) -> float:
    """C3 medido con el trazado: ajuste de dy = C3 h^2 + C5 h^4 + C7 h^6 con rayos cercanos al eje."""
    if h_max is None:
        h_max = 0.1 * lente.semiapertura
    hs = np.linspace(h_max / puntos, h_max, puntos)
    dy = aberracion_longitudinal(lente, y_objeto, hs)
    M = np.vstack([hs**2, hs**4, hs**6]).T
    return float(np.linalg.lstsq(M, dy, rcond=None)[0][0])


def _pupila(h_max: float, n: int) -> np.ndarray:
    """Radios de una pupila circular uniforme, en anillos de igual ancho."""
    return (np.arange(n) + 0.5) / n * h_max


def radio_rms(ab: Abanico, y_plano: float) -> float:
    """Radio RMS de la mancha en el plano y_plano.

    Con el objeto sobre el eje la lente tiene simetria de revolucion: el rayo que entra
    a la distancia rho del eje llega a la distancia |x(rho)| del eje. Por eso el abanico
    2D da la mancha 3D completa, pesando cada anillo en proporcion a rho.
    """
    x = ab.x_en(y_plano)
    return float(np.sqrt(np.sum(ab.alturas * x**2) / np.sum(ab.alturas)))


def radio_maximo(ab: Abanico, y_plano: float) -> float:
    """Radio de la mancha en el plano y_plano: el rayo que mas se aleja del eje."""
    return float(np.max(np.abs(ab.x_en(y_plano))))


def tramo_de_cruces(cruces) -> tuple[float, float]:
    """Tramo del eje entre el primer y el ultimo cruce de los rayos, con un margen chico.

    El mejor plano, con cualquiera de los criterios (radio RMS, circulo de minima confusion
    o frente de onda), esta dentro: antes del primer cruce todos los rayos se acercan al eje
    y despues del ultimo todos se alejan. No alcanza con el foco paraxial y el del borde: si
    la aberracion cambia de signo entre el centro y el borde de la pupila (aberracion zonal,
    como en una lente con caras conicas casi corregida), el mejor plano puede quedar fuera
    del tramo entre esos dos focos.
    """
    lo, hi = float(np.nanmin(cruces)), float(np.nanmax(cruces))
    margen = 0.05 * (hi - lo) + 1e-12
    return lo - margen, hi + margen


@dataclass(frozen=True)
class Focos:
    y_paraxial: float     # donde enfocan los rayos cercanos al eje
    y_marginal: float     # donde cruza el eje el rayo mas alejado (h_max)
    y_rms: float          # plano de radio RMS minimo
    rms: float
    y_circulo: float      # plano del circulo de minima confusion (radio maximo minimo)
    radio_circulo: float

    def fraccion(self, y: float) -> float:
        """Posicion de un plano entre el foco paraxial (0) y el marginal (1)."""
        return (y - self.y_paraxial) / (self.y_marginal - self.y_paraxial)


def mejores_focos(lente: Lente, y_objeto: float | None, h_max: float, n: int = 400) -> Focos:
    """Foco paraxial, foco marginal, plano de minimo radio RMS y circulo de minima confusion
    para una pupila circular de radio h_max."""
    # Los anillos de la pupila dan el radio RMS. El rayo del borde, que va al final, fija el
    # foco marginal y el circulo de minima confusion (los anillos no llegan hasta h_max).
    todos = abanico(lente, y_objeto, np.append(_pupila(h_max, n), h_max))
    anillos = Abanico(*(v[:-1] for v in (todos.alturas, todos.Qx, todos.Qy, todos.ex, todos.ey)))
    y_par = y_paraxial(lente, y_objeto)
    y_marg = float(todos.cruces()[-1])
    cotas = tramo_de_cruces(np.append(todos.cruces(), y_par))
    opciones = {"xatol": 1e-10, "maxiter": 500}
    r1 = minimize_scalar(lambda y: radio_rms(anillos, y), bounds=cotas, method="bounded", options=opciones)
    r2 = minimize_scalar(lambda y: radio_maximo(todos, y), bounds=cotas, method="bounded", options=opciones)
    return Focos(y_par, y_marg, float(r1.x), float(r1.fun), float(r2.x), float(r2.fun))
