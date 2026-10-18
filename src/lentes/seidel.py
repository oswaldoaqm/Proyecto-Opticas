"""Aberracion esferica de tercer orden: la suma de Seidel S_I.

Convencion: z es el eje optico (la y del modelo), la luz va en +z, u = dh/dz es la
pendiente del rayo paraxial marginal y c = 1/R la curvatura de vertice de cada cara
(R > 0 si el centro de curvatura esta del lado de salida, decision 0001).

En cada cara j, con el invariante de refraccion A = n (h c + u):

    S_I = sum_j [ -A_j^2 h_j (u'_j / n'_j - u_j / n_j)  +  k_j c_j^3 h_j^4 (n'_j - n_j) ]

El segundo termino es el aporte de la forma conica (vale 0 en una esfera). La
aberracion longitudinal de tercer orden del rayo que entra a la altura h es

    dy(h) = -S_I / (2 n'_k u'_k^2) = C3 h^2,

con u'_k la pendiente final del rayo marginal. S_I crece como h^4 y u'_k como h,
por eso dy crece como h^2. Solo vale para caras conicas (las que tienen k).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .lente import Lente


@dataclass(frozen=True)
class AporteCara:
    cara: str
    h: float             # altura del rayo marginal paraxial en la cara
    u: float             # pendiente antes de la cara
    u_sal: float         # pendiente despues de la cara
    A: float             # invariante de refraccion n (h c + u)
    esferico: float      # -A^2 h (u'/n' - u/n)
    por_k: float         # c^3 h^4 (n' - n): el aporte conico es k * por_k
    conico: float        # k * por_k


def aportes(lente: Lente, y_objeto: float | None = None, h1: float = 1.0) -> tuple[list[AporteCara], float]:
    """Rayo marginal paraxial que entra a la altura h1 y el aporte de cada cara a S_I.

    y_objeto es la posicion de un objeto sobre el eje; None significa objeto en el
    infinito (el rayo llega paralelo al eje). Devuelve (aportes, u'_k).
    """
    caras = ((lente.abajo, 1.0, lente.n), (lente.arriba, lente.n, 1.0))
    u = 0.0 if y_objeto is None else h1 / (lente.abajo.y_vertice - y_objeto)
    h = h1
    lista = []
    for j, (sup, n1, n2) in enumerate(caras):
        if sup.k is None:
            raise ValueError("la suma de Seidel necesita caras conicas (con constante k)")
        if j == 1:
            h = h + lente.espesor * u
        c = 0.0 if np.isinf(sup.radio_vertice) else 1.0 / sup.radio_vertice
        A = n1 * (h * c + u)
        u_sal = (n1 * u - h * c * (n2 - n1)) / n2
        por_k = c**3 * h**4 * (n2 - n1)
        lista.append(AporteCara(sup.nombre, h, u, u_sal, A, -A**2 * h * (u_sal / n2 - u / n1),
                                por_k, sup.k * por_k))
        u = u_sal
    return lista, u


def suma_seidel(lente: Lente, y_objeto: float | None = None, h1: float = 1.0) -> float:
    """S_I para el rayo marginal que entra a la altura h1."""
    lista, _ = aportes(lente, y_objeto, h1)
    return sum(a.esferico + a.conico for a in lista)


def coeficiente_esferica(lente: Lente, y_objeto: float | None = None) -> float:
    """C3 de la teoria de tercer orden: dy(h) = C3 h^2, con h la altura en la primera cara."""
    lista, uk = aportes(lente, y_objeto, 1.0)
    return -sum(a.esferico + a.conico for a in lista) / (2.0 * uk**2)


def k_que_anula(lente: Lente, y_objeto: float | None = None) -> float:
    """Constante conica, la misma en las dos caras, que anula la aberracion esferica de
    tercer orden. S_I es lineal en k, asi que la solucion es directa."""
    lista, _ = aportes(lente, y_objeto, 1.0)
    por_k = sum(a.por_k for a in lista)
    if por_k == 0:
        raise ValueError("con caras planas la forma conica no cambia la aberracion")
    return -sum(a.esferico for a in lista) / por_k
