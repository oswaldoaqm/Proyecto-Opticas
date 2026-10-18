"""Ley de Snell vectorial y orientacion de la normal (actividad 2, decision 0002)."""
import numpy as np
import pytest

from lentes import detalle_refraccion, refractar

NORMAL_PLANA = np.array([0.0, 1.0])  # interfaz plana y = 0


def test_incidencia_normal_no_desvia():
    t, total = refractar([0.0, 1.0], NORMAL_PLANA, 1.0, 1.5)
    assert not total
    assert np.allclose(t, [0.0, 1.0])


@pytest.mark.parametrize("n1, n2", [(1.0, 1.5), (1.5, 1.0), (1.0, 1.33), (1.33, 1.0)])
@pytest.mark.parametrize("grados", [5, 20, 35, 41, 42, 60, 85])
def test_reproduce_la_ley_de_snell_escalar(n1, n2, grados):
    th = np.radians(grados)
    u = np.array([np.sin(th), np.cos(th)])  # avanza hacia +y y cruza la interfaz y = 0
    t, total = refractar(u, NORMAL_PLANA, n1, n2)
    if n1 * np.sin(th) / n2 > 1:
        assert total
        assert np.allclose(t, [np.sin(th), -np.cos(th)])  # reflexion especular
    else:
        assert not total
        assert np.isclose(n1 * np.sin(th), n2 * t[0])  # n1 sen(ti) = n2 sen(tt)
        assert t[1] > 0  # el rayo sigue hacia adelante
        assert np.isclose(np.hypot(*t), 1.0)


def test_el_sentido_con_que_llega_la_normal_no_importa():
    u = [0.3, 0.95]
    a, _ = refractar(u, [0.1, 1.0], 1.0, 1.5)
    b, _ = refractar(u, [-0.1, -1.0], 1.0, 1.5)
    assert np.allclose(a, b)


def test_conserva_la_componente_tangencial():
    rng = np.random.default_rng(2026)
    for _ in range(500):
        ang = rng.uniform(-np.pi, np.pi)
        normal = np.array([-np.sin(ang), np.cos(ang)])
        tangente = np.array([np.cos(ang), np.sin(ang)])
        phi = rng.uniform(-np.pi, np.pi)
        u = np.array([np.cos(phi), np.sin(phi)])
        n1, n2 = rng.choice([1.0, 1.33, 1.5, 1.7], size=2)
        t, total = refractar(u, normal, n1, n2)
        if total:
            assert np.isclose(u @ tangente, t @ tangente)       # la reflexion conserva la tangencial
            assert np.sign(t @ normal) == -np.sign(u @ normal)  # y vuelve al medio de origen
        else:
            assert np.isclose(n1 * (u @ tangente), n2 * (t @ tangente))
            assert np.sign(t @ normal) == np.sign(u @ normal)   # cruza la interfaz


def test_detalle_devuelve_angulos_coherentes():
    th = np.radians(30)
    u = np.array([np.sin(th), np.cos(th)])
    det = detalle_refraccion(u, NORMAL_PLANA, 1.0, 1.5)
    assert np.isclose(det.theta_i, th)
    assert np.isclose(np.sin(det.theta_i), 1.5 * np.sin(det.theta_t))
    assert det.normal @ u < 0  # la normal usada mira hacia el medio de incidencia
