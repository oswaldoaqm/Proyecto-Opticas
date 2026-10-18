"""Estilo comun de todas las figuras del proyecto (decision 0005).

Paleta categorica validada para daltonismo (orden fijo: azul, naranja, aqua,
amarillo) y una rampa azul de un solo tono para magnitudes ordenadas.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib as mpl

SUPERFICIE = "#fcfcfb"
TINTA = "#0b0b0b"
TINTA_2 = "#52514e"
TENUE = "#898781"
REJILLA = "#e1e0d9"
EJE = "#c3c2b7"
VIDRIO = "#eef3f9"

SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
AZUL, NARANJA, AQUA = SERIES[0], SERIES[1], SERIES[2]

# Rampa ordinal (de claro a oscuro); el paso mas claro aun contrasta con el fondo.
RAMPA_AZUL = ["#86b6ef", "#6da7ec", "#5598e7", "#3987e5", "#2a78d6",
              "#256abf", "#1c5cab", "#184f95", "#104281"]


def aplicar_estilo() -> None:
    """Configura matplotlib con la tinta y la paleta del proyecto."""
    mpl.rcParams.update({
        "font.size": 9.5,
        "axes.edgecolor": EJE,
        "axes.labelcolor": TINTA_2,
        "axes.titlecolor": TINTA,
        "axes.prop_cycle": mpl.cycler(color=SERIES),
        "xtick.color": TENUE,
        "ytick.color": TENUE,
        "figure.facecolor": SUPERFICIE,
        "axes.facecolor": SUPERFICIE,
        "savefig.facecolor": SUPERFICIE,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.unicode_minus": False,      # signo menos como guion simple "-"
        "svg.hashsalt": "grupo1-optica",  # ids estables en los SVG
    })


def color_por_altura(h: float, h_max: float) -> str:
    """Color de la rampa azul segun |h| / h_max (mas oscuro = mas lejos del eje)."""
    frac = min(abs(h) / h_max, 1.0) if h_max > 0 else 0.0
    return RAMPA_AZUL[int(round(frac * (len(RAMPA_AZUL) - 1)))]


def guardar_figura(fig, ruta_sin_extension: Path, formatos=("png", "svg"), dpi: int = 200) -> list[Path]:
    """Guarda la figura sin fecha ni version en los metadatos, para que regenerarla
    produzca exactamente los mismos archivos (diffs limpios en git)."""
    ruta_sin_extension = Path(ruta_sin_extension)
    ruta_sin_extension.parent.mkdir(parents=True, exist_ok=True)
    metadatos = {"png": {"Software": None}, "svg": {"Date": None, "Creator": None}}
    rutas = []
    for fmt in formatos:
        ruta = ruta_sin_extension.with_suffix("." + fmt)
        fig.savefig(ruta, dpi=dpi, bbox_inches="tight", metadata=metadatos.get(fmt))
        rutas.append(ruta)
    return rutas
