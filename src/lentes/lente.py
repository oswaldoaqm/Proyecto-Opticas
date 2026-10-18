"""La lente: la region de vidrio entre la cara de abajo g(x) y la de arriba f(x)."""
from __future__ import annotations

import numpy as np
from scipy.optimize import brentq

from .superficies import Superficie, conica


class Lente:
    """Lente de indice ``n`` limitada por y = g(x) (abajo) e y = f(x) (arriba).

    Ocupa la region  g(x) <= y <= f(x),  |x| <= semiapertura.  Si no se indica la
    semiapertura se usa el borde natural, donde las dos caras se juntan.
    """

    def __init__(self, abajo: Superficie, arriba: Superficie, n: float = 1.5,
                 semiapertura: float | None = None) -> None:
        if n <= 0:
            raise ValueError("el indice n debe ser positivo")
        if arriba.y_vertice <= abajo.y_vertice:
            raise ValueError("en x = 0 la cara de arriba debe estar por encima de la de abajo")
        self.abajo = abajo
        self.arriba = arriba
        self.n = float(n)
        self.semiapertura = float(semiapertura) if semiapertura is not None else self._borde_natural()
        xs = np.linspace(-self.semiapertura, self.semiapertura, 1001)
        self.y_min = float(np.nanmin(self.abajo(xs)))
        self.y_max = float(np.nanmax(self.arriba(xs)))

    # Nombres del enunciado: y = g(x) abajo, y = f(x) arriba.
    @property
    def g(self) -> Superficie:
        return self.abajo

    @property
    def f(self) -> Superficie:
        return self.arriba

    @property
    def espesor(self) -> float:
        """Espesor sobre el eje optico (x = 0)."""
        return self.arriba.y_vertice - self.abajo.y_vertice

    def contiene(self, P) -> bool:
        """True si el punto esta estrictamente dentro del vidrio."""
        x, y = float(P[0]), float(P[1])
        if abs(x) >= self.semiapertura:
            return False
        return bool(self.abajo(x) < y < self.arriba(x))

    def _borde_natural(self) -> float:
        """Menor x > 0 donde f(x) = g(x)."""
        def h(x):
            return float(self.arriba(x) - self.abajo(x))

        x0, paso = 0.0, 1e-3 * max(self.espesor, 1e-6)
        while x0 < 1e6:
            x1 = x0 + paso
            v = h(x1)
            if np.isnan(v):
                # Se llego al limite del dominio de alguna cara: revisar con detalle el ultimo tramo.
                xs = np.linspace(x0, x1, 2001)
                vs = np.array([h(x) for x in xs])
                ok = ~np.isnan(vs)
                idx = np.nonzero(ok[:-1] & ok[1:] & (vs[:-1] > 0) & (vs[1:] <= 0))[0]
                if idx.size:
                    i = idx[0]
                    return float(brentq(h, xs[i], xs[i + 1])) if vs[i + 1] < 0 else float(xs[i + 1])
                raise ValueError("las caras no se juntan dentro de su dominio: indica la semiapertura")
            if v <= 0:
                return float(brentq(h, x0, x1)) if v < 0 else x1
            x0, paso = x1, paso * 1.25
        raise ValueError("no se encontro el borde de la lente: indica la semiapertura")

    def __repr__(self) -> str:
        return (f"Lente(n={self.n:g}, espesor={self.espesor:.4g}, semiapertura={self.semiapertura:.4g}, "
                f"g={self.abajo.nombre!r}, f={self.arriba.nombre!r})")


def lente_biconvexa(R1: float, R2: float, espesor: float, n: float = 1.5,
                    k1: float = 0.0, k2: float = 0.0, semiapertura: float | None = None) -> Lente:
    """Lente biconvexa centrada en el origen (vertices en y = -espesor/2 y +espesor/2).

    R1, R2 > 0 son los radios de vertice, en magnitud, de la cara de abajo g y de la
    de arriba f. k1, k2 son sus constantes conicas (0 esfera, -1 parabola).
    """
    if R1 <= 0 or R2 <= 0 or espesor <= 0:
        raise ValueError("R1, R2 y el espesor deben ser positivos")
    g = conica(-espesor / 2, +R1, k1, nombre="g")
    f = conica(+espesor / 2, -R2, k2, nombre="f")
    return Lente(abajo=g, arriba=f, n=n, semiapertura=semiapertura)
