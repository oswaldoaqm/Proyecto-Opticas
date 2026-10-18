# Enunciado del Grupo 1 y matriz de cumplimiento

**Proyecto:** Formación de imágenes en lentes reales mediante el análisis vectorial de rayos  
**Curso:** Óptica & Ondas, UTEC 2026-2 · Profesores Marco Cuyubamba y Eduardo Castillo  
**Fuente:** documento del curso con los proyectos de todos los grupos. No se publica en este repositorio (está en `.gitignore`); aquí se resume lo que corresponde al Grupo 1.

## El problema, en nuestras palabras
En una lente real la imagen no sale solo de la ecuación de lente delgada. Cuando el espesor y la curvatura de las caras importan, cada rayo se refracta dos veces: al entrar al vidrio y al salir. Hay que analizar la formación de imágenes con un procedimiento vectorial basado en la dirección de los rayos, la normal local de cada cara y la ley de Snell.

Se considera una lente biconvexa de índice $n_L$, limitada por dos curvas suaves $y = f(x)$ e $y = g(x)$ y rodeada de aire. Un punto objeto $P = (x_P, y_P)$ emite rayos que llegan a la primera cara, atraviesan la lente y salen. La imagen se obtiene como la intersección de al menos dos rayos emergentes.

## Matriz de cumplimiento

Cada fila es un requisito del enunciado. Se actualiza con cada avance.

| ID | Requisito | Dónde se cumple | Estado |
|---|---|---|---|
| A1 | Modelar cada rayo con la recta paramétrica $\mathbf L(\lambda) = \mathbf P_0 + \lambda\hat{\mathbf u}$ e indicar cómo se halla su intersección con $y = f(x)$ o $y = g(x)$ | Código: `lentes.trazado.interseccion` · deducción escrita: pendiente | en progreso |
| A2 | Construir $\hat t$ y $\hat n$ para $y = f(x)$ y explicar cómo elegir el sentido correcto de la normal en cada refracción | Código: `Superficie.tangente`, `Superficie.normal`, `refractar` · [decisión 0002](decisiones/0002-normal-y-snell-vectorial.md) · texto del póster: pendiente | en progreso |
| A3 | Aplicar el procedimiento a una biconvexa ($f$ y $g$ de concavidad contraria, $n_L = 1.5$): para un punto objeto, trazar al menos dos rayos, sus dos refracciones y la posición de la imagen | [Notebook 00](../notebooks/00_boceto_trazado.ipynb) (boceto) · ejemplo resuelto a mano: pendiente | en progreso |
| A4 | Comparar con la aproximación paraxial: en qué condiciones coinciden y cuándo aparecen diferencias apreciables | `lentes.paraxial` · fig00 (boceto) · discusión: pendiente | en progreso |
| A5 | Analizar cómo cambia la imagen cuando los rayos incidentes se alejan del eje y relacionarlo con la aberración esférica | fig00, panel (b) (boceto) · análisis final: pendiente | en progreso |
| A6 | Simulación (Python, MATLAB u otro) del trazado vectorial que permita variar $P$, $n_L$, $f(x)$, $g(x)$ y $\hat u_i$, y muestre rayos incidentes, transmitidos y emergentes y la posición de la imagen | Núcleo listo (`src/lentes`) · interfaz interactiva: pendiente | en progreso |
| E1 | Póster académico | `poster/` | pendiente |
| E2 | Deducción del procedimiento vectorial | — | pendiente |
| E3 | Simulación funcional | — | pendiente |
| E4 | Trazado de rayos para al menos dos puntos objeto | Notebook 00 (boceto: $P$ en el eje y $P_2$ fuera del eje) | en progreso |
| E5 | Comparación con la aproximación paraxial | fig00 (boceto) | en progreso |
| E6 | Discusión física de las aberraciones observadas | — | pendiente |

> Si hay una rúbrica oficial aparte, se copia aquí y se cruza fila por fila con esta tabla.
