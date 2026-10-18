"""La escena de la simulacion (notebook 03) frente a calculos independientes."""
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pytest  # noqa: E402

from lentes import lente_biconvexa, trazar  # noqa: E402
from lentes.a_mano import cruce_de_dos_rayos, trazar_a_mano  # noqa: E402
from lentes.simulacion import (  # noqa: E402
    AMARILLO,
    COLORES,
    dibujar_escena,
    escena,
    lente_desde_formulas,
    limpio,
    rango_angular,
    resumen,
    tramos,
)

PARABOLICA = lente_biconvexa(10.0, 10.0, 2.0, n=1.5, k1=-1.0, k2=-1.0)


@pytest.mark.parametrize("P, alfas", [((0.0, -30.0), (2.0, -2.0)), ((-1.0, -30.0), (0.0, 4.0))])
def test_imagen_igual_al_ejemplo_resuelto_a_mano(P, alfas):
    """Los dos puntos objeto del notebook 01, calculados con el metodo independiente."""
    esc = escena(PARABOLICA, P, alfas)
    punto, _, _ = cruce_de_dos_rayos(*(trazar_a_mano(P, math.radians(a)) for a in alfas))
    assert esc.imagen is not None and not esc.imagen.virtual
    assert np.allclose(esc.imagen.punto, punto, rtol=0, atol=1e-9)


def test_lente_por_formulas_igual_a_la_conica():
    por_formulas = lente_desde_formulas("-1 + x**2/20", "1 - x^2/20", n=1.5)
    assert np.isclose(por_formulas.semiapertura, PARABOLICA.semiapertura, rtol=1e-9)
    a = escena(por_formulas, (0.3, -25), (3, -1))
    b = escena(PARABOLICA, (0.3, -25), (3, -1))
    assert np.allclose(a.imagen.punto, b.imagen.punto, atol=1e-9)
    assert np.isclose(a.paraxial.y, b.paraxial.y, rtol=1e-12)


def test_el_abanico_cubre_la_lente_de_borde_a_borde():
    P = (0.5, -20.0)
    amin, amax = rango_angular(PARABOLICA, P)
    esc = escena(PARABOLICA, P, (1, -1), n_abanico=9)
    xs = [tr.puntos[1][0] for tr in esc.abanico]
    assert all(limpio(tr) for tr in esc.abanico)
    assert xs == sorted(xs)
    assert xs[0] < -0.9 * PARABOLICA.semiapertura and xs[-1] > 0.9 * PARABOLICA.semiapertura
    for alfa in (amin, amax):
        tr = trazar(PARABOLICA, P, [math.sin(alfa), math.cos(alfa)])
        assert np.isclose(abs(tr.puntos[1][0]), 0.995 * PARABOLICA.semiapertura, rtol=1e-6)


def test_tramos_de_un_rayo_normal_y_de_uno_con_reflexion_total():
    normal = tramos(trazar(PARABOLICA, (0, -30), [math.sin(0.03), math.cos(0.03)]))
    assert [t for t, _, _ in normal] == ["incidente", "transmitido", "emergente"]
    diamante = lente_biconvexa(6.0, 6.0, 2.0, n=2.4)
    tr = trazar(diamante, (0, -8), [math.sin(math.radians(19)), math.cos(math.radians(19))])
    tipos = [t for t, _, _ in tramos(tr)]
    assert any(d.reflexion_total for d in tr.detalles)
    assert tipos[0] == "incidente" and tipos[-1] == "emergente"
    assert tipos.count("transmitido") == len(tipos) - 2      # todo lo de en medio va por el vidrio
    assert not limpio(tr)
    esc = escena(diamante, (0, -8), (19, -8))
    assert esc.imagen is None and "reflexión total" in resumen(esc)


def test_objeto_dentro_del_foco_da_imagen_virtual():
    esc = escena(PARABOLICA, (0, -7), (8, -8))
    assert esc.imagen.virtual and esc.paraxial.virtual
    assert esc.imagen.punto[1] < -7 and esc.paraxial.y < -7


def test_dibujo_con_los_colores_del_proyecto():
    esc = escena(PARABOLICA, (0, -30), (2, -2), n_abanico=5)
    fig, ax = plt.subplots()
    dibujar_escena(ax, esc)
    lineas = {matplotlib.colors.to_hex(linea.get_color()) for linea in ax.get_lines()}
    rellenos = {matplotlib.colors.to_hex(linea.get_markerfacecolor()) for linea in ax.get_lines()}
    assert set(COLORES.values()) <= lineas and AMARILLO in rellenos
    plt.close(fig)
    assert "Imagen con los rayos 1 y 2: (0.000, 16.029), real" in resumen(esc)
