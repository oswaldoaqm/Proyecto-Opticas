# Enunciado del Grupo 1 y matriz de cumplimiento

**Proyecto:** Formación de imágenes en lentes reales mediante el análisis vectorial de rayos  
**Curso:** Óptica & Ondas, UTEC 2026-2 · Profesores Marco Cuyubamba y Eduardo Castillo  
**Fuente:** documento del curso con los proyectos de todos los grupos. No se publica en este repositorio (está en `.gitignore`); aquí se resume lo que corresponde al Grupo 1.

## El problema, en nuestras palabras
En una lente real la imagen no sale solo de la ecuación de lente delgada. Cuando el espesor y la curvatura de las caras importan, cada rayo se refracta dos veces: al entrar al vidrio y al salir. Hay que analizar la formación de imágenes con un procedimiento vectorial basado en la dirección de los rayos, la normal local de cada cara y la ley de Snell.

Se considera una lente biconvexa de índice $n_L$, limitada por dos curvas suaves $y = f(x)$ e $y = g(x)$ y rodeada de aire. Un punto objeto $P = (x_P, y_P)$ emite rayos que llegan a la primera cara, atraviesan la lente y salen. La imagen se obtiene como la intersección de al menos dos rayos emergentes.

## Matriz de cumplimiento

Cada fila es un requisito del enunciado. Se actualiza con cada avance. No hay rúbrica oficial: esta matriz y la rúbrica interna de abajo hacen ese papel.

| ID | Requisito | Dónde se cumple | Estado |
|---|---|---|---|
| A1 | Modelar cada rayo con la recta paramétrica $\mathbf L(\lambda) = \mathbf P_0 + \lambda\hat{\mathbf u}$ e indicar cómo se halla su intersección con $y = f(x)$ o $y = g(x)$ | [Deducción](deduccion.md), secciones 2 y 3 · `interseccion`, `interseccion_exacta` · pruebas en `tests/test_exacta.py` | listo |
| A2 | Construir $\hat t$ y $\hat n$ para $y = f(x)$ y explicar cómo elegir el sentido correcto de la normal en cada refracción | [Deducción](deduccion.md), secciones 4 a 6 · fig01 · [decisión 0002](decisiones/0002-normal-y-snell-vectorial.md) · `refractar` | listo |
| A3 | Aplicar el procedimiento a una biconvexa ($f$ y $g$ de concavidad contraria, $n_L = 1.5$): para un punto objeto, trazar al menos dos rayos, sus dos refracciones y la posición de la imagen | [Notebook 01](../notebooks/01_ejemplo_resuelto.ipynb): cuatro rayos con todos los pasos, imagen de cada punto objeto, verificado contra el trazador | listo |
| A4 | Comparar con la aproximación paraxial: en qué condiciones coinciden y cuándo aparecen diferencias apreciables | [Análisis](aberraciones.md), sección 2 · fig02 · [notebook 02](../notebooks/02_aberraciones.ipynb) | listo |
| A5 | Analizar cómo cambia la imagen cuando los rayos incidentes se alejan del eje y relacionarlo con la aberración esférica | [Análisis](aberraciones.md), sección 3 · fig03 · teoría de Seidel en `lentes.seidel` | listo |
| A6 | Simulación (Python, MATLAB u otro) del trazado vectorial que permita variar $P$, $n_L$, $f(x)$, $g(x)$ y $\hat u_i$, y muestre rayos incidentes, transmitidos y emergentes y la posición de la imagen | [Simulación](simulacion.md): [página web](https://oswaldoaqm.github.io/Proyecto-Opticas/) con QR (fig05) y [notebook 03](../notebooks/03_simulacion.ipynb) · comparada con el paquete en `tests/test_web.py` | listo |
| E1 | Póster académico | [`poster/`](../poster/): borrador A0 horizontal sobre la plantilla de UTEC ([decisión 0008](decisiones/0008-poster-en-html-a-tamano-real.md)) | en curso |
| E2 | Deducción del procedimiento vectorial | [docs/deduccion.md](deduccion.md) y fig01 · en el póster, los cuatro pasos de la metodología | listo |
| E3 | Simulación funcional | Página web y notebook 03 ([simulacion.md](simulacion.md)); fig05 lleva el QR al póster | listo |
| E4 | Trazado de rayos para al menos dos puntos objeto | Notebook 01: $P_1 = (0, -30)$ en el eje y $P_2 = (-1, -30)$ fuera del eje | listo |
| E5 | Comparación con la aproximación paraxial | fig02 y [análisis](aberraciones.md), sección 2 | listo |
| E6 | Discusión física de las aberraciones observadas | fig03, fig04, fig06 y [análisis](aberraciones.md), secciones 3 a 5 · en el póster, resultados y conclusiones | listo |

## Rúbrica interna

Además de cumplir cada fila, revisamos el trabajo con los criterios que aplicaría un jurado de investigadores:

| Criterio | Qué buscamos |
|---|---|
| Corrección física | Ecuaciones deducidas, no copiadas; hipótesis explícitas; signos y sentidos justificados |
| Validación | Cada resultado comparado con un límite conocido o con un cálculo independiente ([decisión 0006](decisiones/0006-validar-contra-teoria.md)) |
| Reproducibilidad | Cualquier figura o número se regenera con un comando; CI en verde |
| Claridad | El póster se entiende en dos minutos y cada integrante explica su parte |
| Calidad visual | Figuras legibles, rotuladas, con paleta accesible y generadas por código |
| Profundidad | Al menos dos extras que van más allá del enunciado ([plan](plan.md)) |
