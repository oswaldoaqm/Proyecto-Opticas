"""Teoria de tercer orden (Seidel) frente al trazado exacto."""
import numpy as np
import pytest
from scipy.optimize import minimize_scalar

from lentes import lente_biconvexa, lente_con_forma
from lentes.aberraciones import aberracion_longitudinal, coeficiente_esferica_trazado
from lentes.seidel import coeficiente_esferica, k_que_anula

# (R1, R2, espesor, k, y_objeto); y_objeto None = objeto en el infinito
CASOS = [
    (10, 10, 2.0, -1.0, -30.0),
    (10, 10, 2.0, 0.0, -30.0),
    (8, 15, 3.0, 0.0, -40.0),
    (12, 6, 1.5, -0.5, -25.0),
    (10, 10, 2.0, -1.0, -60.0),
    (20, 7, 2.5, 0.3, -35.0),
    (10, 10, 2.0, 0.0, None),
    (15, 9, 2.0, -1.0, None),
]


@pytest.mark.parametrize("R1, R2, espesor, k, y_objeto", CASOS)
def test_seidel_predice_el_coeficiente_del_trazado(R1, R2, espesor, k, y_objeto):
    lente = lente_biconvexa(R1, R2, espesor, 1.5, k, k)
    medido = coeficiente_esferica_trazado(lente, y_objeto)
    teoria = coeficiente_esferica(lente, y_objeto)
    assert medido < 0  # lente convergente: los rayos alejados del eje enfocan antes
    assert np.isclose(medido, teoria, rtol=1e-6)


def test_la_conica_que_anula_deja_solo_el_quinto_orden():
    esferica = lente_biconvexa(10, 10, 2.0, 1.5, 0.0, 0.0)
    k = k_que_anula(esferica, -30.0)
    asferica = lente_biconvexa(10, 10, 2.0, 1.5, k, k)
    assert abs(coeficiente_esferica(asferica, -30.0)) < 1e-12
    assert abs(coeficiente_esferica_trazado(asferica, -30.0)) < 1e-4 * abs(coeficiente_esferica(esferica, -30.0))
    dy = aberracion_longitudinal(asferica, -30.0, [1.0, 2.0])
    assert np.isclose(dy[1] / dy[0], 16.0, rtol=0.1)  # lo que queda crece como h^4


def test_forma_optima_de_una_lente_delgada_es_la_de_los_libros():
    """Objeto en el infinito: q optimo = 2 (n^2 - 1) / (n + 2) = 0.714 para n = 1.5."""
    r = minimize_scalar(lambda q: abs(coeficiente_esferica(lente_con_forma(q, 10.0, 1e-4), None)),
                        bounds=(0.3, 0.95), method="bounded", options={"xatol": 1e-7})
    assert np.isclose(r.x, 2 * (1.5**2 - 1) / (1.5 + 2), atol=1e-4)


def test_lente_con_forma_respeta_la_focal():
    from lentes import focal_efectiva

    for q in (-1.0, -0.4, 0.0, 0.65, 1.0):
        assert np.isclose(focal_efectiva(lente_con_forma(q, 10.0, 2.0)), 10.0, rtol=1e-10)
