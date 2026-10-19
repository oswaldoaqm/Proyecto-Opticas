"""Frente de onda y limite de difraccion (extra 5).

Principio de Fermat: si una lente formara una imagen perfecta, todos los rayos que
van del punto objeto al punto imagen tendrian el mismo camino optico (n por la
longitud recorrida). En una lente real no es asi. La diferencia de camino optico de
cada rayo, medida hasta una esfera de referencia centrada en el punto imagen, es el
error del frente de onda W. Con la convencion de los libros (Welford, 1986),

    W(h) = OPL(rayo axial) - OPL(rayo que entra a la altura h),

y en tercer orden W = (S_I / 8) (h / h_1)^4, con S_I la suma de Seidel de
lentes.seidel para el rayo marginal de altura h_1 (las pruebas lo comparan).

Con W se decide si la lente esta limitada por la difraccion (criterio de Marechal:
W_rms <= lambda / 14, que equivale a un Strehl de 0.8) y se calcula la imagen de un
punto (PSF) con la integral de difraccion de una pupila circular uniforme.

Unidades: las longitudes del proyecto se leen como milimetros y la luz es verde,
lambda = 550 nm = 5.5e-4 mm. El objeto esta sobre el eje (x = 0) o en el infinito
(y_objeto None), como en lentes.aberraciones. Por la simetria de revolucion, el
abanico de rayos de un plano da el frente de onda en toda la pupila circular.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.interpolate import CubicSpline
from scipy.optimize import brentq, minimize_scalar
from scipy.special import j0

from .aberraciones import rayo_a_altura, y_paraxial
from .lente import Lente
from .trazado import Trayectoria, trazar

LAMBDA_VERDE = 5.5e-4   # mm (550 nm)
MARECHAL = 1.0 / 14.0   # W_rms maximo, en longitudes de onda, para estar limitado por difraccion
AIRY = 0.6098           # primer cero de [2 J1(v) / v]^2: v = 3.8317 = 2 pi * 0.6098


def camino_optico(tr: Trayectoria, n_lente: float, n_medio: float = 1.0) -> float:
    """Camino optico del rayo desde su punto de partida hasta su ultimo impacto: suma de n * longitud."""
    total, dentro = 0.0, False
    for i in range(len(tr.puntos) - 1):
        tramo = np.asarray(tr.puntos[i + 1], dtype=float) - np.asarray(tr.puntos[i], dtype=float)
        total += (n_lente if dentro else n_medio) * float(np.hypot(*tramo))
        if not tr.detalles[i].reflexion_total:
            dentro = not dentro
    return total


def _hasta_esfera(Q: np.ndarray, e: np.ndarray, y_ref: float, y_vertice: float) -> np.ndarray:
    """Distancia con signo, a lo largo de cada rayo emergente (Q, e), hasta la esfera centrada
    en (0, y_ref) que pasa por el vertice de salida (0, y_vertice). Se toma el corte mas
    cercano a Q, con la forma estable de la cuadratica (el otro corte es c / q)."""
    d = Q - np.array([0.0, y_ref])
    b = np.einsum("ij,ij->i", e, d)
    c = np.einsum("ij,ij->i", d, d) - (y_ref - y_vertice) ** 2
    raiz = np.sqrt(np.maximum(b * b - c, 0.0))
    q = -b - np.where(b >= 0.0, 1.0, -1.0) * raiz
    return c / q


@dataclass(frozen=True)
class Haz:
    """Rayos de un objeto sobre el eje que entran a la lente a alturas 0 <= h <= h_tope,
    con interpolacion suave en h: asi la pupila se puede muestrear tan fino como haga falta."""

    lente: Lente
    y_objeto: float | None
    h_tope: float
    camino: CubicSpline      # camino optico hasta la salida de la lente
    salida: CubicSpline      # punto de salida (x, y)
    direccion: CubicSpline   # direccion emergente (ex, ey)

    @property
    def n_imagen(self) -> float:
        return 1.0

    def frente_de_onda(self, h, y_ref: float) -> np.ndarray:
        """W(h) en mm respecto a la esfera centrada en (0, y_ref) que pasa por el vertice de salida."""
        h = np.atleast_1d(np.asarray(h, dtype=float))
        y_v = self.lente.arriba.y_vertice
        opl = self.camino(h) + self.n_imagen * _hasta_esfera(self.salida(h), self.direccion(h), y_ref, y_v)
        opl_axial = self.camino(0.0) + self.n_imagen * _hasta_esfera(
            self.salida(np.array([0.0])), self.direccion(np.array([0.0])), y_ref, y_v)[0]
        return opl_axial - opl

    def cruce_con_eje(self, h: float) -> float:
        """y donde el rayo que entra a la altura h cruza el eje optico."""
        (qx, qy), (ex, ey) = self.salida(h), self.direccion(h)
        return float(qy - qx * ey / ex)

    def seno_salida(self, h) -> np.ndarray:
        """Seno del angulo del rayo emergente con el eje optico."""
        return np.abs(self.direccion(np.asarray(h, dtype=float))[..., 0])


def haz(lente: Lente, y_objeto: float | None, h_tope: float | None = None, n: int = 601) -> Haz:
    """Traza n rayos entre h = 0 y h_tope (por defecto, 95 % de la semiapertura)."""
    if h_tope is None:
        h_tope = 0.95 * lente.semiapertura
    hs = np.linspace(0.0, h_tope, n)
    caminos, salidas, direcciones = [], [], []
    for h in hs:
        tr = trazar(lente, *rayo_a_altura(lente, y_objeto, h))
        if tr.estado != "ok" or len(tr.detalles) != 2 or any(d.reflexion_total for d in tr.detalles):
            raise ValueError(f"el rayo que entra a la altura {h:.4g} no atraviesa la lente")
        Q, e = tr.salida
        caminos.append(camino_optico(tr, lente.n))
        salidas.append(Q)
        direcciones.append(e)
    return Haz(lente, y_objeto, float(h_tope), CubicSpline(hs, caminos),
               CubicSpline(hs, np.array(salidas)), CubicSpline(hs, np.array(direcciones)))


def pupila(m: int) -> tuple[np.ndarray, np.ndarray]:
    """rho = h / h_max en m anillos de igual ancho y el area relativa de cada uno (suman 1)."""
    rho = (np.arange(m) + 0.5) / m
    return rho, rho / rho.sum()


def rms(W: np.ndarray, pesos: np.ndarray) -> float:
    """Desviacion RMS de W en la pupila (sin el termino constante, que no cambia la imagen)."""
    media = float(np.sum(pesos * W))
    return float(np.sqrt(np.sum(pesos * (W - media) ** 2)))


@dataclass(frozen=True)
class FocoOnda:
    h_max: float
    y_paraxial: float
    y_marginal: float
    y_ref: float          # plano donde el frente de onda tiene el menor W_rms
    rms: float            # ese W_rms, en mm
    rms_paraxial: float   # W_rms con la referencia en la imagen paraxial

    def fraccion(self, y: float) -> float:
        """Posicion de un plano entre el foco paraxial (0) y el marginal (1)."""
        return (y - self.y_paraxial) / (self.y_marginal - self.y_paraxial)


def mejor_foco_onda(hz: Haz, h_max: float, m: int = 400) -> FocoOnda:
    """Plano de menor W_rms para una pupila de radio h_max (el que maximiza el Strehl
    cuando la aberracion es chica)."""
    rho, pesos = pupila(m)
    h = rho * h_max

    def sigma(y_ref):
        return rms(hz.frente_de_onda(h, y_ref), pesos)

    y_par = y_paraxial(hz.lente, hz.y_objeto)
    y_marg = hz.cruce_con_eje(h_max)
    lo, hi = min(y_par, y_marg), max(y_par, y_marg)
    margen = 0.1 * (hi - lo) + 1e-12
    r = minimize_scalar(sigma, bounds=(lo - margen, hi + margen), method="bounded",
                        options={"xatol": 1e-12, "maxiter": 500})
    return FocoOnda(h_max, y_par, y_marg, float(r.x), float(r.fun), sigma(y_par))


def _muestras(hz: Haz, h_max: float, y_ref: float, lam: float, m_min: int = 400):
    """Pupila muestreada tan fino que la fase cambie menos de 2 pi / 20 entre anillos vecinos."""
    rho, _ = pupila(m_min)
    W = hz.frente_de_onda(rho * h_max, y_ref)
    pendiente = np.max(np.abs(np.diff(W))) * m_min  # dW/drho
    m = int(min(max(m_min, np.ceil(20 * pendiente / lam)), 200_000))
    rho, pesos = pupila(m)
    return rho, pesos, hz.frente_de_onda(rho * h_max, y_ref)


def strehl(hz: Haz, h_max: float, y_ref: float, lam: float = LAMBDA_VERDE) -> float:
    """Pico de la imagen de un punto dividido por el de una lente perfecta de la misma
    apertura: |suma de exp(i k W) en la pupila|^2 (integral de difraccion exacta, escalar)."""
    _, pesos, W = _muestras(hz, h_max, y_ref, lam)
    return float(np.abs(np.sum(pesos * np.exp(2j * np.pi * W / lam))) ** 2)


def strehl_marechal(sigma_ondas: float) -> float:
    """Aproximacion de Marechal: S = exp(-(2 pi W_rms / lambda)^2), buena para W_rms < lambda / 10."""
    return float(np.exp(-(2 * np.pi * sigma_ondas) ** 2))


def intensidad(pesos: np.ndarray, W: np.ndarray, senos: np.ndarray, r, lam: float = LAMBDA_VERDE) -> np.ndarray:
    """Integral de difraccion de una pupila circular uniforme, sumando anillos:

        I(r) = | sum_anillos  peso * exp(i k W) * J0(k r sen(theta)) |^2

    con theta el angulo de cada anillo de rayos con el eje y k = 2 pi / lambda. Con
    W = 0 da el patron de Airy, normalizado a 1 en el centro."""
    k = 2 * np.pi / lam
    r = np.atleast_1d(np.asarray(r, dtype=float))
    campo = (pesos * np.exp(1j * k * W)) @ j0(k * np.outer(senos, r))
    return np.abs(campo) ** 2


def psf(hz: Haz, h_max: float, y_ref: float, r, lam: float = LAMBDA_VERDE) -> np.ndarray:
    """Imagen de un punto: intensidad a la distancia r del eje en el plano y_ref, normalizada
    al pico de una lente perfecta de la misma apertura (en r = 0 vale el Strehl)."""
    rho, pesos, W = _muestras(hz, h_max, y_ref, lam)
    return intensidad(pesos, W, hz.seno_salida(rho * h_max), r, lam)


def apertura_numerica(hz: Haz, h_max: float) -> float:
    """n' sen(theta) del rayo marginal emergente."""
    return float(hz.n_imagen * hz.seno_salida(h_max))


