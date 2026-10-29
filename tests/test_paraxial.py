"""Prediccion paraxial (actividad 4): matrices ABCD y ecuacion de lente delgada."""
import numpy as np
import pytest

from lentes import (
    focal_efectiva,
    imagen_lente_delgada,
    imagen_paraxial,
    lente_biconvexa,
    matriz_sistema,
    planos_principales,
)


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


@pytest.mark.parametrize("R1, R2, espesor, n, y_objeto", [
    (10, 10, 2.0, 1.5, -30.0),
    (8, 15, 3.0, 1.62, -40.0),
    (20, 7, 2.5, 1.5, -12.0),
])
def test_gauss_con_los_planos_principales_da_la_imagen_de_la_lente_gruesa(R1, R2, espesor, n, y_objeto):
    """1/s + 1/s' = 1/f no falla con una lente gruesa si f es la focal efectiva y s, s' se miden
    desde los planos principales: lo que falla es el modelo delgado (f de la lente delgada y
    las distancias medidas desde el centro)."""
    lente = lente_biconvexa(R1, R2, espesor, n=n)
    y_H, y_Hp = planos_principales(lente)
    f = focal_efectiva(lente)
    s = y_H - y_objeto
    y_imagen = y_Hp + 1.0 / (1.0 / f - 1.0 / s)
    assert np.isclose(y_imagen, imagen_paraxial(lente, (0.0, y_objeto)).y, rtol=1e-12)


def test_planos_principales_de_la_lente_simetrica():
    """En la lente de trabajo los planos quedan simetricos respecto del centro, a 0.310 de el."""
    y_H, y_Hp = planos_principales(lente_biconvexa(10, 10, 2.0, n=1.5))
    assert np.isclose(y_H, -y_Hp) and np.isclose(y_Hp, 0.3103, atol=1e-4)
    assert np.isclose(focal_efectiva(lente_biconvexa(10, 10, 2.0, n=1.5)), 10.345, atol=1e-3)
