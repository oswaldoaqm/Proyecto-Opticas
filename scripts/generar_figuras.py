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

from lentes import (  # noqa: E402
    cruce_con_eje,
    imagen_lente_delgada,
    imagen_paraxial,
    lente_biconvexa,
    rayo_hacia,
    trazar,
)
from lentes.estilo import (  # noqa: E402
    AZUL,
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
    axb.set_ylabel("Δy = cruce con el eje − imagen paraxial")
    axb.set_title("(b) Aberración esférica: cuanto más lejos del eje, antes enfoca el rayo",
                  loc="left", fontsize=10)
    axb.grid(True, color=REJILLA, lw=0.6)
    axb.legend(frameon=False, loc="lower left", fontsize=8.5, labelcolor=TINTA_2)

    fig.suptitle("Boceto del Grupo 1 — trazado vectorial en una lente biconvexa gruesa "
                 f"(R = {R:g}, espesor = {espesor:g}, objeto en y = {yP:g})",
                 x=0.06, ha="left", fontsize=11.5, color=TINTA, y=0.995)
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
