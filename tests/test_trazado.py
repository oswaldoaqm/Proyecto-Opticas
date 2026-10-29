"""Trazado completo por la lente, validado contra limites conocidos (decision 0006)."""
import numpy as np
import pytest

from lentes import (
    Lente,
    cruce_con_eje,
    desde_expresion,
    imagen_de_dos_rayos,
    imagen_paraxial,
    interseccion,
    interseccion_exacta,
    lente_biconvexa,
    parabolica,
    rayo_hacia,
    trazar,
)

P_EJE = np.array([0.0, -30.0])


@pytest.fixture(params=[-1.0, 0.0], ids=["caras_parabolicas", "caras_esfericas"])
def lente(request):
    return lente_biconvexa(10.0, 10.0, 2.0, n=1.5, k1=request.param, k2=request.param)


def cruce(lente, P, h):
    tr = trazar(lente, P, rayo_hacia(lente, P, h))
    assert tr.estado == "ok"
    Q, e = tr.salida
    return cruce_con_eje(Q, e)


def test_interseccion_coincide_con_la_formula_cuadratica():
    g = parabolica(-1.0, 10.0)  # y = -1 + x^2 / 20
    P = np.array([0.5, -10.0])
    u = np.array([0.05, 1.0]) / np.hypot(0.05, 1.0)
    lam = interseccion(P, u, g, semiapertura=5.0, lam_min=1e-9, lam_max=50.0)
    # -10 + lam uy = -1 + (0.5 + lam ux)^2 / 20   ->   a lam^2 + b lam + c = 0
    a = u[0] ** 2 / 20
    b = 2 * 0.5 * u[0] / 20 - u[1]
    c = 0.5**2 / 20 - 1.0 + 10.0
    raices = np.roots([a, b, c])
    esperado = min(r.real for r in raices if abs(r.imag) < 1e-12 and r.real > 0)
    assert np.isclose(lam, esperado, rtol=0, atol=1e-10)


def test_rayo_sobre_el_eje_no_se_desvia(lente):
    tr = trazar(lente, P_EJE, [0.0, 1.0])
    assert tr.estado == "ok" and len(tr.detalles) == 2
    assert np.allclose(tr.salida[1], [0.0, 1.0])


def test_cerca_del_eje_coincide_con_la_imagen_paraxial(lente):
    # a h = 0.001 la aberracion esferica mueve el cruce unos 3e-7: la tolerancia esta en esa escala
    y_par = imagen_paraxial(lente, P_EJE).y
    assert abs(cruce(lente, P_EJE, 0.001) - y_par) < 5e-7


@pytest.mark.parametrize("fraccion", [1e-3, 1e-4, 1e-6, 1e-9])
@pytest.mark.parametrize("P", [(0.0, -30.0), (-8.0, -6.0), (3.0, -12.0)])
def test_un_rayo_que_entra_junto_al_borde_se_refracta(lente, P, fraccion):
    """Un rayo dirigido a una fraccion minima del borde de la cara g debe refractarse alli
    (antes, la busqueda del impacto lo perdia y el rayo cruzaba la lente sin desviarse)."""
    a = lente.semiapertura
    for signo in (1, -1):
        u = rayo_hacia(lente, P, signo * a * (1 - fraccion))
        tr = trazar(lente, P, u)
        lam = interseccion_exacta(P, u, lente.abajo, a)
        assert tr.caras[:1] == ["g"]
        assert np.allclose(tr.puntos[1], np.asarray(P) + lam * u, atol=1e-9)


def test_aberracion_esferica_crece_como_h_al_cuadrado(lente):
    y_par = imagen_paraxial(lente, P_EJE).y
    d1 = cruce(lente, P_EJE, 0.2) - y_par
    d2 = cruce(lente, P_EJE, 0.4) - y_par
    assert d1 < 0 and d2 < 0  # los rayos alejados del eje enfocan antes
    assert np.isclose(d2 / d1, 4.0, rtol=0.02)


def test_rayos_simetricos_cruzan_en_el_mismo_punto(lente):
    assert np.isclose(cruce(lente, P_EJE, 2.5), cruce(lente, P_EJE, -2.5), atol=1e-9)


def test_un_rayo_trazado_hacia_atras_vuelve_al_objeto(lente):
    P = np.array([0.7, -25.0])
    ida = trazar(lente, P, rayo_hacia(lente, P, 2.0))
    Q, e = ida.salida
    vuelta = trazar(lente, Q + 15.0 * e, -e)
    R, d = vuelta.salida
    v = P - R
    distancia = abs(v[0] * d[1] - v[1] * d[0])  # distancia de P a la recta R + s d
    assert vuelta.estado == "ok" and distancia < 1e-8


def test_objeto_fuera_del_eje_converge_a_la_paraxial(lente):
    """Fuera del eje la imagen se aparta de la paraxial con terminos de tercer orden en la
    altura del objeto: ~ x_P^2 a lo largo del eje y ~ x_P^3 en altura. Con la mitad de
    altura, las diferencias deben caer 4 y 8 veces."""

    def diferencia(xP):
        P = np.array([xP, -30.0])
        t1 = trazar(lente, P, rayo_hacia(lente, P, -0.01))
        t2 = trazar(lente, P, rayo_hacia(lente, P, 0.01))
        img = imagen_de_dos_rayos(t1, t2)
        par = imagen_paraxial(lente, P)
        assert not img.virtual and not par.virtual
        return img.punto[0] - par.x, img.punto[1] - par.y

    dx1, dy1 = diferencia(-1.0)
    dx2, dy2 = diferencia(-0.5)
    assert np.isclose(dy1 / dy2, 4.0, rtol=0.05)  # a lo largo del eje: ~ x_P^2
    assert np.isclose(dx1 / dx2, 8.0, rtol=0.05)  # en altura: ~ x_P^3
    assert abs(dy2) < 0.02 and abs(dx2) < 1e-3


def test_objeto_dentro_de_la_focal_da_imagen_virtual():
    lente = lente_biconvexa(10.0, 10.0, 2.0, n=1.5, k1=-1.0, k2=-1.0)
    P = np.array([0.0, -6.0])  # mas cerca que la distancia focal (~10.3)
    t1 = trazar(lente, P, rayo_hacia(lente, P, 0.02))
    t2 = trazar(lente, P, rayo_hacia(lente, P, -0.02))
    img = imagen_de_dos_rayos(t1, t2)
    par = imagen_paraxial(lente, P)
    assert img.virtual and par.virtual
    assert np.isclose(img.punto[1], par.y, rtol=1e-4)


def test_rayo_que_no_toca_la_lente():
    lente = lente_biconvexa(10.0, 10.0, 2.0)
    assert trazar(lente, P_EJE, [1.0, 0.2]).estado == "no_toca_lente"


def test_reflexion_total_interna_en_una_placa():
    placa = Lente(abajo=desde_expresion("-1"), arriba=desde_expresion("1"), n=1.5, semiapertura=50.0)
    th = np.radians(60)  # mayor que el angulo critico vidrio-aire (41.8 grados)
    tr = trazar(placa, [0.0, 0.0], [np.sin(th), np.cos(th)])
    assert tr.eventos[0] == "reflexion_total"
    assert np.allclose(tr.direcciones[1], [np.sin(th), -np.cos(th)])
