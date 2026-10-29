"""La escena de la simulacion (actividad 6), lista para dibujar.

Una escena reune lo que pide el enunciado: un punto objeto P, los rayos 1 y 2
(su cruce da la imagen), un abanico de rayos que cubre la lente, la imagen
paraxial y la focal. La usa el notebook 03; la pagina web (web/app.js) arma la
misma escena en JavaScript.

Los angulos de los rayos se miden desde el eje +y, positivos hacia +x:
u = (sen a, cos a) (decision 0001).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from matplotlib.lines import Line2D

from .estilo import AQUA, AZUL, NARANJA, SERIES, SUPERFICIE, TINTA, TINTA_2
from .graficos import dibujar_lente
from .lente import Lente
from .paraxial import ImagenParaxial, focal_efectiva, imagen_paraxial
from .superficies import desde_expresion
from .trazado import Imagen, Trayectoria, imagen_de_dos_rayos, trazar

AMARILLO = SERIES[3]
COLORES = {"incidente": AZUL, "transmitido": NARANJA, "emergente": AQUA}


def lente_desde_formulas(g: str, f: str, n: float = 1.5, semiapertura: float | None = None) -> Lente:
    """Lente entre dos caras escritas como formulas en x: g abajo (entrada) y f arriba (salida)."""
    return Lente(desde_expresion(g, "g"), desde_expresion(f, "f"), n=n, semiapertura=semiapertura)


def direccion(alfa: float) -> np.ndarray:
    """Vector unitario que forma el angulo ``alfa`` (rad) con el eje +y."""
    return np.array([np.sin(alfa), np.cos(alfa)])


def rango_angular(lente: Lente, P) -> tuple[float, float]:
    """Angulos (rad) de los rayos que van de P a los dos bordes de la cara g."""
    a = 0.995 * lente.semiapertura

    def angulo(x):
        return float(np.arctan2(x - P[0], float(lente.abajo(x)) - P[1]))

    return angulo(-a), angulo(a)


def limpio(tr: Trayectoria) -> bool:
    """El rayo entra por g, sale por f sin reflexion total y sigue hacia +y."""
    return (tr.estado == "ok" and len(tr.detalles) == 2
            and not any(d.reflexion_total for d in tr.detalles) and tr.direcciones[-1][1] > 0)


def problema(tr: Trayectoria) -> str:
    """Por que un rayo no sirve para formar la imagen (texto para mostrar)."""
    if tr.estado == "no_toca_lente":
        return "no toca la lente"
    if any(d.reflexion_total for d in tr.detalles):
        return "tiene reflexión total interna"
    if tr.estado == "sale_por_el_borde":
        return "sale por el borde de la lente"
    if tr.estado == "demasiados_eventos":
        return "queda atrapado en la lente"
    return "no sale hacia adelante"


@dataclass
class Escena:
    lente: Lente
    P: np.ndarray
    alfas: tuple[float, float]       # angulos de los rayos 1 y 2 (rad)
    principales: list[Trayectoria]   # rayos 1 y 2
    abanico: list[Trayectoria]
    imagen: Imagen | None            # cruce de los rayos 1 y 2; None si no forman imagen
    paraxial: ImagenParaxial
    focal: float

    @property
    def diferencia(self) -> np.ndarray | None:
        """Imagen de los rayos 1 y 2 menos imagen paraxial, como (dx, dy)."""
        if self.imagen is None or not np.isfinite(self.paraxial.y):
            return None
        return self.imagen.punto - np.array([self.paraxial.x, self.paraxial.y])


def escena(lente: Lente, P, alfas_grados=(2.0, -2.0), n_abanico: int = 13) -> Escena:
    """Traza los rayos 1 y 2 (angulos en grados) y un abanico de ``n_abanico`` rayos
    repartidos entre los bordes de la lente vistos desde P."""
    P = np.asarray(P, dtype=float)
    alfas = (float(np.radians(alfas_grados[0])), float(np.radians(alfas_grados[1])))
    principales = [trazar(lente, P, direccion(a)) for a in alfas]
    amin, amax = rango_angular(lente, P)
    fracciones = np.linspace(-0.97, 0.97, n_abanico) if n_abanico > 1 else np.zeros(n_abanico)
    abanico = [trazar(lente, P, direccion(amin + (t + 1) / 2 * (amax - amin))) for t in fracciones]
    imagen = None
    if all(limpio(t) for t in principales) and abs(alfas[0] - alfas[1]) > 1e-12:
        imagen = imagen_de_dos_rayos(*principales)
    return Escena(lente, P, alfas, principales, abanico, imagen, imagen_paraxial(lente, P), focal_efectiva(lente))


def tramos(tr: Trayectoria, largo_final: float = 10.0) -> list[tuple[str, np.ndarray, np.ndarray]]:
    """Tramos del rayo como (tipo, inicio, fin), con tipo "incidente", "transmitido"
    (dentro del vidrio) o "emergente". El ultimo tramo se prolonga ``largo_final``.
    Despues de una reflexion total el rayo sigue dentro del vidrio."""
    out = []
    dentro = False
    for i, p in enumerate(tr.puntos):
        p = np.asarray(p, dtype=float)
        q = np.asarray(tr.puntos[i + 1], dtype=float) if i + 1 < len(tr.puntos) else p + largo_final * tr.direcciones[i]
        out.append(("incidente" if i == 0 else "transmitido" if dentro else "emergente", p, q))
        if i < len(tr.detalles) and not tr.detalles[i].reflexion_total:
            dentro = not dentro
    return out


def limites(esc: Escena) -> tuple[tuple[float, float], tuple[float, float]]:
    """Rango en y (eje optico) y en x que conviene mostrar: objeto, lente e imagen si esta cerca."""
    lente, P = esc.lente, esc.P
    a = lente.semiapertura
    d_obj = max(lente.y_min - P[1], 0.5)
    alcance = max(3 * d_obj, 12.0)
    y0, y1 = P[1], lente.y_max
    x0, x1 = min(-a, P[0]), max(a, P[0])
    despues = False
    candidatos = []
    if esc.imagen is not None:
        candidatos.append(esc.imagen.punto)
    if np.isfinite(esc.paraxial.y):
        candidatos.append((esc.paraxial.x, esc.paraxial.y))
    for x, y in candidatos:
        if lente.y_max < y <= lente.y_max + alcance:
            y1, despues = max(y1, y), True
        elif lente.y_min - alcance - d_obj <= y < lente.y_min:
            y0 = min(y0, y)
        else:
            continue
        x0, x1 = min(x0, x), max(x1, x)
    largo = y1 - y0
    y1 = y1 + max(0.15 * largo, 1.5) if despues else max(y1 + 0.3 * largo, lente.y_max + 0.6 * d_obj)
    y0 -= 0.05 * largo + 0.8
    ancho = x1 - x0
    return (y0, y1), (x0 - 0.2 * ancho - 0.4, x1 + 0.2 * ancho + 0.4)


def dibujar_escena(ax, esc: Escena, girar: bool = True) -> None:
    """Dibuja la escena: rayos incidentes en azul, dentro del vidrio en naranja y
    emergentes en verde azulado; los rayos 1 y 2 mas gruesos que el abanico. Con ``girar``
    la luz va de izquierda a derecha, como en las figuras del proyecto."""
    (y0, y1), (x0, x1) = limites(esc)
    largo = 3 * ((y1 - y0) + (x1 - x0))

    def xy(p):
        return (p[1], p[0]) if girar else (p[0], p[1])

    def segmento(p, q, **kw):
        (a0, b0), (a1, b1) = xy(p), xy(q)
        ax.plot([a0, a1], [b0, b1], **kw)

    dibujar_lente(ax, esc.lente, girar=girar)
    (ax.axhline if girar else ax.axvline)(0, color="#c3c2b7", lw=0.8, ls=(0, (6, 4)), zorder=0)
    for tr in esc.abanico:
        for tipo, p, q in tramos(tr, largo):
            segmento(p, q, color=COLORES[tipo], lw=0.8, alpha=0.45, zorder=2)
    if esc.imagen is not None and esc.imagen.virtual:
        for tr in esc.principales:
            segmento(tr.salida[0], esc.imagen.punto, color=AQUA, lw=1.3, ls=(0, (4, 3)), zorder=3)
    for tr in esc.principales:
        for tipo, p, q in tramos(tr, largo):
            segmento(p, q, color=COLORES[tipo], lw=2.0, zorder=4, solid_capstyle="round")

    ax.plot(*xy(esc.P), "o", color=TINTA, ms=6, zorder=6)
    ax.annotate("P", xy(esc.P), xytext=(0, -14), textcoords="offset points", ha="center", color=TINTA)
    par = esc.paraxial
    if np.isfinite(par.y):
        ax.plot(*xy((par.x, par.y)), "o", color=TINTA, mfc=SUPERFICIE, mew=1.4, ms=7, zorder=6)
        ax.annotate("paraxial", xy((par.x, par.y)), xytext=(0, -15), textcoords="offset points",
                    ha="center", color=TINTA_2, fontsize=8.5)
    if esc.imagen is not None:
        ax.plot(*xy(esc.imagen.punto), "o", color=TINTA, mfc=AMARILLO, mew=1.2, ms=6.5, zorder=7)
        ax.annotate("imagen virtual" if esc.imagen.virtual else "imagen", xy(esc.imagen.punto),
                    xytext=(0, 9), textcoords="offset points", ha="center", color=TINTA, fontsize=8.5)

    if girar:
        ax.set_xlim(y0, y1)
        ax.set_ylim(x0, x1)
        ax.set_xlabel("y  (eje óptico; la luz avanza en +y)")
        ax.set_ylabel("x")
    else:
        ax.set_xlim(x0, x1)
        ax.set_ylim(y0, y1)
        ax.set_xlabel("x")
        ax.set_ylabel("y  (eje óptico)")
    ax.set_aspect("equal")
    claves = [Line2D([], [], color=c, lw=2, label=t) for t, c in
              (("incidente", AZUL), ("en el vidrio", NARANJA), ("emergente", AQUA))]
    ax.legend(handles=claves, loc="upper left", frameon=False, fontsize=8.5, labelcolor=TINTA_2)


def resumen(esc: Escena) -> str:
    """Las lecturas de la escena en texto, como en la pagina web."""
    lineas = []
    if esc.imagen is None:
        motivos = [f"el rayo {i + 1} {problema(tr)}" for i, tr in enumerate(esc.principales) if not limpio(tr)]
        lineas.append("Rayos 1 y 2: no forman imagen" + (f" ({'; '.join(motivos)})" if motivos else ""))
    else:
        x, y = esc.imagen.punto
        lineas.append(f"Imagen con los rayos 1 y 2: ({x:.3f}, {y:.3f}), {'virtual' if esc.imagen.virtual else 'real'}")
    par = esc.paraxial
    lineas.append(f"Imagen paraxial: ({par.x:.3f}, {par.y:.3f}), aumento {par.aumento:.3f}")
    if esc.diferencia is not None:
        dx, dy = esc.diferencia
        lineas.append(f"Diferencia: Δy = {dy:+.3f}, Δx = {dx:+.3f}")
    lineas.append(f"Focal efectiva: {esc.focal:.3f}")
    return "\n".join(lineas).replace("-0.000", "0.000").replace("+0.000", "0.000")
