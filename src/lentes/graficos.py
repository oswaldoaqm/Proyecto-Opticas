"""Dibujos reutilizables: la lente y las trayectorias de los rayos.

Con ``girar=True`` (por defecto) se dibuja (y, x): la luz va de izquierda a
derecha como en los libros, aunque el eje optico del modelo sea el eje y
(decision 0001).
"""
from __future__ import annotations

import numpy as np

from .estilo import TINTA_2, VIDRIO
from .lente import Lente
from .trazado import Trayectoria


def _xy(puntos_x, puntos_y, girar: bool):
    return (puntos_y, puntos_x) if girar else (puntos_x, puntos_y)


def dibujar_lente(ax, lente: Lente, girar: bool = True, puntos: int = 400,
                  relleno: str = VIDRIO, borde: str = TINTA_2) -> None:
    """Rellena el vidrio y traza el contorno de las dos caras."""
    x = np.linspace(-lente.semiapertura, lente.semiapertura, puntos)
    X = np.concatenate([x, x[::-1]])
    Y = np.concatenate([lente.abajo(x), lente.arriba(x[::-1])])
    a, b = _xy(X, Y, girar)
    ax.fill(a, b, color=relleno, zorder=1)
    ax.plot(a, b, color=borde, lw=1.0, zorder=3)


def dibujar_trayectoria(ax, tr: Trayectoria, y_final: float | None = None, largo_final: float = 10.0,
                        color: str = "#2a78d6", lw: float = 1.0, girar: bool = True, **kwargs) -> None:
    """Dibuja el rayo incidente, los tramos dentro del vidrio y el emergente.

    El tramo emergente llega hasta la altura ``y_final`` sobre el eje (si se da y
    el rayo va hacia alla) o, si no, tiene longitud ``largo_final``.
    """
    pts = list(tr.puntos)
    Q, e = tr.salida
    lam = largo_final
    if y_final is not None and abs(e[1]) > 1e-12:
        lam_y = (y_final - Q[1]) / e[1]
        if lam_y > 0:
            lam = lam_y
    pts.append(Q + lam * e)
    P = np.array(pts)
    a, b = _xy(P[:, 0], P[:, 1], girar)
    ax.plot(a, b, color=color, lw=lw, zorder=2, **kwargs)
