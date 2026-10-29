# 0007 · La simulación web es el trazador traducido a JavaScript y se valida contra Python

- **Fecha:** 2026-10-18
- **Estado:** aceptada

## Contexto
La actividad 6 pide una simulación que permita variar $P$, $n_L$, $f(x)$, $g(x)$ y $\hat u_i$. Queremos que el jurado la pruebe desde su celular escaneando un código QR del póster, sin instalar nada y sin esperar.

## Decisión
- La simulación para el público es una página estática ([`web/`](../../web)) con el trazador traducido a JavaScript (`web/trazado.js`): misma convención de ejes, misma normal orientada hacia el medio de incidencia, misma búsqueda del impacto (se muestrea el tramo del rayo dentro de la apertura y el cruce se afina: por bisección en JavaScript, con el método de Brent en Python) y el mismo Snell vectorial con reflexión total.
- [`tests/test_web.py`](../../tests/test_web.py) ejecuta el JavaScript con Node.js y lo compara con el paquete Python en 13 casos, con las mismas 601 muestras por cara que usa la página. En el CI esa prueba no se puede omitir.
- GitHub Pages publica `web/` desde `main` ([`.github/workflows/pages.yml`](../../.github/workflows/pages.yml)).
- El notebook 03 tiene los mismos controles con ipywidgets, sobre el paquete Python (`lentes.simulacion`).

## Consecuencias
- La página pesa unos 105 kB sin contar las fuentes (32 kB comprimida) y funciona sin conexión abriendo `web/index.html`.
- Hay dos implementaciones de la física y la prueba automática evita que se separen: un cambio en `src/lentes/trazado.py` que no se repita en `web/trazado.js` hace fallar el CI.
- La web deriva numéricamente las caras escritas como fórmula (Python lo hace con sympy). Las diferencias son del orden de $10^{-8}$ (la prueba pide $10^{-7}$), muy por debajo de lo que se ve.

## Alternativas consideradas
- **Pyodide** (Python dentro del navegador): usaría el mismo paquete, pero descarga decenas de MB (numpy, scipy, sympy, matplotlib) y tarda varios segundos en arrancar en un celular.
- **Binder o Voilà**: el notebook en un servidor. Binder tarda minutos en arrancar y Voilà necesita un servidor propio.
- **Solo el notebook**: cumple el enunciado, pero el jurado no podría probarlo desde el póster.
