"""Interseccion exacta con caras conicas frente a la numerica (actividad 1)."""
import numpy as np
import pytest

from lentes import (
    conica,
    desde_expresion,
    interseccion,
    interseccion_exacta,
    lente_biconvexa,
    raices_cuadratica,
    rayo_hacia,
    trazar,
)


def test_raices_cuadratica_casos_basicos():
    assert np.allclose(raices_cuadratica(1.0, -3.0, 2.0), [1.0, 2.0])
    assert raices_cuadratica(1.0, 0.0, 1.0) == []
    assert np.allclose(raices_cuadratica(0.0, 2.0, -4.0), [2.0])  # caso lineal
    assert np.allclose(raices_cuadratica(1.0, 0.0, -4.0), [-2.0, 2.0])


@pytest.mark.parametrize("k", [-2.5, -1.0, -0.5, 0.0, 0.6])
def test_la_exacta_coincide_con_la_numerica_en_las_dos_caras(k):
    lente = lente_biconvexa(10.0, 12.0, 2.0, n=1.5, k1=k, k2=k)
    rng = np.random.default_rng(7)
    probados = 0
    for _ in range(300):
        P = np.array([rng.uniform(-3, 3), rng.uniform(-40, -5)])
        u = rayo_hacia(lente, P, rng.uniform(-0.95, 0.95) * lente.semiapertura)
        # cara de entrada g, desde el aire
        lam_n = interseccion(P, u, lente.abajo, lente.semiapertura, 1e-9, 200.0, muestras=20001)
        lam_e = interseccion_exacta(P, u, lente.abajo, lente.semiapertura)
        assert lam_n is not None and lam_e is not None
        assert np.isclose(lam_n, lam_e, rtol=0, atol=1e-9)
        # cara de salida f, desde dentro del vidrio con el rayo ya refractado
        tr = trazar(lente, P, u)
        if tr.estado != "ok":
            continue
        Q1, d1 = tr.puntos[1], tr.direcciones[1]
        lam_e2 = interseccion_exacta(Q1, d1, lente.arriba, lente.semiapertura)
        assert np.allclose(Q1 + lam_e2 * d1, tr.puntos[2], atol=1e-9)
        probados += 1
    assert probados > 250


def test_cara_plana():
    plana = conica(0.5, np.inf)  # radio infinito: la recta y = 0.5
    assert np.isclose(interseccion_exacta([0.2, -3.0], [0.0, 1.0], plana, 3.0), 3.5)


def test_sin_constante_conica_no_hay_formula_cerrada():
    with pytest.raises(ValueError):
        interseccion_exacta([0.0, -5.0], [0.0, 1.0], desde_expresion("x**4"), 3.0)
