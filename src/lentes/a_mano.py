"""Ejemplo resuelto "a mano": una segunda implementacion, independiente del trazador.

Para el ejemplo de la actividad 3, y para validar el trazado vectorial, aqui todo
se calcula como se haria con calculadora:

1. la interseccion con cada cara parabolica  y = y_v + a x^2  sale de una ecuacion
   cuadratica, resuelta con la formula estable (sin metodos iterativos);
2. la refraccion se calcula con la ley de Snell escrita con angulos con signo, no
   con la forma vectorial;
3. la imagen es el cruce de dos rayos emergentes, por la regla de Cramer.

Supone luz que viaja en +y (decision 0001). Los angulos se miden desde el eje +y,
positivos hacia +x: la direccion de un rayo es (sin(alpha), cos(alpha)).
"""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class PasoCara:
    """Lo que pasa en una cara, en el orden en que se calcula."""

    cara: str            # "g" (entrada) o "f" (salida)
    n1: float
    n2: float
    y_v: float           # la cara es y = y_v + a x^2
    a: float
    A: float             # coeficientes de A lam^2 + B lam + C = 0
    B: float
    C: float
    discriminante: float
    lam: float           # distancia recorrida desde el punto anterior
    Q: tuple[float, float]
    pendiente: float     # s'(x_Q) = 2 a x_Q
    phi: float           # inclinacion de la cara: arctan(s') (rad)
    alpha_in: float      # direccion del rayo que llega (rad)
    theta_i: float       # angulo de incidencia con signo: alpha_in + phi
    theta_t: float       # angulo de refraccion con signo
    alpha_out: float     # direccion del rayo que sale: theta_t - phi

    @property
    def u_in(self) -> tuple[float, float]:
        return math.sin(self.alpha_in), math.cos(self.alpha_in)

    @property
    def u_out(self) -> tuple[float, float]:
        return math.sin(self.alpha_out), math.cos(self.alpha_out)


@dataclass(frozen=True)
class RayoAMano:
    P: tuple[float, float]
    alpha0: float
    caras: tuple[PasoCara, ...]

    @property
    def salida(self) -> tuple[tuple[float, float], tuple[float, float]]:
        """Punto de salida y direccion del rayo emergente."""
        ultima = self.caras[-1]
        return ultima.Q, ultima.u_out

    @property
    def cruce_eje(self) -> float | None:
        """y donde el rayo emergente cruza el eje optico (x = 0)."""
        (x, y), (ex, ey) = self.salida
        return None if ex == 0 else y - x * ey / ex


def coeficientes(P, u, y_v: float, a: float) -> tuple[float, float, float]:
    """a (x0 + lam ux)^2 + y_v - (y0 + lam uy) = 0   ->   A lam^2 + B lam + C = 0."""
    (x0, y0), (ux, uy) = P, u
    return a * ux**2, 2 * a * x0 * ux - uy, a * x0**2 + y_v - y0


def menor_raiz_positiva(A: float, B: float, C: float) -> tuple[float | None, float]:
    """Menor raiz positiva y discriminante, con la formula estable
    q = -(B + sgn(B) sqrt(D)) / 2, raices q/A y C/q (tambien sirve si A = 0)."""
    D = B * B - 4 * A * C
    if D < 0:
        return None, D
    q = -0.5 * (B + math.copysign(math.sqrt(D), B))
    raices = ([q / A] if A != 0 else []) + ([C / q] if q != 0 else [])
    positivas = [r for r in raices if r > 1e-12]
    return (min(positivas) if positivas else None), D


def snell_con_angulos(alpha: float, pendiente: float, n1: float, n2: float):
    """Refraccion de un rayo que sube (cos(alpha) > 0) en una cara de pendiente s'.

    La normal que apunta hacia +y forma el angulo -phi con el eje, phi = arctan(s'):
        theta_i = alpha + phi,   n1 sin(theta_i) = n2 sin(theta_t),   alpha' = theta_t - phi
    Devuelve (phi, theta_i, theta_t, alpha').
    """
    phi = math.atan(pendiente)
    theta_i = alpha + phi
    seno_t = n1 / n2 * math.sin(theta_i)
    if abs(seno_t) > 1:
        raise ValueError("reflexion total interna: el metodo con angulos no la contempla")
    theta_t = math.asin(seno_t)
    return phi, theta_i, theta_t, theta_t - phi


def trazar_a_mano(P, alpha0: float, R1: float = 10.0, R2: float = 10.0,
                  espesor: float = 2.0, n: float = 1.5) -> RayoAMano:
    """Rayo por la lente biconvexa de caras parabolicas
    g(x) = -e/2 + x^2/(2 R1)  y  f(x) = e/2 - x^2/(2 R2), con indice n."""
    caras = (("g", -espesor / 2, 1 / (2 * R1), 1.0, n),
             ("f", +espesor / 2, -1 / (2 * R2), n, 1.0))
    borde = math.sqrt(espesor / (1 / (2 * R1) + 1 / (2 * R2)))
    pos, alpha, pasos = (float(P[0]), float(P[1])), float(alpha0), []
    for nombre, y_v, a, n1, n2 in caras:
        u = (math.sin(alpha), math.cos(alpha))
        A, B, C = coeficientes(pos, u, y_v, a)
        lam, D = menor_raiz_positiva(A, B, C)
        if lam is None:
            raise ValueError(f"el rayo no toca la cara {nombre}")
        Q = (pos[0] + lam * u[0], pos[1] + lam * u[1])
        if abs(Q[0]) > borde:
            raise ValueError(f"el rayo pasa fuera de la lente (cara {nombre})")
        pendiente = 2 * a * Q[0]
        phi, theta_i, theta_t, alpha_out = snell_con_angulos(alpha, pendiente, n1, n2)
        pasos.append(PasoCara(nombre, n1, n2, y_v, a, A, B, C, D, lam, Q, pendiente,
                              phi, alpha, theta_i, theta_t, alpha_out))
        pos, alpha = Q, alpha_out
    return RayoAMano(P=(float(P[0]), float(P[1])), alpha0=float(alpha0), caras=tuple(pasos))


def cruce_de_dos_rayos(r1: RayoAMano, r2: RayoAMano):
    """Imagen como cruce de dos rayos emergentes, por la regla de Cramer.

        Q1 + s e1 = Q2 + t e2,   s = [Q2 - Q1, e2] / [e1, e2],   t = [Q2 - Q1, e1] / [e1, e2]

    con [a, b] = a_x b_y - a_y b_x. Devuelve (punto, s, t), o None si son paralelos.
    s < 0 y t < 0 significa imagen virtual.
    """
    (Q1, e1), (Q2, e2) = r1.salida, r2.salida

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    d = det(e1, e2)
    if d == 0:
        return None
    w = (Q2[0] - Q1[0], Q2[1] - Q1[1])
    s, t = det(w, e2) / d, det(w, e1) / d
    return (Q1[0] + s * e1[0], Q1[1] + s * e1[1]), s, t
