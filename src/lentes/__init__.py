"""lentes: trazado vectorial de rayos en lentes gruesas.

Proyecto del Grupo 1, Optica & Ondas (UTEC, 2026-2).
Se importan aparte: ``lentes.graficos`` y ``lentes.estilo`` (figuras),
``lentes.a_mano`` (ejemplo resuelto con un metodo independiente),
``lentes.aberraciones`` (aberracion medida con el trazado) y ``lentes.seidel``
(teoria de tercer orden).
"""
from .lente import Lente, lente_biconvexa, lente_con_forma
from .paraxial import (
    ImagenParaxial,
    focal_efectiva,
    foco_imagen,
    imagen_lente_delgada,
    imagen_paraxial,
    matriz_refraccion,
    matriz_sistema,
    matriz_traslacion,
)
from .superficies import Superficie, conica, desde_expresion, esferica, parabolica
from .trazado import (
    DetalleRefraccion,
    Imagen,
    Trayectoria,
    cruce_con_eje,
    detalle_refraccion,
    imagen_de_dos_rayos,
    interseccion,
    interseccion_exacta,
    interseccion_rectas,
    raices_cuadratica,
    rayo_hacia,
    refractar,
    trazar,
    unitario,
)

__version__ = "0.1.0"

__all__ = [
    "DetalleRefraccion",
    "Imagen",
    "ImagenParaxial",
    "Lente",
    "Superficie",
    "Trayectoria",
    "conica",
    "cruce_con_eje",
    "desde_expresion",
    "detalle_refraccion",
    "esferica",
    "focal_efectiva",
    "foco_imagen",
    "imagen_de_dos_rayos",
    "imagen_lente_delgada",
    "imagen_paraxial",
    "interseccion",
    "interseccion_exacta",
    "interseccion_rectas",
    "lente_biconvexa",
    "lente_con_forma",
    "matriz_refraccion",
    "matriz_sistema",
    "matriz_traslacion",
    "parabolica",
    "raices_cuadratica",
    "rayo_hacia",
    "refractar",
    "trazar",
    "unitario",
]
