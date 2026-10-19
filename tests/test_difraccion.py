"""Frente de onda (principio de Fermat) y difraccion frente a la teoria (extra 5)."""
import numpy as np
import pytest

from lentes import lente_biconvexa, trazar
from lentes.aberraciones import rayo_a_altura, y_paraxial
from lentes.difraccion import (
    AIRY,
    LAMBDA_VERDE,
    _hasta_esfera,
    apertura_cruce,
    apertura_limite,
    camino_optico,
    haz,
    intensidad,
    mejor_foco_onda,
    pupila,
    radio_airy,
    radio_rms_geometrico,
    strehl,
    strehl_marechal,
)
from lentes.seidel import suma_seidel

LAM = LAMBDA_VERDE
# (R1, R2, espesor, k, y_objeto); None = objeto en el infinito
CASOS = [
    (10, 10, 2.0, -1.0, -30.0),
    (10, 10, 2.0, 0.0, -30.0),
    (12, 6, 1.5, -0.5, -25.0),
    (10, 10, 2.0, 0.0, None),
]


@pytest.fixture(scope="module")
def parabolica():
    return haz(lente_biconvexa(10, 10, 2.0, 1.5, -1.0, -1.0), -30.0)


@pytest.mark.parametrize("R1, R2, espesor, k, y_objeto", CASOS)
def test_frente_de_onda_de_tercer_orden_igual_a_seidel(R1, R2, espesor, k, y_objeto):
    """Tres caminos independientes: Fermat (camino optico), Seidel y el trazado.
    Con la referencia en la imagen paraxial, W(h) = (S_I / 8) h^4 + O(h^6) y sin termino h^2."""
    lente = lente_biconvexa(R1, R2, espesor, 1.5, k, k)
    hz = haz(lente, y_objeto)
    hs = np.linspace(0.02, 0.3, 15)
    W = hz.frente_de_onda(hs, y_paraxial(lente, y_objeto))
    c2, c4, *_ = np.linalg.lstsq(np.vstack([hs**2, hs**4, hs**6, hs**8]).T, W, rcond=None)[0]
    assert np.isclose(c4, suma_seidel(lente, y_objeto, 1.0) / 8, rtol=1e-5)
    assert abs(c2) * hs[-1] ** 2 < 1e-6 * np.max(np.abs(W))  # sin desenfoque: el h^2 es ruido numerico


def test_la_interpolacion_reproduce_el_trazado(parabolica):
    lente, y_ref = parabolica.lente, y_paraxial(parabolica.lente, -30.0)
    rayo0 = trazar(lente, *rayo_a_altura(lente, -30.0, 0.0))
    for h in (0.1, 1.3, 2.5, 4.0):
        tr = trazar(lente, *rayo_a_altura(lente, -30.0, h))
        Q, e = tr.salida
        t = _hasta_esfera(np.array([Q]), np.array([e]), y_ref, lente.arriba.y_vertice)[0]
        directo = camino_optico(rayo0, lente.n) - (camino_optico(tr, lente.n) + t)
        assert abs(parabolica.frente_de_onda(h, y_ref)[0] - directo) < 1e-6 * LAM


def test_mejor_foco_de_onda_a_la_mitad_con_un_cuarto_del_rms(parabolica):
    """Tercer orden: W = W040 rho^4 + W020 rho^2 tiene el menor RMS con W020 = -W040, es decir
    a mitad de camino entre el foco paraxial y el marginal, y ese RMS es 1/4 del paraxial
    (sqrt(1/180) frente a sqrt(4/45))."""
    f = mejor_foco_onda(parabolica, h_max=0.3)
    assert np.isclose(f.fraccion(f.y_ref), 0.5, atol=0.002)
    assert np.isclose(f.rms / f.rms_paraxial, 0.25, atol=0.001)


def test_patron_de_airy_de_una_lente_perfecta():
    rho, pesos = pupila(2000)
    na = 0.1
    r = np.linspace(0.0, 1.2 * AIRY * LAM / na, 4000)
    I = intensidad(pesos, np.zeros_like(rho), na * rho, r)
    assert np.isclose(I[0], 1.0, atol=1e-6)
    cero = r[np.argmin(I[: len(r) * 9 // 10])]
    assert np.isclose(cero, AIRY * LAM / na, rtol=2e-3)       # primer anillo oscuro: 0.61 lambda / NA


def test_strehl_exacto_coincide_con_marechal_si_la_aberracion_es_chica(parabolica):
    for h_max in (0.8, 1.0, 1.2):
        f = mejor_foco_onda(parabolica, h_max)
        assert abs(strehl(parabolica, h_max, f.y_ref) - strehl_marechal(f.rms / LAM)) < 0.005


def test_escalas_con_la_apertura(parabolica):
    """Frente de onda ~ h^4, mancha geometrica ~ h^3 y disco de Airy ~ 1/h."""
    s1, s2 = (mejor_foco_onda(parabolica, h).rms for h in (0.2, 0.4))
    g1, g2 = (radio_rms_geometrico(parabolica, h) for h in (0.2, 0.4))
    a1, a2 = (radio_airy(parabolica, h) for h in (0.2, 0.4))
    assert np.isclose(s2 / s1, 16, rtol=0.02)
    assert np.isclose(g2 / g1, 8, rtol=0.02)
    assert np.isclose(a1 / a2, 2, rtol=0.01)


def test_los_dos_criterios_de_difraccion_coinciden(parabolica):
    """Marechal (W_rms = lambda/14, Strehl 0.8) y mancha geometrica = disco de Airy
    dan casi la misma apertura limite."""
    h_marechal, h_cruce = apertura_limite(parabolica), apertura_cruce(parabolica)
    assert np.isclose(h_marechal, h_cruce, rtol=0.05)
    f = mejor_foco_onda(parabolica, h_marechal)
    assert np.isclose(f.rms / LAM, 1 / 14, rtol=1e-6)
    assert np.isclose(strehl(parabolica, h_marechal, f.y_ref), 0.8, atol=0.03)


def test_la_conica_que_anula_el_tercer_orden_amplia_la_apertura_limite():
    esferica = haz(lente_biconvexa(10, 10, 2.0, 1.5, 0.0, 0.0), -30.0)
    asferica = haz(lente_biconvexa(10, 10, 2.0, 1.5, -2.33, -2.33), -30.0)
    assert apertura_limite(asferica) > 3 * apertura_limite(esferica)


def test_un_haz_que_no_atraviesa_la_lente_avisa():
    diamante = lente_biconvexa(6.0, 6.0, 2.0, n=2.4)
    with pytest.raises(ValueError):
        haz(diamante, -8.0)
