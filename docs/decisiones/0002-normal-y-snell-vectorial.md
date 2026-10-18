# 0002 · La normal se orienta hacia el medio de incidencia; Snell en forma vectorial

- **Fecha:** 2026-10-18
- **Estado:** aceptada

## Contexto
$\hat n = (-s', 1)/\sqrt{1+s'^2}$ siempre apunta hacia $+y$: en la cara $g$ (la primera) apunta hacia dentro del vidrio y en la cara $f$ (la segunda) hacia fuera. La fórmula de Snell vectorial supone una normal que mira hacia el medio de donde viene la luz ($\hat n\cdot\hat u < 0$). Como en nuestra lente la luz viaja en $+y$, la $\hat n$ del enunciado incumple esa condición en **las dos** caras; y si se fijara la normal "hacia fuera del vidrio", fallaría solo en la segunda. Hace falta una regla que no dependa de la cara. La actividad 2 pide justamente explicar cómo elegir el sentido correcto.

## Decisión
En cada refracción se usa la normal que mira **hacia el medio de donde viene la luz**: si $\hat n\cdot\hat u > 0$, se cambia $\hat n \to -\hat n$. Así $\cos\theta_i = -\hat n\cdot\hat u > 0$ siempre y la ley de Snell vectorial es la misma en las dos caras:

$$\hat u_t = \eta\,\hat u + \left(\eta\cos\theta_i - \cos\theta_t\right)\hat n,\qquad \eta = \frac{n_1}{n_2},\qquad \cos\theta_t = \sqrt{1-\eta^2\left(1-\cos^2\theta_i\right)}.$$

Si el radicando es negativo hay **reflexión total interna**: $\hat u_r = \hat u + 2\cos\theta_i\,\hat n$, y el rayo sigue dentro del vidrio.

## Por qué funciona (para la defensa)
Al cruzar la interfaz se conserva la componente tangencial de $n\,\hat u$: $n_1(\hat u\cdot\hat t) = n_2(\hat u_t\cdot\hat t)$, que es la ley de Snell $n_1\sin\theta_i = n_2\sin\theta_t$. La componente normal queda fijada por $|\hat u_t| = 1$ y porque el rayo debe pasar al otro lado. La fórmula de arriba cumple ambas condiciones.

## Consecuencias
- Una sola función (`lentes.refractar`) para todas las refracciones, sin casos especiales por cara.
- `tests/test_refraccion.py` comprueba que el resultado no depende del signo con que llegue la normal, que se recupera $n_1\sin\theta_i = n_2\sin\theta_t$, que se conserva la componente tangencial en 500 casos al azar y que aparece la reflexión total más allá del ángulo crítico.

## Alternativas consideradas
- Fijar la normal "hacia afuera del vidrio" en ambas caras y cambiar el signo de la fórmula según el rayo entre o salga: funciona, pero obliga a distinguir casos y es fácil equivocarse.

## Historial
- 2026-10-18: se corrigió el contexto. La primera versión decía que, usada tal cual, la normal del enunciado fallaba en una sola cara; con la luz en $+y$ falla en las dos. La deducción completa está en [`docs/deduccion.md`](../deduccion.md), sección 5.
