"""Figuras del poster a tamano final y exportacion del poster a PDF y PNG (decision 0008).

Uso (desde la raiz del repo):
    python poster/generar_poster.py              # figuras y, si hay Playwright, poster.pdf y poster.png
    python poster/generar_poster.py --figuras    # solo las figuras (lo que corre el CI)

El poster es poster/poster.html, en tamano real: A0 horizontal, 1189 x 841 mm. Cada figura
se dibuja al ancho de una columna (343 mm) con textos de 24 pt o mas, para que se lea a 2 m.
Como en la decision 0005, ninguna figura se edita a mano.

Para exportar hace falta Playwright (pip install playwright y luego playwright install
chromium). Sin Playwright: abrir poster.html en Chrome o Edge, Imprimir, Guardar como PDF;
el tamano de hoja lo fija el propio archivo.
"""
from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib as mpl  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.patches import Arc  # noqa: E402
from matplotlib.ticker import FuncFormatter, NullFormatter  # noqa: E402

from lentes import lente_biconvexa, rayo_hacia, trazar  # noqa: E402
from lentes.aberraciones import aberracion_longitudinal, mejores_focos, y_paraxial  # noqa: E402
from lentes.difraccion import LAMBDA_VERDE, MARECHAL, apertura_limite, haz, mejor_foco_onda  # noqa: E402
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
)
from lentes.graficos import dibujar_lente, dibujar_trayectoria  # noqa: E402
from lentes.seidel import coeficiente_esferica, k_que_anula  # noqa: E402

CARPETA = Path(__file__).resolve().parent
FIGURAS = CARPETA / "figuras"
ANCHO = 343 / 25.4          # pulgadas: el ancho util de una columna del poster
URL_SIMULADOR = "https://oswaldoaqm.github.io/Proyecto-Opticas/"

# La lente de trabajo, como en el resto del proyecto (medidas en mm).
Y_OBJ = -30.0
PARABOLA = lente_biconvexa(10, 10, 2.0, 1.5, -1.0, -1.0)
ESFERA = lente_biconvexa(10, 10, 2.0, 1.5, 0.0, 0.0)
K0 = k_que_anula(ESFERA, Y_OBJ)
CONICA = lente_biconvexa(10, 10, 2.0, 1.5, K0, K0)
H_MAX = 0.9 * min(PARABOLA.semiapertura, ESFERA.semiapertura)   # la pupila completa: 3.92


def familias() -> list[str]:
    """Arial (o Liberation Sans, con sus mismas medidas, donde no esta) y DejaVu Sans de respaldo.

    matplotlib toma de la siguiente fuente de la lista los caracteres que le faltan a la
    primera. Arial no tiene el subindice de k0: sin respaldo, en Windows saldria un recuadro.
    """
    instaladas = {f.name for f in font_manager.fontManager.ttflist}
    return [f for f in ("Arial", "Liberation Sans") if f in instaladas][:1] + ["DejaVu Sans"]


def estilo_poster() -> None:
    """El estilo del proyecto con tamanos de poster: nada por debajo de 24 pt."""
    aplicar_estilo()
    mpl.rcParams.update({
        "font.family": familias(),
        "font.sans-serif": ["Arial", "Liberation Sans", "DejaVu Sans"],
        "font.size": 26,
        "axes.labelsize": 26,
        "xtick.labelsize": 24,
        "ytick.labelsize": 24,
        "legend.fontsize": 24,
        "axes.linewidth": 1.6,
        "xtick.major.width": 1.6,
        "ytick.major.width": 1.6,
        "xtick.major.size": 8,
        "ytick.major.size": 8,
        "xtick.minor.size": 4,
        "ytick.minor.size": 4,
        "axes.labelpad": 10,
        "lines.linewidth": 4,
        "axes.unicode_minus": False,
        "svg.fonttype": "path",
        "figure.facecolor": "#ffffff",   # el fondo de las cajas del poster
        "axes.facecolor": "#ffffff",
        "savefig.facecolor": "#ffffff",
    })


