"""Trazado vectorial de rayos: interseccion con las caras, ley de Snell vectorial
y recorrido completo de un rayo por la lente.

Un rayo es la recta L(lambda) = P0 + lambda * u, con u unitario y lambda >= 0.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.optimize import brentq

from .lente import Lente
from .superficies import Superficie

EPS = 1e-9


def unitario(v) -> np.ndarray:
    """Normaliza un vector 2D."""
    v = np.asarray(v, dtype=float)
    norma = float(np.hypot(v[0], v[1]))
    if norma == 0.0:
        raise ValueError("vector nulo")
    return v / norma


# ---------------------------------------------------------------- refraccion

@dataclass(frozen=True)
class DetalleRefraccion:
    """Lo que pasa en una cara: normal usada, angulos y nueva direccion."""

    normal: np.ndarray          # normal orientada hacia el medio de incidencia
    theta_i: float              # angulo de incidencia (rad)
    theta_t: float | None       # angulo de refraccion (rad); None si hay reflexion total
    direccion: np.ndarray       # direccion del rayo despues de la cara
    reflexion_total: bool


def refractar(u, normal, n1: float, n2: float) -> tuple[np.ndarray, bool]:
    """Ley de Snell en forma vectorial (decision 0002).

    Primero orienta la normal hacia el medio de incidencia (n . u < 0). Luego

        cos(ti) = -n . u,   eta = n1 / n2,   cos(tt) = sqrt(1 - eta^2 (1 - cos(ti)^2))
        u_t = eta u + (eta cos(ti) - cos(tt)) n

    Devuelve (direccion, False). Si la raiz es negativa hay reflexion total
    interna y devuelve (u + 2 cos(ti) n, True).
    """
    u = unitario(u)
    nh = unitario(normal)
    if nh @ u > 0:
        nh = -nh
    cos_i = -float(nh @ u)
    eta = n1 / n2
    k = 1.0 - eta**2 * (1.0 - cos_i**2)
    if k < 0:
        return unitario(u + 2.0 * cos_i * nh), True
    return unitario(eta * u + (eta * cos_i - np.sqrt(k)) * nh), False


def detalle_refraccion(u, normal, n1: float, n2: float) -> DetalleRefraccion:
    """Como ``refractar`` pero devuelve tambien la normal orientada y los angulos."""
    u = unitario(u)
    nh = unitario(normal)
    if nh @ u > 0:
        nh = -nh
    direccion, total = refractar(u, nh, n1, n2)
    theta_i = float(np.arccos(np.clip(-(nh @ u), -1.0, 1.0)))
    theta_t = None if total else float(np.arccos(np.clip(-(nh @ direccion), -1.0, 1.0)))
    return DetalleRefraccion(normal=nh, theta_i=theta_i, theta_t=theta_t,
                             direccion=direccion, reflexion_total=total)


# -------------------------------------------------------------- interseccion

def _rango_en_caja(P, u, xmin, xmax, ymin, ymax) -> tuple[float, float] | None:
    """Intervalo de lambda en el que P + lambda u esta dentro de la caja (metodo de losas)."""
    lo, hi = -np.inf, np.inf
    for p, d, a, b in ((P[0], u[0], xmin, xmax), (P[1], u[1], ymin, ymax)):
        if abs(d) < 1e-15:
            if p < a or p > b:
                return None
        else:
            t1, t2 = (a - p) / d, (b - p) / d
            lo, hi = max(lo, min(t1, t2)), min(hi, max(t1, t2))
    lo = max(lo, EPS)
    if hi <= lo:
        return None
    return lo, hi


def interseccion(P, u, sup: Superficie, semiapertura: float, lam_min: float, lam_max: float,
                 muestras: int = 2001) -> float | None:
    """Menor lambda en [lam_min, lam_max] con  P_y + lambda u_y = s(P_x + lambda u_x)  y |x| <= semiapertura.

    Se muestrea h(lambda) = y(lambda) - s(x(lambda)) para encontrar el primer cambio de
    signo y se refina con el metodo de Brent. Funciona para cualquier cara suave.
    """
    P = np.asarray(P, dtype=float)
    u = np.asarray(u, dtype=float)
    lam = np.linspace(lam_min, lam_max, muestras)
    x = P[0] + lam * u[0]
    with np.errstate(invalid="ignore"):
        h = P[1] + lam * u[1] - sup(x)
    h = np.where(np.abs(x) <= semiapertura, h, np.nan)
    valido = np.isfinite(h)
    candidatos = np.nonzero(valido[:-1] & valido[1:] & (h[:-1] * h[1:] <= 0))[0]
    for i in candidatos:
        if h[i] == 0.0:
            if i == 0:
                continue  # es el punto de partida, no un impacto nuevo
            return float(lam[i])
        if h[i + 1] == 0.0:
            return float(lam[i + 1])

        def H(L):
            return P[1] + L * u[1] - float(sup(P[0] + L * u[0]))

        return float(brentq(H, lam[i], lam[i + 1], xtol=1e-14, rtol=1e-14))
    return None


def _primer_impacto(lente: Lente, P, u) -> tuple[float, Superficie] | None:
    """Primera cara que encuentra el rayo (dentro de la apertura), o None."""
    pad = 1e-9 + 1e-6 * (lente.y_max - lente.y_min)
    rango = _rango_en_caja(P, u, -lente.semiapertura - pad, lente.semiapertura + pad,
                           lente.y_min - pad, lente.y_max + pad)
    if rango is None:
        return None
    lo, hi = rango
    mejor = None
    for sup in (lente.abajo, lente.arriba):
        lam = interseccion(P, u, sup, lente.semiapertura, lo, hi)
        if lam is not None and (mejor is None or lam < mejor[0]):
            mejor = (lam, sup)
    return mejor


# ------------------------------------------------------------ trazado completo

@dataclass
class Trayectoria:
    """Resultado de trazar un rayo.

    puntos[0] es el punto de partida y puntos[i] (i >= 1) los impactos con las caras.
    direcciones[i] es la direccion del rayo DESPUES de puntos[i]: la ultima es la emergente.
    detalles[i-1] y caras[i-1] describen lo que paso en puntos[i].

    estado: "ok" (entra y sale), "no_toca_lente", "sale_por_el_borde" o "demasiados_eventos".
    """

    puntos: list[np.ndarray] = field(default_factory=list)
    direcciones: list[np.ndarray] = field(default_factory=list)
    detalles: list[DetalleRefraccion] = field(default_factory=list)
    caras: list[str] = field(default_factory=list)
    estado: str = "ok"

    @property
    def salida(self) -> tuple[np.ndarray, np.ndarray]:
        """Ultimo punto y ultima direccion (el rayo emergente si estado == "ok")."""
        return self.puntos[-1], self.direcciones[-1]

    @property
    def eventos(self) -> list[str]:
        return ["reflexion_total" if d.reflexion_total else "refraccion" for d in self.detalles]


def trazar(lente: Lente, P, u, n_medio: float = 1.0, max_eventos: int = 12) -> Trayectoria:
    """Sigue un rayo que sale de P con direccion u a traves de la lente.

    En cada impacto se aplica Snell vectorial (o reflexion total interna) y se
    continua hasta que el rayo ya no toca ninguna cara.
    """
    P = np.asarray(P, dtype=float)
    d = unitario(u)
    tr = Trayectoria(puntos=[P], direcciones=[d])
    dentro = lente.contiene(P)
    pos = P
    for _ in range(max_eventos):
        impacto = _primer_impacto(lente, pos, d)
        if impacto is None:
            if dentro:
                tr.estado = "sale_por_el_borde"
            elif not tr.detalles:
                tr.estado = "no_toca_lente"
            else:
                tr.estado = "ok"
            return tr
        lam, sup = impacto
        Q = pos + lam * d
        n1, n2 = (lente.n, n_medio) if dentro else (n_medio, lente.n)
        det = detalle_refraccion(d, sup.normal(Q[0]), n1, n2)
        tr.puntos.append(Q)
        tr.direcciones.append(det.direccion)
        tr.detalles.append(det)
        tr.caras.append(sup.nombre)
        if not det.reflexion_total:
            dentro = not dentro
        pos, d = Q, det.direccion
    tr.estado = "demasiados_eventos"
    return tr


def rayo_hacia(lente: Lente, P, h: float, cara: str = "abajo") -> np.ndarray:
    """Direccion unitaria desde P hacia el punto de la cara (g por defecto) con x = h."""
    sup = lente.abajo if cara == "abajo" else lente.arriba
    return unitario(np.array([h, float(sup(h))]) - np.asarray(P, dtype=float))


# ----------------------------------------------------------------- la imagen

def cruce_con_eje(Q, e) -> float | None:
    """y donde la recta Q + s e corta el eje optico (x = 0); None si es paralela al eje."""
    if abs(e[0]) < 1e-14:
        return None
    s = -Q[0] / e[0]
    return float(Q[1] + s * e[1])


def interseccion_rectas(P1, u1, P2, u2) -> tuple[np.ndarray, float, float] | None:
    """Punto donde se cortan P1 + s u1 y P2 + t u2 (sistema lineal 2x2).

    Devuelve (punto, s, t), o None si son paralelas. Si s < 0 y t < 0 el cruce
    esta detras de los puntos de salida: es una imagen virtual.
    """
    P1, u1, P2, u2 = (np.asarray(v, dtype=float) for v in (P1, u1, P2, u2))
    A = np.column_stack([u1, -u2])
    det = A[0, 0] * A[1, 1] - A[0, 1] * A[1, 0]
    if abs(det) < 1e-14:
        return None
    s, t = np.linalg.solve(A, P2 - P1)
    return P1 + s * u1, float(s), float(t)


@dataclass(frozen=True)
class Imagen:
    punto: np.ndarray
    virtual: bool


def imagen_de_dos_rayos(t1: Trayectoria, t2: Trayectoria) -> Imagen | None:
    """Imagen como cruce de dos rayos emergentes (o de sus prolongaciones hacia atras)."""
    (Q1, e1), (Q2, e2) = t1.salida, t2.salida
    res = interseccion_rectas(Q1, e1, Q2, e2)
    if res is None:
        return None
    punto, s, t = res
    return Imagen(punto=punto, virtual=bool(s < 0 and t < 0))
