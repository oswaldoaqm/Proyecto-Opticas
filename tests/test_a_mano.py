"""Metodo "a mano" (cuadratica + Snell con angulos) frente al trazador vectorial.

Son dos implementaciones independientes de la misma fisica: si coinciden, el
ejemplo resuelto y la simulacion se validan mutuamente (decision 0006).
"""
import math
from decimal import Decimal, getcontext

import numpy as np
import pytest

from lentes import imagen_de_dos_rayos, lente_biconvexa, refractar, trazar
from lentes.a_mano import (
    coeficientes,
    cruce_de_dos_rayos,
    menor_raiz_positiva,
    snell_con_angulos,
    trazar_a_mano,
)

LENTE = lente_biconvexa(10.0, 10.0, 2.0, n=1.5, k1=-1.0, k2=-1.0)
RAYOS_DEL_EJEMPLO = [((0.0, -30.0), 2.0), ((0.0, -30.0), -2.0), ((-1.0, -30.0), 0.0), ((-1.0, -30.0), 4.0)]


def direccion(grados):
    a = math.radians(grados)
    return [math.sin(a), math.cos(a)]


def test_snell_con_angulos_igual_a_la_forma_vectorial():
    rng = np.random.default_rng(11)
    comparados = 0
    for _ in range(2000):
        alpha = rng.uniform(-0.5, 0.5)
        pendiente = rng.uniform(-1.2, 1.2)
        n1, n2 = (1.0, 1.5) if rng.random() < 0.5 else (1.5, 1.0)
        u = np.array([math.sin(alpha), math.cos(alpha)])
        t, total = refractar(u, [-pendiente, 1.0], n1, n2)
        try:
            *_, alpha_out = snell_con_angulos(alpha, pendiente, n1, n2)
        except ValueError:
            assert total  # los dos metodos detectan la reflexion total
            continue
        assert not total
        assert np.allclose(t, [math.sin(alpha_out), math.cos(alpha_out)], atol=1e-12)
        comparados += 1
    assert comparados > 1500


@pytest.mark.parametrize("P, grados", RAYOS_DEL_EJEMPLO)
def test_ejemplo_a_mano_coincide_con_el_trazador(P, grados):
    a_mano = trazar_a_mano(P, math.radians(grados))
    tr = trazar(LENTE, P, direccion(grados))
    assert tr.estado == "ok" and tr.caras == ["g", "f"]
    for paso, Q, d in zip(a_mano.caras, tr.puntos[1:], tr.direcciones[1:]):
        assert np.allclose(paso.Q, Q, atol=1e-10)
        assert np.allclose(paso.u_out, d, atol=1e-12)


def test_imagen_por_cramer_igual_que_la_del_paquete():
    for (P, g1), (_, g2) in (RAYOS_DEL_EJEMPLO[0:2], RAYOS_DEL_EJEMPLO[2:4]):
        punto, s, t = cruce_de_dos_rayos(trazar_a_mano(P, math.radians(g1)), trazar_a_mano(P, math.radians(g2)))
        img = imagen_de_dos_rayos(trazar(LENTE, P, direccion(g1)), trazar(LENTE, P, direccion(g2)))
        assert np.allclose(punto, img.punto, atol=1e-9)
        assert s > 0 and t > 0 and not img.virtual


def test_rayo_vertical_usa_la_solucion_lineal():
    A, B, C = coeficientes((0.5, -10.0), (0.0, 1.0), -1.0, 0.05)
    assert A == 0.0
    lam, _ = menor_raiz_positiva(A, B, C)
    assert np.isclose(lam, -1.0 + 0.05 * 0.5**2 + 10.0)


def test_formula_estable_frente_a_la_escolar():
    """Con un rayo casi paralelo al eje la formula escolar pierde cifras; la estable no."""
    getcontext().prec = 60
    u = (1e-4, math.sqrt(1.0 - 1e-8))  # rayo casi paralelo al eje
    A, B, C = coeficientes((0.0, -30.0), u, -1.0, 0.05)
    Ad, Bd, Cd = Decimal(A), Decimal(B), Decimal(C)
    exacta = (-Bd - (Bd * Bd - 4 * Ad * Cd).sqrt()) / (2 * Ad)

    def error(x):
        return abs(Decimal(x) - exacta) / exacta

    estable, _ = menor_raiz_positiva(A, B, C)
    escolar = (-B - math.sqrt(B * B - 4 * A * C)) / (2 * A)
    assert error(estable) < Decimal("1e-14")
    assert error(escolar) > Decimal("1e-11")
