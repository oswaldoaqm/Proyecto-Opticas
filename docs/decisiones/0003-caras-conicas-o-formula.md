# 0003 · Las caras son cónicas o cualquier fórmula en x

- **Fecha:** 2026-10-18
- **Estado:** aceptada

## Contexto
La actividad 3 pide una lente concreta, la 5 pide estudiar la aberración esférica y la simulación (actividad 6) debe permitir cambiar $f(x)$ y $g(x)$.

## Decisión
- Familia cónica con vértice en $(0, y_v)$, radio de vértice $R$ y constante cónica $k$:
  $$s(x) = y_v + \frac{c\,x^2}{1+\sqrt{1-(1+k)\,c^2x^2}},\qquad c = \frac{1}{R}.$$
  Con $k = 0$ es una circunferencia (lente esférica, como las comerciales) y con $k = -1$ una parábola.
- También cualquier fórmula en $x$, por ejemplo `"1 - x**2/20"`: sympy calcula la derivada exacta, así que la normal no tiene error numérico.
- El borde de la lente es donde $f(x) = g(x)$, o una semiapertura dada.
- La intersección rayo–cara se resuelve numéricamente (muestreo + método de Brent), así sirve para cualquier cara. Para la parábola se comprueba contra la fórmula cuadrática exacta (`tests/test_trazado.py`).

## Consecuencias
- El ejemplo a mano usa caras parabólicas: la intersección sale de una ecuación cuadrática.
- La discusión compara parábola y esfera con los mismos radios de vértice (misma predicción paraxial, distinta aberración) y deja abierta la búsqueda de la cónica que anula la aberración, que es la idea de las lentes asféricas.

## Alternativas consideradas
- Solo parábolas: más simple, pero deja fuera las lentes esféricas reales y la comparación entre formas.
- Derivadas numéricas para fórmulas arbitrarias: introducen error en la normal; sympy lo evita.
