# 0005 · Las figuras solo se generan con código

- **Fecha:** 2026-10-18
- **Estado:** aceptada

## Contexto
El póster depende de figuras. Si una figura se retoca a mano, nadie puede rehacerla cuando cambia un parámetro y se pierde la relación entre el número que se muestra y el código que lo calculó.

## Decisión
- Cada figura es una función en `scripts/generar_figuras.py`, registrada con `@figura("nombre")`, y se guarda en `figuras/` en PNG (para ver) y SVG (vectorial, para el póster).
- Ninguna figura se edita a mano: si hay que cambiar algo, se cambia el código y se regenera.
- Los archivos se guardan sin fecha ni versión en los metadatos y los SVG con saltos de línea LF. Así, en la misma máquina, regenerar produce exactamente los mismos bytes y git solo muestra cambios cuando la figura cambió de verdad. Entre sistemas (Windows y Linux) los PNG tienen los mismos píxeles pero pueden cambiar los bytes, y los SVG difieren en millonésimas de punto: no son cambios de la figura.
- Estilo común (`lentes.estilo`): paleta categórica validada para daltonismo (azul, naranja, verde azulado, amarillo, en ese orden) y una rampa azul de un solo tono para magnitudes ordenadas, como la altura del rayo.
- Un color, un significado: en las figuras de los documentos y del póster, azul son las caras parabólicas, naranja las esféricas y verde azulado la cónica que anula el tercer orden; la normal de la refracción va en negro. La simulación (página y notebook 03) colorea por tramo del rayo y no se mezcla con esas figuras en el póster.

## Consecuencias
- Cualquier número o curva del póster se puede rastrear hasta el código que la produjo.
- El CI comprueba en cada push que todas las figuras se pueden regenerar.