def radio_airy(hz: Haz, h_max: float, lam: float = LAMBDA_VERDE) -> float:
    """Radio del primer anillo oscuro de una lente perfecta: 0.61 lambda / NA'."""
    return AIRY * lam / apertura_numerica(hz, h_max)


def radio_rms_geometrico(hz: Haz, h_max: float, m: int = 400) -> float:
    """Menor radio RMS de la mancha geometrica (en el mejor plano), con los mismos rayos."""
    rho, pesos = pupila(m)
    Q, e = hz.salida(rho * h_max), hz.direccion(rho * h_max)

    def radio(y):
        x = Q[:, 0] + (y - Q[:, 1]) * e[:, 0] / e[:, 1]
        return float(np.sqrt(np.sum(pesos * x**2)))

    y_par = y_paraxial(hz.lente, hz.y_objeto)
    y_marg = hz.cruce_con_eje(h_max)
    lo, hi = min(y_par, y_marg), max(y_par, y_marg)
    margen = 0.1 * (hi - lo) + 1e-12
    r = minimize_scalar(radio, bounds=(lo - margen, hi + margen), method="bounded",
                        options={"xatol": 1e-12, "maxiter": 500})
    return float(r.fun)


def apertura_limite(hz: Haz, lam: float = LAMBDA_VERDE, criterio: float = MARECHAL) -> float:
    """Mayor h_max con W_rms <= criterio * lambda en el mejor foco (Marechal: lambda / 14).
    Si toda la lente cumple, devuelve h_tope."""
    def exceso(h):
        return mejor_foco_onda(hz, h).rms / lam - criterio

    h_lo = 1e-3 * hz.h_tope
    if exceso(hz.h_tope) <= 0:
        return hz.h_tope
    return float(brentq(exceso, h_lo, hz.h_tope, xtol=1e-9))


def apertura_cruce(hz: Haz, lam: float = LAMBDA_VERDE) -> float:
    """h_max donde la mancha geometrica (radio RMS) iguala al radio de Airy: por debajo
    manda la difraccion y por encima la aberracion."""
    def diferencia(h):
        return np.log(radio_rms_geometrico(hz, h) / radio_airy(hz, h, lam))

    return float(brentq(diferencia, 1e-2 * hz.h_tope, hz.h_tope, xtol=1e-9))
