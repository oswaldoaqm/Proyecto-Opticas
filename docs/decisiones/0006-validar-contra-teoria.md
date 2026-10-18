# 0006 · Todo resultado se valida contra un límite analítico

- **Fecha:** 2026-10-18
- **Estado:** aceptada

## Contexto
La pregunta más probable de un jurado investigador es: "¿cómo saben que su simulación está bien?". La respuesta no puede ser "se ve bien".

## Decisión
Cada pieza del código se compara con un resultado conocido mediante pruebas automáticas (`tests/`):

| Comprobación | Qué valida |
|---|---|
| Interfaz plana: $n_1\sin\theta_i = n_2\sin\theta_t$; incidencia normal sin desvío; reflexión total más allá del ángulo crítico | Snell vectorial |
| Intersección con una parábola igual a la raíz de la ecuación cuadrática | Intersección rayo–cara |
| Rayos muy cerca del eje → imagen paraxial de lente gruesa (matrices ABCD) | Trazado completo |
| Lente muy delgada → ecuación de lente delgada; focal igual a la ecuación del fabricante para lente gruesa | Óptica paraxial |
| Rayos a $\pm h$ cruzan en el mismo punto | Simetría |
| Un rayo trazado de vuelta regresa al objeto | Reversibilidad del camino óptico |
| $\Delta y \propto h^2$ para $h$ pequeño | Aberración esférica de tercer orden |
| Objeto fuera del eje: diferencias con la paraxial $\propto x_P^2$ a lo largo del eje y $\propto x_P^3$ en altura | Aberraciones de campo de tercer orden |
| Objeto dentro de la distancia focal → imagen virtual en el lugar paraxial | Prolongación de rayos hacia atrás |
| Intersección exacta con cónicas igual a la numérica, en cientos de rayos al azar y cinco formas de cara | Las dos maneras de hallar el impacto |
| Snell con ángulos igual a Snell vectorial; el ejemplo resuelto "a mano" igual al trazador, punto por punto | Todo el recorrido del rayo, con dos implementaciones independientes |
| Fórmula cuadrática estable frente a la escolar, contra un cálculo con 60 cifras | Pérdida de cifras en rayos casi paralelos al eje |

## Consecuencias
- Si un cambio rompe la física, una prueba falla antes de que el error llegue al póster.
- El CI corre las pruebas en Linux y Windows en cada push.
- Toda funcionalidad nueva (por ejemplo, el frente de onda o la forma óptima) entra con su propia comprobación contra teoría.
