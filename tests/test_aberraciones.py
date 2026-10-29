"""Aberracion esferica medida con el trazado (actividades 4 y 5)."""
import numpy as np

from lentes import lente_biconvexa
from lentes.aberraciones import (
    _pupila,
    abanico,
    aberracion_transversal,
    mejores_focos,
    radio_maximo,
    radio_rms,
    y_paraxial,
)

LENTE = lente_biconvexa(10, 10, 2.0, 1.5, 0.0, 0.0)


def test_rayos_paralelos_cercanos_al_eje_cruzan_en_el_foco_imagen():
    assert abs(abanico(LENTE, None, [0.01]).cruces()[0] - y_paraxial(LENTE, None)) < 1e-4


def test_la_aberracion_transversal_crece_como_h_al_cubo():
    ta = aberracion_transversal(LENTE, -30.0, [0.2, 0.4])
    assert np.isclose(ta[1] / ta[0], 8.0, rtol=0.03)


def test_mejores_focos_siguen_la_teoria_de_tercer_orden():
    """Con aberracion de tercer orden, el radio RMS minimo esta a 2/3 del camino entre el foco
    paraxial y el marginal, y el circulo de minima confusion a 3/4."""
    f = mejores_focos(LENTE, -30.0, h_max=0.3)
    assert np.isclose(f.fraccion(f.y_rms), 2 / 3, atol=0.002)
    assert np.isclose(f.fraccion(f.y_circulo), 3 / 4, atol=0.002)
    assert f.rms < f.radio_circulo


def test_en_el_foco_paraxial_la_mancha_es_mayor_que_en_el_mejor_foco():
    ab = abanico(LENTE, -30.0, _pupila(3.0, 300))
    f = mejores_focos(LENTE, -30.0, h_max=3.0, n=300)
    assert radio_rms(ab, f.y_paraxial) > 2 * f.rms


def test_mejores_focos_con_aberracion_zonal():
    """Con caras conicas casi corregidas la aberracion cambia de signo entre el centro y el
    borde de la pupila (aberracion zonal), y los mejores planos quedan fuera del tramo entre
    el foco paraxial y el del borde. Tienen que coincidir con un barrido fino del eje."""
    lente = lente_biconvexa(10, 10, 2.0, 1.5, -2.3444, -2.3444)
    h_max = 3.9
    f = mejores_focos(lente, -30.0, h_max)
    assert f.y_rms > max(f.y_paraxial, f.y_marginal)
    anillos = abanico(lente, -30.0, _pupila(h_max, 400))
    todos = abanico(lente, -30.0, np.append(_pupila(h_max, 400), h_max))
    ys = np.linspace(f.y_paraxial - 0.03, f.y_paraxial + 0.03, 6001)
    assert f.rms <= min(radio_rms(anillos, y) for y in ys) * (1 + 1e-9)
    assert f.radio_circulo <= min(radio_maximo(todos, y) for y in ys) * (1 + 1e-9)
