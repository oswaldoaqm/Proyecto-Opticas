# 0004 · Python 3.12 con versiones fijadas y la física en un solo paquete

- **Fecha:** 2026-10-18
- **Estado:** aceptada

## Contexto
Somos cuatro integrantes con computadoras distintas (sobre todo Windows) y el jurado podría querer correr el código. Si cada notebook tiene su propia copia de las fórmulas, un error corregido en un sitio sigue vivo en otro.

## Decisión
- Python 3.12. Dependencias con versión exacta en `requirements.txt`, verificadas con instaladores para Windows y Linux. `environment.yml` crea el entorno conda con esas mismas versiones.
- Toda la física vive en `src/lentes`, un paquete instalable con `pip install -e .`. Notebooks y scripts solo lo importan.
- En el código, los nombres, comentarios y docstrings van sin tildes ni ñ (como los commits), para evitar problemas de codificación en consolas de Windows. Los textos que se muestran (figuras, notebooks, documentos) van con ortografía completa.

## Consecuencias
- Un cambio en la física se hace en un solo lugar y lo cubren las pruebas.
- El CI instala exactamente este entorno en Linux y en Windows en cada push.
- Para actualizar una versión: cambiarla en `requirements.txt`, correr `pytest`, regenerar las figuras y anotarlo en la bitácora.

## Alternativas consideradas
- MATLAB: permitido por el enunciado, pero requiere licencia y es menos fácil de compartir con el jurado.
- Versiones sin fijar: cada quien terminaría con un entorno distinto y resultados que no se pueden comparar.
