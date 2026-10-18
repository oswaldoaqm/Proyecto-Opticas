# Bitácora

Registro corto de avances, del más reciente al más antiguo.

## 2026-10-18
- Estructura del repositorio, entorno fijado (Python 3.12) y CI en Linux y Windows.
- Núcleo de trazado vectorial (`src/lentes`): caras cónicas o por fórmula, Snell vectorial con reflexión total, trazado completo, imagen por cruce de rayos, predicción paraxial (matrices ABCD) y de lente delgada.
- 63 pruebas automáticas contra límites analíticos ([decisión 0006](decisiones/0006-validar-contra-teoria.md)).
- Boceto (fig00 y notebook 00) con $R = 10$, espesor 2, $n_L = 1.5$ y objeto a 30 unidades: la paraxial de lente gruesa pone la imagen en $y = 16.19$ y la de lente delgada en $y = 15.00$ (la diferencia se debe solo al espesor); el rayo marginal cruza el eje en $y = 13.7$. La aberración crece como $h^2$: $\Delta y \approx -0.154\,h^2$ con caras parabólicas y $-0.269\,h^2$ con caras esféricas.
- Decisiones 0001 a 0006.
