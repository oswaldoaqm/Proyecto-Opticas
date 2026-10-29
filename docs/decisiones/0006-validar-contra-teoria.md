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
| Intersección con una parábola igual a la raíz de la ecuación cuadrática | Intersección rayo-cara |
| Rayos muy cerca del eje → imagen paraxial de lente gruesa (matrices ABCD) | Trazado completo |
| Rayos dirigidos a la cara de entrada a una distancia del borde de entre $10^{-3}$ y $10^{-9}$ veces la semiapertura se refractan allí y coinciden con la intersección exacta | Intersección junto al borde de la lente |
| Lente muy delgada → ecuación de lente delgada; focal igual a la ecuación del fabricante para lente gruesa; $1/s + 1/s' = 1/f$ con la focal efectiva y los planos principales da la imagen de la lente gruesa | Óptica paraxial |
| Rayos a $\pm h$ cruzan en el mismo punto | Simetría |
| Un rayo trazado de vuelta regresa al objeto | Reversibilidad del camino óptico |
| $\Delta y \propto h^2$ para $h$ pequeño | Aberración esférica de tercer orden |
| Objeto fuera del eje: diferencias con la paraxial $\propto x_P^2$ a lo largo del eje y $\propto x_P^3$ en altura | Aberraciones de campo de tercer orden |
| Objeto dentro de la distancia focal → imagen virtual en el lugar paraxial | Prolongación de rayos hacia atrás |
| Intersección exacta con cónicas igual a la numérica, en cientos de rayos al azar y cinco formas de cara | Las dos maneras de hallar el impacto |
| Snell con ángulos igual a Snell vectorial; el ejemplo resuelto "a mano" igual al trazador, punto por punto | Todo el recorrido del rayo, con dos implementaciones independientes |
| Fórmula cuadrática estable frente a la escolar, contra un cálculo con 60 cifras | Pérdida de cifras en rayos casi paralelos al eje |
| Coeficiente de aberración esférica del trazado igual al de la suma de Seidel, en diez lentes (dos con caras hiperbólicas, una sobrecorregida), con diferencia relativa menor que $10^{-7}$ | Trazado completo frente a teoría de tercer orden |
| Mejor foco a 2/3 y círculo de mínima confusión a 3/4 entre el foco paraxial y el marginal (pupila pequeña); con aberración zonal, los mejores planos iguales a un barrido fino del eje | Cálculo de la mancha y del mejor foco |
| Forma óptima de una lente delgada: $q = 2(n^2-1)/(n+2)$ | Lentes de forma y focal dadas |
| La cónica que anula $S_I$ deja una aberración que crece como $h^4$ | Aporte de las caras cónicas |
| La página web traza los mismos rayos que el paquete Python, punto por punto, en 13 casos (incluidos rayos junto al borde y el experimento de la fórmula libre) | La simulación en JavaScript ([decisión 0007](0007-simulacion-web-en-javascript.md)) |
| La escena del notebook 03 da la misma imagen que el método a mano | La simulación en Python |
| Frente de onda por camino óptico (Fermat): el coeficiente de $h^4$ es $S_I/8$ en cuatro lentes, sin término $h^2$ en la imagen paraxial | Camino óptico frente a Seidel |
| Menor $W_\text{rms}$ a mitad de camino entre los focos y igual a 1/4 del paraxial; patrón de Airy con el primer cero en $0.61\lambda/\mathrm{NA}$; Strehl exacto y aproximación de Maréchal a menos de 0.005 hasta el límite de Maréchal incluido; en el plano paraxial la apertura límite es $4^{-1/4}$ de la del mejor foco | Difracción |
| La cónica de menor $W_\text{rms}$ con la pupila completa deja menos error que la que anula el tercer orden y se acerca a ella al achicar la pupila | Compensación entre tercer y quinto orden |

## Consecuencias
- Si un cambio rompe la física, una prueba falla antes de que el error llegue al póster.
- El CI corre las pruebas en Linux y Windows en cada push.
- Toda funcionalidad nueva (por ejemplo, el frente de onda o la forma óptima) entra con su propia comprobación contra teoría.
