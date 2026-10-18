"""Las caras: formas conicas, derivadas, vectores tangente y normal (actividad 2)."""
import numpy as np
import pytest

from lentes import conica, desde_expresion, esferica, parabolica

X = np.linspace(-4.0, 4.0, 41)


def test_conica_con_k_0_es_una_circunferencia():
    R, yv = 10.0, -1.0
    assert np.allclose(esferica(yv, R)(X), yv + R - np.sqrt(R**2 - X**2))


def test_conica_con_k_menos_1_es_una_parabola():
    R, yv = -10.0, 1.0
    assert np.allclose(parabolica(yv, R)(X), yv + X**2 / (2 * R))


@pytest.mark.parametrize("k", [-2.0, -1.0, -0.5, 0.0, 0.7])
def test_derivada_coincide_con_diferencias_finitas(k):
    s = conica(0.3, 12.0, k)
    h = 1e-6
    numerica = (s(X + h) - s(X - h)) / (2 * h)
    assert np.allclose(s.ds(X), numerica, rtol=1e-6, atol=1e-8)


def test_radio_de_vertice_es_el_inverso_de_la_curvatura():
    s = conica(0.0, 8.0, k=-0.4)
    h = 1e-4
    curvatura = (s(h) - 2 * s(0.0) + s(-h)) / h**2
    assert np.isclose(1 / curvatura, s.radio_vertice, rtol=1e-6)


def test_tangente_y_normal_son_unitarias_y_perpendiculares():
    s = esferica(0.0, 5.0)
    for x in (-3.0, -0.5, 0.0, 1.2, 4.0):
        t, n = s.tangente(x), s.normal(x)
        assert np.isclose(np.linalg.norm(t), 1.0)
        assert np.isclose(np.linalg.norm(n), 1.0)
        assert np.isclose(t @ n, 0.0, atol=1e-12)


def test_cara_desde_una_formula_igual_a_la_parabola():
    s = desde_expresion("1 - x**2/20")
    p = parabolica(1.0, -10.0)
    assert np.allclose(s(X), p(X))
    assert np.allclose(s.ds(X), p.ds(X))
    assert np.isclose(s.radio_vertice, -10.0)
    assert np.isclose(s.y_vertice, 1.0)


def test_formula_con_otras_variables_se_rechaza():
    with pytest.raises(ValueError):
        desde_expresion("a*x**2")