def guardar(fig, nombre: str) -> Path:
    """SVG sin fecha, con saltos LF y al tamano exacto de la figura (sin recortes), para que
    en el poster el texto quede del tamano con que se dibujo."""
    FIGURAS.mkdir(parents=True, exist_ok=True)
    ruta = FIGURAS / f"{nombre}.svg"
    datos = io.BytesIO()
    fig.savefig(datos, format="svg", metadata={"Date": None, "Creator": None})
    ruta.write_bytes(datos.getvalue().replace(b"\r\n", b"\n"))
    plt.close(fig)
    return ruta


def _rayo(lente, h):
    P = np.array([0.0, Y_OBJ])
    return trazar(lente, P, rayo_hacia(lente, P, h))


def abanico():
    """Introduccion: rayos de P a traves de la lente; los del borde cruzan el eje antes."""
    fig = plt.figure(figsize=(ANCHO, 4.7))
    ax = fig.add_axes([0.0, 0.02, 1.0, 0.96])
    y_par = y_paraxial(PARABOLA, Y_OBJ)
    y_fin = 21.5
    dibujar_lente(ax, PARABOLA, borde=TINTA_2)
    ax.axhline(0, color=EJE, lw=1.4, zorder=0)
    a = 0.9 * PARABOLA.semiapertura
    for h in np.linspace(-a, a, 17):
        dibujar_trayectoria(ax, _rayo(PARABOLA, h), y_final=y_fin, color=color_por_altura(h, a), lw=2.2)
    y_borde = float(aberracion_longitudinal(PARABOLA, Y_OBJ, [a])[0]) + y_par
    ax.plot(Y_OBJ, 0, "o", color=TINTA, ms=13, zorder=5)
    ax.plot(y_par, 0, "o", mfc=SUPERFICIE, mec=TINTA, mew=3, ms=15, zorder=6)
    ax.plot(y_borde, 0, "o", color=RAMPA_AZUL[-1], ms=12, zorder=6)
    texto = dict(fontsize=26, color=TINTA)
    ax.annotate("P", (Y_OBJ, 0), xytext=(0, 18), textcoords="offset points", ha="center", **texto)
    ax.annotate("lente gruesa", (0, PARABOLA.semiapertura), xytext=(0, 10), textcoords="offset points",
                ha="center", va="bottom", **texto)
    linea = dict(arrowstyle="-", color=TINTA_2, lw=1.6, shrinkA=2, shrinkB=10)
    ax.annotate("foco paraxial", (y_par, 0), xytext=(0, 78), textcoords="offset points", ha="center",
                va="center", arrowprops=linea, **texto)
    ax.annotate("los rayos del borde\ncruzan antes", (y_borde, 0), xytext=(-10, -110), textcoords="offset points",
                ha="center", va="center", arrowprops=linea, **texto)
    ax.set_xlim(Y_OBJ - 1.5, y_fin)
    ax.set_ylim(-7.4, 7.4)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig


def _girar(v):
    return np.array([v[1], v[0]], dtype=float)


def _flecha(ax, origen, vector, color, lw, z=6):
    o, v = _girar(origen), _girar(vector)
    ax.annotate("", xy=o + v, xytext=o, zorder=z,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, shrinkA=0, shrinkB=0, mutation_scale=34))


