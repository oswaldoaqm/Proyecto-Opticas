"""Prediccion paraxial (actividad 4): matrices ABCD y ecuacion de lente delgada."""
import numpy as np

from lentes import focal_efectiva, imagen_lente_delgada, imagen_paraxial, lente_biconvexa, matriz_sistema


def test_determinante_unitario_de_aire_a_aire():
    lente = lente_biconvexa(10.0, 14.0, 3.0, n=1.62)
    assert np.isclose(np.linalg.det(matriz_sistema(lente)), 1.0)


def test_focal_coincide_con_la_ecuacion_del_fabricante_para_lente_gruesa():
    n, R1, R2, d = 1.5, 10.0, -10.0, 2.0  # radios con signo
    esperado = 1.0 / ((n - 1) * (1 / R1 - 1 / R2 + (n - 1) * d / (n * R1 * R2)))
    assert np.isclose(focal_efectiva(lente_biconvexa(10.0, 10.0, d, n=n)), esperado)


def test_lente_muy_delgada_tiende_a_la_ecuacion_de_lente_delgada():
    lente = lente_biconvexa(10.0, 10.0, 1e-6, n=1.5)
    P = (0.8, -30.0)
    gruesa, delgada = imagen_paraxial(lente, P), imagen_lente_delgada(lente, P)
    assert np.isclose(gruesa.y, delgada.y, atol=1e-4)
    assert np.isclose(gruesa.aumento, delgada.aumento, atol=1e-5)


def test_objeto_a_2f_da_imagen_a_2f_invertida():
    lente = lente_biconvexa(10.0, 10.0, 1e-6, n=1.5)  # f = 10
    img = imagen_lente_delgada(lente, (1.0, -20.0))
    assert np.isclose(img.y, 20.0) and np.isclose(img.aumento, -1.0)
