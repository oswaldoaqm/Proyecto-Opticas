"""Regenera TODAS las figuras del proyecto en la carpeta figuras/ (decision 0005).

Uso (desde la raiz del repo):
    python scripts/generar_figuras.py               # todas
    python scripts/generar_figuras.py --lista       # ver cuales hay
    python scripts/generar_figuras.py fig00_boceto_trazado

Cada figura es una funcion registrada con @figura("nombre"). Ninguna figura se
edita a mano: si hay que cambiarla, se cambia aqui y se vuelve a generar.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Arc  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402
from scipy.optimize import minimize_scalar  # noqa: E402

from lentes import (  # noqa: E402
    cruce_con_eje,
    imagen_lente_delgada,
    imagen_paraxial,
    lente_biconvexa,
    lente_con_forma,
    rayo_hacia,
    trazar,
)
from lentes.aberraciones import (  # noqa: E402
    abanico,
    aberracion_longitudinal,
    coeficiente_esferica_trazado,
    mejores_focos,
    y_paraxial,
)
from lentes.estilo import (  # noqa: E402
    AQUA,
    AZUL,
    EJE,
    NARANJA,
    RAMPA_AZUL,
    REJILLA,
    SUPERFICIE,
    TENUE,
    TINTA,
    TINTA_2,
    aplicar_estilo,
    color_por_altura,
    guardar_figura,
)
from lentes.graficos import dibujar_lente, dibujar_trayectoria  # noqa: E402
from lentes.seidel import coeficiente_esferica, k_que_anula  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
CARPETA = RAIZ / "figuras"
FIGURAS = {}


def figura(nombre):
    def registrar(fn):
        FIGURAS[nombre] = fn
        return fn
    return registrar


def _cruces(lente, P, alturas):
    """Donde cruza el eje cada rayo que entra a la lente a la altura h."""
    ys = []
    for h in alturas:
        tr = trazar(lente, P, rayo_hacia(lente, P, h))
        Q, e = tr.salida
        ys.append(cruce_con_eje(Q, e) if tr.estado == "ok" else np.nan)
    return np.array(ys)


@figura("fig00_boceto_trazado")
def boceto_trazado():
    """Abanico de rayos, zoom al foco y aberracion esferica: parabola vs esfera."""
    n, R, espesor, yP = 1.5, 10.0, 2.0, -30.0
    P = np.array([0.0, yP])
    parab = lente_biconvexa(R, R, espesor, n, k1=-1.0, k2=-1.0)
    esfer = lente_biconvexa(R, R, espesor, n, k1=0.0, k2=0.0)
    y_par = imagen_paraxial(parab, P).y          # igual para ambas: mismos radios de vertice
    y_del = imagen_lente_delgada(parab, P).y
    h_max = 0.9 * min(parab.semiapertura, esfer.semiapertura)
    hs = np.linspace(0.02, h_max, 80)
    c_par, c_esf = _cruces(parab, P, hs), _cruces(esfer, P, hs)
    y_marg = c_par[-1]

    fig = plt.figure(figsize=(11, 7.0))
    gs = fig.add_gridspec(2, 2, height_ratios=[0.62, 1.0], width_ratios=[2.5, 1],
                          hspace=0.44, wspace=0.14)
    ax = fig.add_subplot(gs[0, :])
    axb = fig.add_subplot(gs[1, 0])
    axz = fig.add_subplot(gs[1, 1])

    # (a) abanico de rayos; vista girada: la luz va de izquierda a derecha
    y_fin = y_par + 9
    a_fan = 0.9 * parab.semiapertura
    for a in (ax, axz):
        dibujar_lente(a, parab)
        a.axhline(0, color="#c3c2b7", lw=0.8, zorder=0)
    for h in np.linspace(-a_fan, a_fan, 15):
        tr = trazar(parab, P, rayo_hacia(parab, P, h))
        if tr.estado != "ok":
            continue
        for a in (ax, axz):
            dibujar_trayectoria(a, tr, y_final=y_fin, color=color_por_altura(h, a_fan))

    ax.plot(yP, 0, "o", color=TINTA, ms=6, zorder=5)
    ax.annotate("P (objeto)", (yP, 0), xytext=(0, 9), textcoords="offset points",
                ha="center", color=TINTA, fontsize=9)
    ax.plot(y_par, 0, "o", mfc=SUPERFICIE, mec=TINTA, ms=7, mew=1.4, zorder=6)
    ax.annotate("imagen paraxial", (y_par, 0), xytext=(8, 12), textcoords="offset points",
                ha="left", color=TINTA, fontsize=9)
    ax.annotate("lente, $n_L=1.5$", (0, parab.semiapertura), xytext=(0, 4), textcoords="offset points",
                ha="center", va="bottom", color=TINTA_2, fontsize=8.5)
    for cara, sup, dx in (("cara g(x)", parab.abajo, -52), ("cara f(x)", parab.arriba, 18)):
        ax.annotate(cara, (float(sup(-2.6)), -2.6), xytext=(dx, -16), textcoords="offset points",
                    color=TINTA_2, fontsize=8.5, va="top",
                    arrowprops=dict(arrowstyle="-", color=TENUE, lw=0.7))
    ax.set_xlim(yP - 2, y_fin)
    ax.set_ylim(-parab.semiapertura - 2.2, parab.semiapertura + 1.6)
    ax.set_aspect("equal")
    ax.set_xlabel("y  (eje óptico; la luz avanza en +y)")
    ax.set_ylabel("x")
    ax.set_title("(a) Dos refracciones por rayo: el color marca la altura del rayo "
                 "(más oscuro = más lejos del eje)", loc="left", fontsize=10)

    # zoom al foco: tres predicciones sobre el eje
    caja = dict(boxstyle="round,pad=0.18", fc=SUPERFICIE, ec="none", alpha=0.92)
    axz.plot(y_par, 0, "o", mfc=SUPERFICIE, mec=TINTA, ms=7, mew=1.4, zorder=6)
    axz.plot(y_del, 0, "D", color=TENUE, ms=5.5, zorder=6)
    axz.plot(y_marg, 0, "o", color=RAMPA_AZUL[-1], ms=5.5, zorder=6)
    axz.annotate("paraxial\n(lente gruesa)", (y_par, 0), xytext=(0, 14), textcoords="offset points",
                 ha="center", color=TINTA, fontsize=8, bbox=caja, zorder=7)
    axz.annotate("lente\ndelgada", (y_del, 0), xytext=(0, -30), textcoords="offset points",
                 ha="center", color=TINTA_2, fontsize=8, bbox=caja, zorder=7)
    axz.annotate("rayo\nmarginal", (y_marg, 0), xytext=(0, 14), textcoords="offset points",
                 ha="center", color=TINTA_2, fontsize=8, bbox=caja, zorder=7)
    axz.set_xlim(y_marg - 0.7, y_par + 0.7)
    axz.set_ylim(-0.5, 0.5)
    axz.set_title("Zoom al foco: dónde cruza el eje", loc="left", fontsize=10)
    axz.set_xlabel("y")

    # (b) aberracion esferica longitudinal
    axb.axhline(0, color=TENUE, lw=1.0, ls=(0, (4, 3)), zorder=1)
    axb.annotate("imagen paraxial (lente gruesa)", (0.05, 0), xytext=(0, 4),
                 textcoords="offset points", color=TINTA_2, fontsize=8.5)
    axb.axhline(y_del - y_par, color=TENUE, lw=1.0, ls=(0, (1, 2)), zorder=1)
    axb.annotate("predicción de lente delgada\n(ignora el espesor)", (4.72, y_del - y_par), xytext=(0, -5),
                 textcoords="offset points", ha="right", va="top", color=TINTA_2, fontsize=8.5)
    axb.plot(hs, c_par - y_par, color=AZUL, lw=2, label="caras parabólicas", zorder=3)
    axb.plot(hs, c_esf - y_par, color=NARANJA, lw=2, label="caras esféricas", zorder=3)
    for ys, etiqueta in ((c_par, "caras\nparabólicas"), (c_esf, "caras\nesféricas")):
        axb.annotate(etiqueta, (hs[-1], ys[-1] - y_par), xytext=(6, 0), textcoords="offset points",
                     ha="left", va="center", color=TINTA_2, fontsize=8.5)
    axb.set_xlim(-0.1, 4.75)
    axb.set_xlabel("altura h a la que el rayo entra en la lente")
    axb.set_ylabel("Δy = cruce con el eje - imagen paraxial")
    axb.set_title("(b) Aberración esférica: cuanto más lejos del eje, antes enfoca el rayo",
                  loc="left", fontsize=10)
    axb.grid(True, color=REJILLA, lw=0.6)
    axb.legend(frameon=False, loc="lower left", fontsize=8.5, labelcolor=TINTA_2)

    fig.suptitle("Boceto del Grupo 1 - trazado vectorial en una lente biconvexa gruesa "
                 f"(R = {R:g}, espesor = {espesor:g}, objeto en y = {yP:g})",
                 x=0.06, ha="left", fontsize=11.5, color=TINTA, y=0.995)
    return fig


def _girar(v):
    """Punto o vector del modelo (x, y) -> coordenadas de la vista girada (y, x)."""
    return np.array([v[1], v[0]], dtype=float)


def _angulo_vista(v) -> float:
    w = _girar(v)
    return float(np.degrees(np.arctan2(w[1], w[0])))


def _flecha(ax, origen, vector, color, lw=1.6, z=6):
    o, v = _girar(origen), _girar(vector)
    ax.annotate("", xy=o + v, xytext=o, zorder=z,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, shrinkA=0, shrinkB=0,
                                mutation_scale=11))


def _arco(ax, centro, v1, v2, r, color, texto, factor=1.75):
    """Arco del angulo entre las direcciones v1 y v2 (el menor), con su etiqueta."""
    c = _girar(centro)
    a1, a2 = _angulo_vista(v1), _angulo_vista(v2)
    d = (a2 - a1 + 180.0) % 360.0 - 180.0
    t1, t2 = (a1, a1 + d) if d >= 0 else (a1 + d, a1)
    ax.add_patch(Arc(c, 2 * r, 2 * r, theta1=t1, theta2=t2, color=color, lw=1.2, zorder=5))
    m = np.radians(0.5 * (t1 + t2))
    ax.text(c[0] + factor * r * np.cos(m), c[1] + factor * r * np.sin(m), texto, color=color,
            ha="center", va="center", fontsize=9, zorder=7)


@figura("fig01_geometria_refraccion")
def geometria_refraccion():
    """Construccion vectorial en cada cara: tangente, normal del enunciado, normal usada y angulos."""
    lente = lente_biconvexa(10.0, 10.0, 2.0, 1.5, k1=-1.0, k2=-1.0)
    P = np.array([0.0, -30.0])
    tr = trazar(lente, P, rayo_hacia(lente, P, 3.0))
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.6))
    fig.subplots_adjust(left=0.03, right=0.97, top=0.84, bottom=0.08, wspace=0.08)
    paneles = (
        (axs[0], 1, lente.abajo, "(a) Cara g: del aire al vidrio", ("aire, n = 1", "vidrio, $n_L$ = 1.5")),
        (axs[1], 2, lente.arriba, "(b) Cara f: del vidrio al aire", ("vidrio, $n_L$ = 1.5", "aire, n = 1")),
    )
    largo_vector, largo_rayo = 0.62, 1.0
    for ax, i, sup, titulo, (medio_entrada, medio_salida) in paneles:
        Q = tr.puntos[i]
        u_in, u_out = tr.direcciones[i - 1], tr.direcciones[i]
        det = tr.detalles[i - 1]
        t_hat, n_enunciado, n_usada = sup.tangente(Q[0]), sup.normal(Q[0]), det.normal

        dibujar_lente(ax, lente)
        for v, estilo in ((t_hat, (0, (5, 3))), (n_usada, (0, (1, 2)))):  # rectas guia
            a, b = _girar(Q - 1.4 * v), _girar(Q + 1.4 * v)
            ax.plot([a[0], b[0]], [a[1], b[1]], color=TENUE, lw=0.9, ls=estilo, zorder=2)

        # el rayo: incidente y refractado, con una punta de flecha a mitad de cada tramo
        for inicio, d in ((Q - largo_rayo * u_in, u_in), (Q, u_out)):
            a, b = _girar(inicio), _girar(inicio + largo_rayo * d)
            ax.plot([a[0], b[0]], [a[1], b[1]], color=AZUL, lw=2.2, zorder=4, solid_capstyle="round")
            _flecha(ax, inicio + 0.45 * largo_rayo * d, 0.12 * d, AZUL, lw=2.2, z=4)

        _flecha(ax, Q, largo_vector * t_hat, TINTA_2, lw=1.4)
        _flecha(ax, Q, largo_vector * n_enunciado, TENUE, lw=1.4)
        _flecha(ax, Q, largo_vector * n_usada, NARANJA, lw=2.2, z=7)
        _arco(ax, Q, n_usada, -u_in, 0.36, TINTA, f"$\\theta_i$ = {np.degrees(det.theta_i):.1f}°", factor=1.6)
        _arco(ax, Q, -n_usada, u_out, 0.36, TINTA, f"$\\theta_t$ = {np.degrees(det.theta_t):.1f}°", factor=1.6)

        # etiquetas de los vectores, justo despues de la punta (sin tapar la flecha)
        caja = dict(boxstyle="round,pad=0.15", fc=SUPERFICIE, ec="none", alpha=0.9)
        for vector, texto, color in ((t_hat, "$\\hat t$", TINTA_2),
                                     (n_enunciado, "$\\hat n$ del enunciado", TENUE),
                                     (n_usada, "normal usada\n($\\hat n \\cdot \\hat u < 0$)", NARANJA)):
            w = _girar(vector)
            p = _girar(Q + (largo_vector + 0.06) * vector)
            ax.text(p[0], p[1], texto, color=color, fontsize=8.5, bbox=caja, zorder=8,
                    ha="left" if w[0] > 0.3 else ("right" if w[0] < -0.3 else "center"),
                    va="bottom" if w[1] > 0.3 else ("top" if w[1] < -0.3 else "center"))
        ax.text(0.03, 0.96, medio_entrada, transform=ax.transAxes, ha="left", va="top",
                color=TINTA_2, fontsize=9, bbox=caja, zorder=8)
        ax.text(0.97, 0.96, medio_salida, transform=ax.transAxes, ha="right", va="top",
                color=TINTA_2, fontsize=9, bbox=caja, zorder=8)

        c = _girar(Q)
        ax.set_xlim(c[0] - 1.15, c[0] + 1.15)
        ax.set_ylim(c[1] - 0.95, c[1] + 0.95)
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        for lado in ("top", "right", "bottom", "left"):
            ax.spines[lado].set_visible(True)
            ax.spines[lado].set_color(EJE)
        ax.set_title(titulo, loc="left", fontsize=10)

    fig.suptitle("Refracción vectorial: en cada cara se usa la normal que mira hacia el medio de donde llega la luz",
                 x=0.03, ha="left", fontsize=11, color=TINTA, y=0.99)
    fig.text(0.03, 0.02, "Rayo de P = (0, -30) que entra a la altura x = 3 en una lente de caras parabólicas "
             "(R = 10, espesor 2). Vista girada: la luz avanza de izquierda a derecha.",
             ha="left", fontsize=8.5, color=TINTA_2)
    return fig


def _umbrales(ax, x_texto):
    """Lineas de referencia en 1 % y 0.1 %."""
    for nivel, texto in ((1.0, "1 %"), (0.1, "0.1 %")):
        ax.axhline(nivel, color=TENUE, lw=0.8, ls=(0, (4, 3)), zorder=1)
        ax.text(x_texto, nivel * 1.12, texto, color=TENUE, fontsize=8, ha="right", va="bottom")


def _guia_pendiente(ax, x0, x1, y0, potencia, texto):
    """Recta de referencia y = y0 (x / x0)^potencia en escala log-log."""
    xs = np.array([x0, x1])
    ax.loglog(xs, y0 * (xs / x0) ** potencia, color=TENUE, lw=1.0, ls=(0, (1, 2)), zorder=2)
    ax.text(np.sqrt(x0 * x1), y0 * (np.sqrt(x1 / x0)) ** potencia * 0.55, texto, color=TENUE,
            fontsize=8.5, ha="left", va="top")


def _cruce_log(x, y, nivel):
    """x donde la curva creciente y(x) alcanza el nivel (interpolando en escala log)."""
    return float(np.exp(np.interp(np.log(nivel), np.log(y), np.log(x))))


@figura("fig02_cuando_vale_paraxial")
def cuando_vale_paraxial():
    """Actividad 4: la diferencia con la paraxial crece como h^2 (apertura) y el error de la
    ecuacion de lente delgada como d (espesor)."""
    y_obj = -30.0
    casos = (("caras parabólicas", lente_biconvexa(10, 10, 2.0, 1.5, -1.0, -1.0), AZUL),
             ("caras esféricas", lente_biconvexa(10, 10, 2.0, 1.5, 0.0, 0.0), NARANJA))
    h_max = 0.9 * min(L.semiapertura for _, L, _ in casos)
    hs = np.geomspace(0.05, h_max, 70)

    fig, (axa, axb) = plt.subplots(1, 2, figsize=(11, 4.8))
    fig.subplots_adjust(left=0.07, right=0.98, top=0.83, bottom=0.21, wspace=0.27)

    # (a) apertura
    for (nombre, L, color), (dx, dy, ha, va) in zip(casos, ((8, -6, "left", "top"), (-8, 6, "right", "bottom"))):
        rel = 100 * np.abs(aberracion_longitudinal(L, y_obj, hs)) / y_paraxial(L, y_obj)
        axa.loglog(hs, rel, color=color, lw=2, label=nombre, zorder=3)
        h1 = _cruce_log(hs, rel, 1.0)
        axa.plot(h1, 1.0, "o", color=color, ms=6, zorder=4)
        axa.annotate(f"h = {h1:.2f}", (h1, 1.0), xytext=(dx, dy), textcoords="offset points",
                     ha=ha, va=va, color=TINTA_2, fontsize=8.5)
    _umbrales(axa, hs[-1])
    _guia_pendiente(axa, 0.06, 0.6, 3e-4, 2, "pendiente 2: ∝ h²")
    axa.set_xlabel("altura h a la que el rayo entra en la lente")
    axa.set_ylabel("diferencia con la paraxial\n(% de la distancia imagen)")
    axa.set_title("(a) Apertura: la diferencia crece como h²", loc="left", fontsize=10)
    axa.legend(frameon=False, loc="upper left", fontsize=8.5, labelcolor=TINTA_2)

    # (b) espesor
    ds = np.geomspace(0.01, 4.0, 60)
    error = []
    for d in ds:
        L = lente_biconvexa(10, 10, d, 1.5)
        gruesa = imagen_paraxial(L, (0.0, y_obj)).y
        delgada = imagen_lente_delgada(L, (0.0, y_obj)).y
        error.append(100 * abs(delgada - gruesa) / gruesa)
    error = np.array(error)
    axb.loglog(ds, error, color=TINTA_2, lw=2, zorder=3)
    d1 = _cruce_log(ds, error, 1.0)
    e2 = float(np.exp(np.interp(np.log(2.0), np.log(ds), np.log(error))))
    axb.plot([d1, 2.0], [1.0, e2], "o", color=TINTA_2, ms=6, zorder=4)
    axb.annotate(f"d = {d1:.2f}", (d1, 1.0), xytext=(-7, 7), textcoords="offset points",
                 ha="right", color=TINTA_2, fontsize=8.5)
    axb.annotate(f"nuestra lente: d = 2, error {e2:.1f} %", (2.0, e2), xytext=(-8, 6),
                 textcoords="offset points", ha="right", color=TINTA_2, fontsize=8.5)
    _umbrales(axb, ds[-1])
    _guia_pendiente(axb, 0.012, 0.12, 0.012, 1, "pendiente 1: ∝ d")
    axb.set_xlabel("espesor d de la lente (radios R = 10)")
    axb.set_ylabel("error de la ecuación de lente delgada\n(% de la distancia imagen)")
    axb.set_title("(b) Espesor: el error de lente delgada crece como d", loc="left", fontsize=10)

    decimal = FuncFormatter(lambda v, _: f"{v:g}")
    for ax in (axa, axb):
        ax.xaxis.set_major_formatter(decimal)
        ax.yaxis.set_major_formatter(decimal)

    fig.suptitle("¿Cuándo coinciden el trazado vectorial y la aproximación paraxial?",
                 x=0.03, ha="left", fontsize=11.5, color=TINTA, y=0.98)
    fig.text(0.03, 0.03, "Lente biconvexa con R = 10 y n = 1.5; objeto sobre el eje a 30 unidades del centro. "
             "En (a) el espesor es 2; en (b) se comparan dos predicciones paraxiales.",
             ha="left", fontsize=8.5, color=TINTA_2)
    return fig


@figura("fig03_aberracion_esferica")
def aberracion_esferica():
    """Actividad 5: aberracion longitudinal (trazado y Seidel), transversal y la caustica."""
    y_obj = -30.0
    parab = lente_biconvexa(10, 10, 2.0, 1.5, -1.0, -1.0)
    esfer = lente_biconvexa(10, 10, 2.0, 1.5, 0.0, 0.0)
    h_max = 0.9 * min(parab.semiapertura, esfer.semiapertura)
    hs = np.linspace(0.02, h_max, 90)

    fig = plt.figure(figsize=(11, 8.6))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 0.9], hspace=0.45, wspace=0.26,
                          left=0.07, right=0.98, top=0.91, bottom=0.095)
    axa, axb, axc = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, :])

    # (a) longitudinal: trazado exacto frente a tercer orden
    axa.axhline(0, color=EJE, lw=0.8, zorder=1)
    for nombre, L, color in (("parabólicas", parab, AZUL), ("esféricas", esfer, NARANJA)):
        axa.plot(hs, aberracion_longitudinal(L, y_obj, hs), color=color, lw=2.2, zorder=3,
                 label=f"caras {nombre}: trazado exacto")
        axa.plot(hs, coeficiente_esferica(L, y_obj) * hs**2, color=color, lw=1.2, ls=(0, (4, 3)), zorder=3,
                 label=f"caras {nombre}: tercer orden (Seidel)")
    axa.set_xlabel("altura h a la que el rayo entra en la lente")
    axa.set_ylabel("Δy = cruce con el eje - imagen paraxial")
    axa.set_title("(a) Trazado exacto y teoría de tercer orden", loc="left", fontsize=10)
    axa.grid(True, color=REJILLA, lw=0.6)
    axa.legend(frameon=False, loc="lower left", fontsize=8, labelcolor=TINTA_2)

    # (b) aberracion transversal de la lente parabolica
    focos = mejores_focos(parab, y_obj, h_max)
    hh = np.linspace(-h_max, h_max, 181)
    ab = abanico(parab, y_obj, hh)
    axb.axhline(0, color=EJE, lw=0.8, zorder=1)
    axb.axvline(0, color=EJE, lw=0.8, zorder=1)
    axb.plot(hh, ab.x_en(focos.y_paraxial), color=AZUL, lw=1.4, ls=(0, (4, 3)), zorder=3,
             label=f"en el plano paraxial (y = {focos.y_paraxial:.2f})")
    axb.plot(hh, ab.x_en(focos.y_rms), color=AZUL, lw=2.2, zorder=3,
             label=f"en el plano de mejor foco (y = {focos.y_rms:.2f})")
    axb.set_xlabel("altura h a la que el rayo entra en la lente")
    axb.set_ylabel("altura x al llegar al plano")
    axb.set_title("(b) Aberración transversal (caras parabólicas)", loc="left", fontsize=10)
    axb.grid(True, color=REJILLA, lw=0.6)
    axb.legend(frameon=False, loc="upper right", fontsize=8, labelcolor=TINTA_2)

    # (c) caustica cerca del foco, vista girada
    a_fan = h_max
    y_fin = focos.y_paraxial + 1.0
    for h in np.linspace(-a_fan, a_fan, 41):
        tr = trazar(parab, *_rayo_eje(parab, y_obj, h))
        if tr.estado == "ok":
            dibujar_trayectoria(axc, tr, y_final=y_fin, color=color_por_altura(h, a_fan), lw=0.8)
    axc.axhline(0, color=EJE, lw=0.8, zorder=0)
    caja = dict(boxstyle="round,pad=0.18", fc=SUPERFICIE, ec="none", alpha=0.92)
    axc.plot(focos.y_paraxial, 0, "o", mfc=SUPERFICIE, mec=TINTA, ms=7, mew=1.4, zorder=6)
    axc.plot(focos.y_marginal, 0, "o", color=TINTA, ms=5.5, zorder=6)
    axc.plot(focos.y_rms, 0, "D", color=TINTA, ms=5.5, zorder=6)
    axc.plot([focos.y_circulo] * 2, [-focos.radio_circulo, focos.radio_circulo], color=TINTA, lw=2.2,
             solid_capstyle="butt", zorder=6)
    for y, x, texto, dy in ((focos.y_paraxial, 0, "foco paraxial", 16),
                            (focos.y_marginal, 0, "foco del rayo\nmás alejado", 16),
                            (focos.y_rms, 0, f"mejor foco\n(radio RMS {focos.rms:.2f})", -38),
                            (focos.y_circulo, focos.radio_circulo,
                             f"círculo de mínima confusión\n(radio {focos.radio_circulo:.2f})", 12)):
        axc.annotate(texto, (y, x), xytext=(0, dy), textcoords="offset points", ha="center",
                     color=TINTA, fontsize=8.5, bbox=caja, zorder=7)
    axc.set_xlim(focos.y_marginal - 0.7, focos.y_paraxial + 0.9)
    axc.set_ylim(-0.6, 0.6)
    axc.set_aspect("equal")
    axc.set_xlabel("y  (eje óptico; la luz avanza en +y)")
    axc.set_ylabel("x")
    axc.set_title("(c) Cáustica cerca del foco (caras parabólicas): la mancha más chica no está en el foco paraxial",
                  loc="left", fontsize=10)

    fig.suptitle("Aberración esférica: los rayos que entran lejos del eje enfocan antes",
                 x=0.03, ha="left", fontsize=11.5, color=TINTA, y=0.985)
    fig.text(0.03, 0.015, "Lente biconvexa con R = 10, espesor 2 y n = 1.5; objeto sobre el eje en y = -30. "
             "El radio RMS supone una pupila circular de radio 3.92.", ha="left", fontsize=8.5, color=TINTA_2)
    return fig


def _rayo_eje(lente, y_obj, h):
    P = np.array([0.0, y_obj])
    return P, rayo_hacia(lente, P, h)


@figura("fig04_forma_y_asfericas")
def forma_y_asfericas():
    """Extras: forma optima de la lente (bending) y caras conicas que anulan el tercer orden."""
    fig, (axa, axb) = plt.subplots(1, 2, figsize=(11, 4.9))
    fig.subplots_adjust(left=0.07, right=0.98, top=0.82, bottom=0.2, wspace=0.32)

    # (a) forma de la lente, misma focal, objeto en el infinito
    qs = np.linspace(-1.0, 1.0, 161)
    curvas = {}
    for d in (2.0, 1e-4):
        curvas[d] = np.array([abs(coeficiente_esferica(lente_con_forma(q, 10.0, d), None)) for q in qs])
    optimos = {d: minimize_scalar(lambda q: abs(coeficiente_esferica(lente_con_forma(q, 10.0, d), None)),
                                  bounds=(0.2, 0.95), method="bounded", options={"xatol": 1e-6}).x
               for d in (2.0, 1e-4)}
    axa.plot(qs, curvas[1e-4], color=TENUE, lw=1.3, ls=(0, (4, 3)), label="lente delgada (teoría)", zorder=2)
    axa.plot(qs, curvas[2.0], color=TINTA_2, lw=2.2, label="nuestra lente, d = 2 (teoría de tercer orden)", zorder=3)
    q_puntos = np.array([-1.0, -0.5, 0.0, 0.5, optimos[2.0], 1.0])
    medidos = [abs(coeficiente_esferica_trazado(lente_con_forma(q, 10.0, 2.0), None)) for q in q_puntos]
    axa.plot(q_puntos, medidos, "o", color=TINTA, ms=6, label="trazado exacto", zorder=4)
    tope = curvas[2.0].max()
    for d in (2.0, 1e-4):
        axa.axvline(optimos[d], color=TENUE, lw=0.8, ls=(0, (1, 2)), zorder=1)
    axa.annotate(f"óptimo con d = 2: q = {optimos[2.0]:.2f}", (optimos[2.0], 0.79 * tope), xytext=(-6, 0),
                 textcoords="offset points", ha="right", color=TINTA_2, fontsize=8.5)
    axa.annotate(f"óptimo de lente delgada: q = {optimos[1e-4]:.3f}", (optimos[2.0], 0.71 * tope),
                 xytext=(-6, 0), textcoords="offset points", ha="right", color=TENUE, fontsize=8.5)
    for q, texto in ((-1.0, "cara plana\nhacia la luz"), (0.0, "simétrica"), (1.0, "cara curva\nhacia la luz")):
        axa.annotate(texto, (q, 0), xytext=(0, -30), textcoords="offset points", ha="center", va="top",
                     color=TINTA_2, fontsize=8, annotation_clip=False)
    axa.set_ylim(0, tope * 1.08)
    axa.set_xlabel("factor de forma q", labelpad=30)
    axa.set_ylabel("|Δy| de un rayo que entra a h = 1")
    axa.set_title("(a) Forma de la lente con la misma focal (f = 10, objeto lejano)", loc="left", fontsize=10)
    axa.grid(True, color=REJILLA, lw=0.6)
    axa.legend(frameon=False, loc="upper right", fontsize=8, labelcolor=TINTA_2)

    # (b) forma de las caras: esfera, parabola y la conica que anula el tercer orden
    y_obj = -30.0
    k_cero = k_que_anula(lente_biconvexa(10, 10, 2.0, 1.5, 0.0, 0.0), y_obj)
    casos = (("esfera (k = 0)", 0.0, NARANJA), ("parábola (k = -1)", -1.0, AZUL),
             (f"cónica que anula el tercer orden (k = {k_cero:.2f})", k_cero, AQUA))
    lentes_k = [(nombre, lente_biconvexa(10, 10, 2.0, 1.5, k, k), color) for nombre, k, color in casos]
    h_max = 0.9 * min(L.semiapertura for _, L, _ in lentes_k)
    hs = np.linspace(0.02, h_max, 90)
    axb.axhline(0, color=EJE, lw=0.8, zorder=1)
    finales = {}
    for nombre, L, color in lentes_k:
        dy = aberracion_longitudinal(L, y_obj, hs)
        finales[nombre] = dy[-1]
        axb.plot(hs, dy, color=color, lw=2.2, label=nombre, zorder=3)
    d_esf, d_k = finales[casos[0][0]], finales[casos[2][0]]
    axb.text(0.1, -1.9, f"Con la cónica adecuada, a h = {hs[-1]:.1f}:\nΔy = {d_k:.3f}, "
             f"{d_esf / d_k:.0f} veces menos que la esfera", ha="left", va="top", color=TINTA_2, fontsize=8.5)
    axb.set_xlabel("altura h a la que el rayo entra en la lente")
    axb.set_ylabel("Δy (cruce con el eje - paraxial)")
    axb.set_title("(b) Forma de las caras (lente simétrica, objeto en y = -30)", loc="left", fontsize=10)
    axb.grid(True, color=REJILLA, lw=0.6)
    axb.legend(frameon=False, loc="lower left", fontsize=8, labelcolor=TINTA_2)

    fig.suptitle("Cómo se reduce la aberración esférica: forma de la lente y caras asféricas",
                 x=0.03, ha="left", fontsize=11.5, color=TINTA, y=0.98)
    return fig


URL_SIMULADOR = "https://oswaldoaqm.github.io/Proyecto-Opticas/"


@figura("fig05_qr_simulador")
def qr_simulador():
    """Codigo QR de la pagina web del simulador, para el poster (vectorial en el SVG)."""
    import segno
    from matplotlib.patches import PathPatch, Rectangle
    from matplotlib.path import Path as Trazo

    matriz = np.array([[bool(v) for v in fila] for fila in segno.make(URL_SIMULADOR, error="q", micro=False).matrix])
    n, borde, solape = matriz.shape[0], 4, 0.02   # el solape evita rendijas blancas entre modulos al imprimir
    vertices, codigos = [], []
    for i, fila in enumerate(matriz):
        y, j = n - 1 - i, 0
        while j < n:
            if not fila[j]:
                j += 1
                continue
            k = j
            while k < n and fila[k]:
                k += 1
            x0, x1, y0, y1 = j - solape, k + solape, y - solape, y + 1 + solape
            vertices += [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
            codigos += [Trazo.MOVETO, Trazo.LINETO, Trazo.LINETO, Trazo.LINETO, Trazo.CLOSEPOLY]
            j = k

    fig = plt.figure(figsize=(3.2, 3.95))
    ax = fig.add_axes([0.0, 0.19, 1.0, 0.81])
    ax.add_patch(Rectangle((-borde, -borde), n + 2 * borde, n + 2 * borde, color="#ffffff", zorder=0))
    ax.add_patch(PathPatch(Trazo(vertices, codigos), facecolor=TINTA, edgecolor="none", zorder=1))
    ax.set_xlim(-borde, n + borde)
    ax.set_ylim(-borde, n + borde)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.text(0.5, 0.115, "Simulación interactiva", ha="center", fontsize=12, color=TINTA, weight="bold")
    fig.text(0.5, 0.045, URL_SIMULADOR.removeprefix("https://").rstrip("/"), ha="center", fontsize=8.5,
             color=TINTA_2, family="monospace")
    return fig


@figura("fig06_frente_de_onda_difraccion")
def frente_de_onda_difraccion():
    """Extra 5: error del frente de onda (Fermat) y cuando la lente esta limitada por difraccion."""
    from matplotlib.colors import LinearSegmentedColormap, PowerNorm
    from matplotlib.ticker import NullFormatter

    from lentes.difraccion import (
        LAMBDA_VERDE,
        MARECHAL,
        apertura_cruce,
        apertura_limite,
        haz,
        mejor_foco_onda,
        psf,
        radio_airy,
        radio_rms_geometrico,
        strehl,
    )

    lam, y_obj = LAMBDA_VERDE, -30.0
    k_cero = k_que_anula(lente_biconvexa(10, 10, 2.0, 1.5, 0.0, 0.0), y_obj)
    casos = (("esfera", 0.0, NARANJA), ("parábola", -1.0, AZUL), ("asférica", k_cero, AQUA))
    haces = [(nombre, haz(lente_biconvexa(10, 10, 2.0, 1.5, k, k), y_obj), color) for nombre, k, color in casos]
    parab = haces[1][1]
    h_tope = min(hz.h_tope for _, hz, _ in haces)
    hl = np.geomspace(0.15, h_tope, 50)
    numero = FuncFormatter(lambda v, _: f"{v:g}")

    def ejes_log(ax, yticks):
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(hl[0], hl[-1])
        ax.set_xticks([0.2, 0.5, 1, 2, 4])
        ax.set_yticks(yticks)
        for eje in (ax.xaxis, ax.yaxis):
            eje.set_major_formatter(numero)
            eje.set_minor_formatter(NullFormatter())
        ax.set_xlabel("h_max: radio de la apertura (mm)")
        ax.grid(True, which="major", color=REJILLA, lw=0.6)

    fig = plt.figure(figsize=(11, 8.6))
    gs = fig.add_gridspec(2, 2, hspace=0.5, wspace=0.27, left=0.07, right=0.97, top=0.9, bottom=0.07)
    axa, axb, axc = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, 0])
    sub = gs[1, 1].subgridspec(1, 3, wspace=0.08)
    axd = [fig.add_subplot(sub[0, i]) for i in range(3)]

    # (a) W(rho) de la parabola con h_max = 2: referencia en la imagen paraxial y en el mejor foco
    h_a = 2.0
    foco = mejor_foco_onda(parab, h_a)
    rho = np.linspace(0, 1, 301)
    W_par = parab.frente_de_onda(rho * h_a, foco.y_paraxial) / lam
    W_mej = parab.frente_de_onda(rho * h_a, foco.y_ref) / lam
    axa.axhline(0, color=EJE, lw=0.8, zorder=1)
    axa.plot(rho, W_par, color=AZUL, lw=1.5, ls=(0, (4, 3)), zorder=3)
    axa.plot(rho, W_mej, color=AZUL, lw=2.2, zorder=3)
    i = 255
    axa.annotate(f"referencia en la imagen paraxial\nW_rms = {foco.rms_paraxial / lam:.2f} λ", (rho[i], W_par[i]),
                 xytext=(-10, 0), textcoords="offset points", ha="right", va="center", color=TINTA_2, fontsize=8.5)
    j = int(np.argmin(W_mej))
    axa.annotate(f"referencia en el mejor foco\nW_rms = {foco.rms / lam:.2f} λ", (rho[j], W_mej[j]),
                 xytext=(0, -8), textcoords="offset points", ha="center", va="top", color=TINTA_2, fontsize=8.5)
    axa.set_xlim(0, 1.0)
    axa.set_ylim(-2.2, 5.0)
    axa.set_xlabel("ρ = h / h_max (posición en la pupila)")
    axa.set_ylabel("W (longitudes de onda)")
    axa.set_title(f"(a) Error del frente de onda: parábola, h_max = {h_a:g} mm", loc="left", fontsize=10)
    axa.grid(True, color=REJILLA, lw=0.6)

    # (b) W_rms en el mejor foco segun la apertura, con el limite de Marechal
    axb.axhline(MARECHAL, color=TENUE, lw=1.0, ls=(0, (4, 3)), zorder=1)
    axb.annotate("límite de Maréchal: λ/14 (Strehl 0.8)", (hl[0], MARECHAL), xytext=(4, -4),
                 textcoords="offset points", ha="left", va="top", color=TINTA_2, fontsize=8.5)
    for (nombre, hz, color), (dx, dy, ha, va) in zip(haces, ((-8, 6, "right", "bottom"), (8, -6, "left", "top"),
                                                            (-8, 6, "right", "bottom"))):
        s = np.array([mejor_foco_onda(hz, h).rms / lam for h in hl])
        axb.plot(hl, s, color=color, lw=2.2, zorder=3)
        h_lim = apertura_limite(hz)
        axb.plot(h_lim, MARECHAL, "o", color=color, ms=7, mec=SUPERFICIE, mew=1.5, zorder=4)
        axb.annotate(f"{nombre}: {h_lim:.2f} mm", (h_lim, MARECHAL), xytext=(dx, dy), textcoords="offset points",
                     ha=ha, va=va, color=TINTA_2, fontsize=8.5)
    axb.annotate("~ h⁴", (0.62, mejor_foco_onda(parab, 0.62).rms / lam), xytext=(6, -10), textcoords="offset points",
                 color=TINTA_2, fontsize=9)
    axb.annotate("~ h⁶", (2.0, mejor_foco_onda(haces[2][1], 2.0).rms / lam), xytext=(6, -10),
                 textcoords="offset points", color=TINTA_2, fontsize=9)
    ejes_log(axb, [1e-4, 1e-3, 1e-2, 0.1, 1, 10])
    axb.set_ylim(1e-4, 30)
    axb.set_ylabel("W_rms en el mejor foco (longitudes de onda)")
    axb.set_title("(b) ¿Hasta qué apertura manda la difracción?", loc="left", fontsize=10)

    # (c) mancha geometrica frente al disco de Airy
    airy = np.array([radio_airy(parab, h) * 1e3 for h in hl])
    axc.plot(hl, airy, color=TINTA_2, lw=1.6, ls=(0, (4, 3)), zorder=3)
    axc.annotate("disco de Airy: 0.61 λ / NA", (hl[4], airy[4]), xytext=(2, 6), textcoords="offset points",
                 ha="left", va="bottom", color=TINTA_2, fontsize=8.5)
    for nombre, hz, color in haces:
        geo = np.array([radio_rms_geometrico(hz, h) * 1e3 for h in hl])
        axc.plot(hl, geo, color=color, lw=2.2, zorder=3)
        h_c = apertura_cruce(hz)
        axc.plot(h_c, radio_airy(hz, h_c) * 1e3, "o", color=color, ms=7, mec=SUPERFICIE, mew=1.5, zorder=4)
        k = min(int(np.searchsorted(geo, 40 if nombre != "asférica" else 0.12)), len(hl) - 1)
        arriba = nombre != "parábola"
        axc.annotate(nombre, (hl[k], geo[k]), xytext=(-6, 3) if arriba else (6, -3), textcoords="offset points",
                     ha="right" if arriba else "left", va="bottom" if arriba else "top", color=TINTA_2, fontsize=8.5)
    ejes_log(axc, [0.1, 1, 10, 100])
    axc.set_ylim(0.05, 600)
    axc.set_ylabel("radio de la mancha (μm)")
    axc.set_title("(c) Mancha geométrica (~ h³) frente al disco de Airy (~ 1/h)", loc="left", fontsize=10)

    # (d) imagen de un punto en el mejor foco de la parabola, para tres aperturas
    mapa = LinearSegmentedColormap.from_list("intensidad", [SUPERFICIE, "#86b6ef", "#3987e5", "#1c5cab", "#104281"])
    lado = 16.0  # um
    xs = np.linspace(-lado, lado, 241)
    X, Y = np.meshgrid(xs, xs)
    radios = np.linspace(0, lado * np.sqrt(2), 600)
    for ax, h in zip(axd, (0.8, apertura_limite(parab), 2.0)):
        f = mejor_foco_onda(parab, h)
        perfil = psf(parab, h, f.y_ref, radios * 1e-3)
        imagen = np.interp(np.hypot(X, Y), radios, perfil)
        ax.imshow(imagen / imagen.max(), extent=(-lado, lado, -lado, lado), origin="lower", cmap=mapa,
                  norm=PowerNorm(gamma=0.5, vmin=0, vmax=1), interpolation="bilinear")
        ax.add_patch(plt.Circle((0, 0), radio_airy(parab, h) * 1e3, fill=False, ec=TINTA_2, lw=0.8, ls=(0, (2, 2))))
        ax.set_title(f"h = {h:.2f} mm\nStrehl {strehl(parab, h, f.y_ref):.2f}", fontsize=9, color=TINTA)
        ax.set_xticks([-10, 0, 10])
        ax.set_yticks([])
        ax.tick_params(labelsize=8)
    axd[1].set_xlabel("μm  (círculo: radio de Airy)", fontsize=8.5)
    axd[0].annotate("(d) Imagen de un punto en el mejor foco (parábola)", (0, 1), xycoords="axes fraction",
                    xytext=(0, 34), textcoords="offset points", ha="left", va="bottom", fontsize=10, color=TINTA)

    fig.suptitle("Extra 5 - frente de onda y límite de difracción (λ = 550 nm, longitudes en mm, objeto en y = -30)",
                 x=0.03, ha="left", fontsize=11.5, color=TINTA, y=0.985)
    return fig


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Regenera las figuras del proyecto en figuras/.")
    parser.add_argument("nombres", nargs="*", help="figuras a generar (por defecto, todas)")
    parser.add_argument("--lista", action="store_true", help="solo lista las figuras disponibles")
    args = parser.parse_args(argv)

    if args.lista:
        for nombre in FIGURAS:
            print(nombre)
        return 0
    desconocidas = [n for n in args.nombres if n not in FIGURAS]
    if desconocidas:
        print("Figuras desconocidas:", ", ".join(desconocidas), file=sys.stderr)
        return 1

    aplicar_estilo()
    for nombre in args.nombres or list(FIGURAS):
        fig = FIGURAS[nombre]()
        rutas = guardar_figura(fig, CARPETA / nombre)
        plt.close(fig)
        print("ok:", ", ".join(str(r.relative_to(RAIZ)).replace("\\", "/") for r in rutas))
    return 0


if __name__ == "__main__":
    sys.exit(main())