def refraccion():
    """Metodologia: la construccion vectorial en la cara de entrada."""
    tr = _rayo(PARABOLA, 3.0)
    Q, u_in, u_out, det = tr.puntos[1], tr.direcciones[0], tr.direcciones[1], tr.detalles[0]
    t_hat, n_usada = PARABOLA.abajo.tangente(Q[0]), det.normal
    fig = plt.figure(figsize=(ANCHO, 5.0))
    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
    dibujar_lente(ax, PARABOLA, borde=TINTA_2)
    for v, estilo in ((t_hat, (0, (6, 4))), (n_usada, (0, (1.5, 3)))):
        a, b = _girar(Q - 1.6 * v), _girar(Q + 1.6 * v)
        ax.plot([a[0], b[0]], [a[1], b[1]], color=TENUE, lw=2, ls=estilo, zorder=2)
    for inicio, d in ((Q - 1.05 * u_in, u_in), (Q, u_out)):
        a, b = _girar(inicio), _girar(inicio + 1.05 * d)
        ax.plot([a[0], b[0]], [a[1], b[1]], color=AZUL, lw=5, zorder=4, solid_capstyle="round")
        _flecha(ax, inicio + 0.42 * d, 0.14 * d, AZUL, lw=5, z=4)
    _flecha(ax, Q, 0.6 * n_usada, TINTA, lw=4.5, z=7)
    _flecha(ax, Q, 0.42 * t_hat, TINTA_2, lw=3, z=6)

    def arco(v1, v2, r, texto, factor):
        c = _girar(Q)
        a1 = np.degrees(np.arctan2(*_girar(v1)[::-1]))
        a2 = np.degrees(np.arctan2(*_girar(v2)[::-1]))
        d = (a2 - a1 + 180.0) % 360.0 - 180.0
        t1, t2 = (a1, a1 + d) if d >= 0 else (a1 + d, a1)
        ax.add_patch(Arc(c, 2 * r, 2 * r, theta1=t1, theta2=t2, color=TINTA, lw=2.4, zorder=5))
        m = np.radians(0.5 * (t1 + t2))
        ax.text(c[0] + factor * r * np.cos(m), c[1] + factor * r * np.sin(m), texto, ha="center", va="center",
                fontsize=28, color=TINTA, zorder=7)

    arco(n_usada, -u_in, 0.42, "$\\theta_i$", 1.45)
    arco(-n_usada, u_out, 0.42, "$\\theta_t$", 1.45)
    caja = dict(boxstyle="round,pad=0.2", fc=SUPERFICIE, ec="none", alpha=0.92)
    for punto, texto, color, ha, va in (
            (Q + 0.66 * n_usada, "normal $\\hat n$\n(hacia la luz que llega)", TINTA, "right", "bottom"),
            (Q + 0.36 * t_hat, "tangente $\\hat t$  ", TINTA_2, "right", "center"),
            (Q - 0.95 * u_in, "rayo $\\hat u$", AZUL, "center", "top"),
            (Q + 0.95 * u_out, "refractado $\\hat u_t$", AZUL, "center", "top")):
        p = _girar(punto)
        ax.text(p[0], p[1] - (0.08 if va == "top" else 0), texto, color=color, fontsize=26, ha=ha, va=va,
                bbox=caja, zorder=8)
    ax.text(0.02, 0.95, "aire, n = 1", transform=ax.transAxes, ha="left", va="top", fontsize=26, color=TINTA_2)
    ax.text(0.98, 0.95, "vidrio, n = 1.5", transform=ax.transAxes, ha="right", va="top", fontsize=26,
            color=TINTA_2)
    c = _girar(Q)
    ax.set_xlim(c[0] - 1.75, c[0] + 1.75)
    ax.set_ylim(c[1] - 0.65, c[1] + 0.65)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig


def aberracion():
    """Resultados 1: donde cruza cada rayo segun la altura a la que entra."""
    fig = plt.figure(figsize=(ANCHO, 4.8))
    ax = fig.add_axes([0.17, 0.215, 0.6, 0.755])
    hs = np.linspace(0.02, H_MAX, 120)
    y_par = y_paraxial(PARABOLA, Y_OBJ)
    ax.axhline(0, color=EJE, lw=1.6, zorder=1)
    ax.axhline(-0.01 * y_par, color=TENUE, lw=2, ls=(0, (1.5, 3)), zorder=1)
    ax.text(1.95, -0.01 * y_par - 0.06, "1 % de la distancia imagen", color=TINTA_2, fontsize=24, va="top")
    for nombre, lente, color in (("esfera", ESFERA, NARANJA), ("parábola", PARABOLA, AZUL),
                                 (f"cónica k₀ = {K0:.2f}", CONICA, AQUA)):
        dy = aberracion_longitudinal(lente, Y_OBJ, hs)
        ax.plot(hs, dy, color=color, lw=4.5, zorder=3)
        if lente is not CONICA:
            ax.plot(hs, coeficiente_esferica(lente, Y_OBJ) * hs**2, color=color, lw=2.4, ls=(0, (5, 3)), zorder=3)
        ax.annotate(nombre, (hs[-1], dy[-1]), xytext=(14, 0), textcoords="offset points", ha="left", va="center",
                    color=TINTA, fontsize=26, annotation_clip=False)
    ax.plot([], [], color=TINTA_2, lw=4.5, label="trazado exacto")
    ax.plot([], [], color=TINTA_2, lw=2.4, ls=(0, (5, 3)), label="teoría de Seidel")
    ax.legend(frameon=False, loc="lower left", labelcolor=TINTA_2, handlelength=2.6)
    ax.set_xlim(0, 4.05)
    ax.set_ylim(-4.6, 0.35)
    ax.set_xlabel("altura h a la que entra el rayo (mm)")
    ax.set_ylabel("Δy: dónde cruza el eje,\ndesde la paraxial (mm)")
    ax.grid(True, color=REJILLA, lw=1.2)
    return fig


