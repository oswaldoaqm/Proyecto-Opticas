# 0008 · El póster es una página HTML a tamaño real sobre la plantilla de UTEC

- **Fecha:** 2026-10-25
- **Estado:** propuesta

## Contexto
Los profesores piden seguir las buenas prácticas de pósters y compartieron dos plantillas de UTEC (A0 horizontal y vertical, hechas en Google Slides) como guía. Las plantillas no se suben al repositorio: son material del curso. El póster depende de figuras y números que salen del código, y queremos que un cambio en el código llegue al póster sin copiar a mano.

## Decisión
- **Formato:** A0 horizontal, 1189 x 841 mm, con la identidad de la plantilla: logo de UTEC arriba a la izquierda, título en la banda celeste, integrantes en la banda negra y secciones Introducción, Metodología, Resultados, Conclusiones y Referencias. Se agregan una sección de validación, el hallazgo principal destacado arriba de los resultados y el código QR de la simulación.
- **Fuente:** `poster/poster.html`, escrita en milímetros y puntos, así que al imprimir sale a tamaño real. Las figuras salen de `poster/generar_poster.py`, dibujadas al ancho de una columna (343 mm) con textos de 24 pt o más. Ninguna figura se edita a mano (decisión 0005).
- **Exportación:** `python poster/generar_poster.py` genera `poster/poster.pdf` y una vista previa `poster/poster.png` con Playwright. Sin Playwright se abre `poster.html` en Chrome o Edge y se imprime como PDF.
- **Buenas prácticas:** entre 600 y 800 palabras, texto de lectura de 30 pt y nada por debajo de 24 pt, una idea por figura, rótulos directos en lugar de leyendas cuando se puede, un color con un solo significado y el QR de unos 13 cm con su margen blanco.
- **Letra:** Arial, como la plantilla. Donde no está (Linux), Liberation Sans, que tiene las mismas medidas: el texto se corta igual en cualquier sistema.

## Consecuencias
- Cada número del póster se puede rastrear hasta un notebook o una prueba, y las figuras se regeneran con un comando; el CI comprueba que se puedan regenerar.
- Para cambiar un texto se edita el HTML, que es texto plano: los cambios se ven en git y se revisan en el pull request.
- El celeste de las bandas es el de la plantilla (#01BEFF), pero los títulos van en negro y no en blanco como en la plantilla: blanco sobre ese celeste da un contraste de 2.1:1, por debajo del 3:1 que piden las pautas de accesibilidad (WCAG) para textos grandes, y negro da 9.2:1. Todo el texto de lectura va en negro sobre blanco.

## Alternativas consideradas
- **Google Slides con la plantilla:** es lo que usaron los profesores y permite editar entre varios, pero las figuras y los números se copian a mano y quedan desactualizados cuando cambia el código.
- **LaTeX (beamerposter o tikzposter):** buena tipografía para fórmulas, pero pide instalar una distribución de TeX en cada computadora y es más difícil de editar para todo el grupo.
- **La plantilla vertical:** cabe lo mismo en dos columnas más largas. Colgado, el póster vertical mide 1.19 m de alto y su parte de abajo queda baja para leer de pie; el horizontal mide 0.84 m y todo queda entre la cintura y los ojos. Si la exposición pide vertical, se cambia el tamaño de página y se pasa a dos columnas.
