"""Caras de la lente descritas como curvas y = s(x).

Convencion (ver docs/decisiones/0001): el eje optico es el eje y y la luz viaja
en +y. Una cara con radio de vertice R > 0 tiene su centro de curvatura por
encima del vertice (es concava hacia arriba), como la cara g(x) de abajo; con
R < 0 es concava hacia abajo, como la cara f(x) de arriba. Con esta convencion
R = 1/s''(0) ya tiene el signo que usa la optica paraxial.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

Funcion = Callable[[float | np.ndarray], float | np.ndarray]


@dataclass(frozen=True)
class Superficie:
    """Una cara y = s(x) junto con su derivada s'(x).

    Atributos
    ---------
    s, ds : funciones vectorizadas (aceptan arrays de numpy).
    y_vertice : s(0).
    radio_vertice : 1 / s''(0) con signo; ``np.inf`` si la cara es plana en el vertice.
    nombre : etiqueta para graficos y mensajes.
    k : constante conica si la cara es una conica (permite la interseccion exacta,
        ``trazado.interseccion_exacta``); None si es una formula arbitraria.
    """

    s: Funcion
    ds: Funcion
    y_vertice: float
    radio_vertice: float
    nombre: str = ""
    k: float | None = None

    def __call__(self, x):
        return self.s(x)

    def tangente(self, x: float) -> np.ndarray:
        """Vector unitario tangente: (1, s'(x)) / sqrt(1 + s'(x)^2)."""
        d = float(self.ds(x))
        return np.array([1.0, d]) / np.hypot(1.0, d)

    def normal(self, x: float) -> np.ndarray:
        """Vector unitario normal: (-s'(x), 1) / sqrt(1 + s'(x)^2).

        Siempre apunta hacia +y. El sentido correcto en cada refraccion lo
        decide ``trazado.refractar`` (decision 0002).
        """
        d = float(self.ds(x))
        return np.array([-d, 1.0]) / np.hypot(1.0, d)


def conica(y_vertice: float, radio: float, k: float = 0.0, nombre: str = "") -> Superficie:
    """Perfil conico con vertice en (0, y_vertice).

        s(x) = y_v + c x^2 / (1 + sqrt(1 - (1 + k) c^2 x^2)),   c = 1 / radio

    k = 0: circunferencia (lente esferica); k = -1: parabola;
    -1 < k < 0 o k > 0: elipse; k < -1: hiperbola.
    Fuera de su dominio (raiz negativa) devuelve NaN.
    """
    if radio == 0:
        raise ValueError("el radio no puede ser 0 (usa np.inf para una cara plana)")
    c = 1.0 / radio

    def s(x):
        x = np.asarray(x, dtype=float)
        with np.errstate(invalid="ignore"):
            return y_vertice + c * x**2 / (1.0 + np.sqrt(1.0 - (1.0 + k) * c**2 * x**2))

    def ds(x):
        x = np.asarray(x, dtype=float)
        with np.errstate(invalid="ignore", divide="ignore"):
            return c * x / np.sqrt(1.0 - (1.0 + k) * c**2 * x**2)

    return Superficie(s=s, ds=ds, y_vertice=float(y_vertice), radio_vertice=float(radio), nombre=nombre,
                      k=float(k))


def esferica(y_vertice: float, radio: float, nombre: str = "") -> Superficie:
    """Arco de circunferencia (k = 0)."""
    return conica(y_vertice, radio, k=0.0, nombre=nombre)


def parabolica(y_vertice: float, radio: float, nombre: str = "") -> Superficie:
    """Parabola y = y_v + x^2 / (2 R) (k = -1)."""
    return conica(y_vertice, radio, k=-1.0, nombre=nombre)


def desde_expresion(expresion: str, nombre: str = "") -> Superficie:
    """Cara arbitraria a partir de una formula en x, por ejemplo ``"1 - x**2/20"``.

    La derivada se calcula de forma simbolica (sympy), asi que la normal es exacta.
    """
    import sympy as sp

    x = sp.Symbol("x", real=True)
    expr = sp.sympify(expresion, locals={"x": x})
    sobrantes = expr.free_symbols - {x}
    if sobrantes:
        raise ValueError(f"la expresion solo puede depender de x: {expresion!r}")
    d1 = sp.diff(expr, x)
    d2 = sp.diff(expr, x, 2)
    s_num = sp.lambdify(x, expr, "numpy")
    d_num = sp.lambdify(x, d1, "numpy")

    def s(xx):
        xx = np.asarray(xx, dtype=float)
        return np.zeros_like(xx) + s_num(xx)

    def ds(xx):
        xx = np.asarray(xx, dtype=float)
        return np.zeros_like(xx) + d_num(xx)

    curvatura = float(d2.subs(x, 0))
    radio = np.inf if curvatura == 0 else 1.0 / curvatura
    return Superficie(s=s, ds=ds, y_vertice=float(expr.subs(x, 0)), radio_vertice=radio,
                      nombre=nombre or expresion)