def mancha():
    """Resultados 2: la caustica cerca del foco y los planos de "mejor foco"."""
    f = mejores_focos(PARABOLA, Y_OBJ, H_MAX)
    fig = plt.figure(figsize=(ANCHO, 4.35))
    ax = fig.add_axes([0.01, 0.255, 0.98, 0.735])
    y_fin = f.y_paraxial + 1.2
    for h in np.linspace(-H_MAX, H_MAX, 41):
        dibujar_trayectoria(ax, _rayo(PARABOLA, h), y_final=y_fin, color=color_por_altura(h, H_MAX), lw=1.6)
    ax.axhline(0, color=EJE, lw=1.4, zorder=0)
    ax.plot([f.y_circulo] * 2, [-f.radio_circulo, f.radio_circulo], color=TINTA, lw=5, solid_capstyle="butt",
            zorder=6)
    ax.plot(f.y_paraxial, 0, "o", mfc=SUPERFICIE, mec=TINTA, mew=3, ms=17, zorder=7)
    ax.plot(f.y_rms, 0, "D", color=TINTA, ms=14, zorder=7)
    ax.plot(f.y_marginal, 0, "o", color=TINTA, ms=13, zorder=7)
    caja = dict(boxstyle="round,pad=0.2", fc=SUPERFICIE, ec="none", alpha=0.94)
    linea = dict(arrowstyle="-", color=TINTA_2, lw=1.6, shrinkA=0, shrinkB=8)
    for y, x, texto, desplazamiento, ha in (
            (f.y_marginal, 0, "foco del borde", (0, 62), "center"),
            (f.y_circulo, -f.radio_circulo, "círculo de mínima\nconfusión (3/4)", (-60, -62), "center"),
            (f.y_rms, 0, "mancha más chica\n(2/3 del camino)", (170, -86), "center"),
            (f.y_paraxial, 0, "foco paraxial", (0, 62), "center")):
        ax.annotate(texto, (y, x), xytext=desplazamiento, textcoords="offset points", ha=ha, va="center",
                    color=TINTA, fontsize=26, bbox=caja, zorder=8, arrowprops=linea)
    ax.set_xlim(f.y_marginal - 0.75, f.y_paraxial + 1.0)
    ax.set_ylim(-0.62, 0.62)
    ax.set_aspect("equal")
    ax.set_yticks([])
    for lado in ("left", "right", "top"):
        ax.spines[lado].set_visible(False)
    ax.set_xlabel("posición sobre el eje óptico (mm)")
    return fig


