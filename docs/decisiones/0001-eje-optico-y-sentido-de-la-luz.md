# 0001 · El eje óptico es el eje y y la luz viaja en +y

- **Fecha:** 2026-10-18
- **Estado:** aceptada

## Contexto
El enunciado describe las caras de la lente como $y = f(x)$ e $y = g(x)$, de concavidad contraria, y da los vectores $\hat t = (1, f')/\sqrt{1+f'^2}$ y $\hat n = (-f', 1)/\sqrt{1+f'^2}$. Una cara escrita como función de $x$ solo tiene sentido si la lente está "acostada": su eje de simetría, el eje óptico, es el eje $y$, y la luz la atraviesa en vertical.

## Decisión
- Eje óptico: la recta $x = 0$ (eje $y$). La luz viaja en $+y$ y el objeto $P$ está debajo de la lente.
- $g(x)$ es la cara de abajo, cóncava hacia arriba: es la **primera** que toca la luz. $f(x)$ es la de arriba, cóncava hacia abajo: es la **segunda**.
- La lente está centrada en el origen, con vértices en $y = -d/2$ (cara $g$) e $y = +d/2$ (cara $f$), donde $d$ es el espesor sobre el eje.
- Radio de vértice con signo: $R = 1/s''(0)$. Con la luz en $+y$ coincide con la convención de la óptica paraxial ($R > 0$ si el centro de curvatura está del lado de salida). En una biconvexa, $R_g > 0$ y $R_f < 0$.
- Longitudes en unidades arbitrarias (pueden leerse como mm); índice del aire igual a 1.

## Consecuencias
- Las fórmulas del póster coinciden letra por letra con las del enunciado.
- En las figuras la vista se gira 90°: la luz va de izquierda a derecha, como en los libros. Los ejes se rotulan ("y, eje óptico") para que no haya confusión.
- El trazador acepta objetos arriba o abajo y rayos en cualquier dirección; la parte paraxial (`lentes.paraxial`) asume luz en $+y$.

## Alternativas consideradas
- Escribir las caras como $x = f(y)$, con el eje horizontal: descartada porque cambiaría la notación del enunciado y las expresiones de $\hat t$ y $\hat n$.