def difraccion():
    """Resultados 3: error del frente de onda segun el diametro de la apertura, con el limite
    de Marechal (lambda = 550 nm)."""
    lam = LAMBDA_VERDE
    haces = [("esfera", haz(ESFERA, Y_OBJ), NARANJA), ("parábola", haz(PARABOLA, Y_OBJ), AZUL),
             ("cónica k₀", haz(CONICA, Y_OBJ), AQUA)]
    tope = min(hz.h_tope for _, hz, _ in haces)
    hl = np.geomspace(0.2, tope, 40)
    fig = plt.figure(figsize=(ANCHO, 4.8))
    ax = fig.add_axes([0.17, 0.215, 0.64, 0.755])
    ax.axhline(MARECHAL, color=TINTA_2, lw=2.2, ls=(0, (6, 4)), zorder=2)
    ax.text(0.43, MARECHAL / 1.4, "límite de difracción (λ/14)", color=TINTA_2, fontsize=24, va="top")
    extremos = {"esfera": (4, "bottom"), "parábola": (-4, "top"), "cónica k₀": (0, "center")}
    for (nombre, hz, color), (dx, dy, ha, va) in zip(haces, ((-14, 10, "right", "bottom"), (14, -14, "left", "top"),
                                                            (-14, 10, "right", "bottom"))):
        s = np.array([mejor_foco_onda(hz, h).rms / lam for h in hl])
        ax.plot(2 * hl, s, color=color, lw=4.5, zorder=3)
        dy_nombre, va_nombre = extremos[nombre]
        ax.annotate(nombre, (2 * hl[-1], s[-1]), xytext=(14, dy_nombre), textcoords="offset points", ha="left",
                    va=va_nombre, color=TINTA, fontsize=26, annotation_clip=False)
        h_lim = apertura_limite(hz)
        ax.plot(2 * h_lim, MARECHAL, "o", color=color, ms=16, mec=SUPERFICIE, mew=3, zorder=4)
        ax.annotate(f"{2 * h_lim:.1f} mm", (2 * h_lim, MARECHAL), xytext=(dx, dy), textcoords="offset points",
                    ha=ha, va=va, color=TINTA, fontsize=26)
    ax.set_xscale("log")
    ax.set_yscale("log")
    numero = FuncFormatter(lambda v, _: f"{v:g}")
    ax.set_xticks([0.5, 1, 2, 4, 8])
    ax.set_yticks([1e-3, 1e-2, 0.1, 1, 10])
    for eje in (ax.xaxis, ax.yaxis):
        eje.set_major_formatter(numero)
        eje.set_minor_formatter(NullFormatter())
    ax.set_xlim(0.4, 2 * tope)
    ax.set_ylim(3e-4, 30)
    ax.set_xlabel("diámetro de la apertura (mm)")
    ax.set_ylabel("error RMS del frente\nde onda (en λ)")
    ax.grid(True, which="major", color=REJILLA, lw=1.2)
    return fig


def qr():
    """Codigo QR de la pagina, vectorial, con su margen blanco de 4 modulos."""
    import segno

    FIGURAS.mkdir(parents=True, exist_ok=True)
    ruta = FIGURAS / "qr_simulador.svg"
    datos = io.BytesIO()
    segno.make(URL_SIMULADOR, error="q", micro=False).save(datos, kind="svg", scale=10, border=4, dark=TINTA,
                                                            light="#ffffff", xmldecl=False, svgns=True)
    ruta.write_bytes(datos.getvalue().replace(b"\r\n", b"\n"))
    return ruta


FIGURAS_POSTER = {
    "abanico": abanico,
    "refraccion": refraccion,
    "aberracion": aberracion,
    "mancha": mancha,
    "difraccion": difraccion,
}


def generar_figuras() -> list[Path]:
    estilo_poster()
    rutas = [guardar(fn(), nombre) for nombre, fn in FIGURAS_POSTER.items()]
    rutas.append(qr())
    return rutas


def exportar() -> bool:
    """poster.html -> poster.pdf (para imprimir) y poster.png (vista previa). Devuelve False si
    no esta Playwright."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False
    html = (CARPETA / "poster.html").resolve().as_uri()
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        pagina = navegador.new_page(viewport={"width": 1600, "height": 1132})
        pagina.goto(html, wait_until="networkidle")
        pagina.emulate_media(media="print")
        pagina.pdf(path=str(CARPETA / "poster.pdf"), prefer_css_page_size=True, print_background=True)
        # Vista previa: el poster entero a 2000 px de ancho.
        pagina.emulate_media(media="screen")
        pagina.evaluate("document.documentElement.classList.add('captura')")
        pagina.set_viewport_size({"width": 2000, "height": 1415})
        pagina.screenshot(path=str(CARPETA / "poster.png"), full_page=False)
        navegador.close()
    return True


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Figuras del póster y exportación a PDF y PNG.")
    parser.add_argument("--figuras", action="store_true", help="solo regenera las figuras del póster")
    args = parser.parse_args(argv)
    raiz = CARPETA.parent
    for ruta in generar_figuras():
        print("ok:", str(ruta.relative_to(raiz)).replace("\\", "/"))
    if args.figuras:
        return 0
    if exportar():
        print("ok: poster/poster.pdf, poster/poster.png")
    else:
        print("Falta Playwright para exportar (pip install playwright; playwright install chromium).\n"
              "También se puede abrir poster/poster.html en Chrome o Edge e imprimirlo como PDF.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
