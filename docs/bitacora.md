# Bitácora

Registro corto de avances, del más reciente al más antiguo.

## 2026-10-18 (tarde)
- Deducción completa del procedimiento vectorial ([`deduccion.md`](deduccion.md)): rayo paramétrico; intersección cuadrática (con la fórmula estable), cónica y numérica; tangente y normal; regla del sentido de la normal; Snell vectorial deducido desde la conservación de la componente tangencial; reflexión total; imagen por la regla de Cramer.
- Ejemplo resuelto ([notebook 01](../notebooks/01_ejemplo_resuelto.ipynb)) con $P_1 = (0, -30)$ y $P_2 = (-1, -30)$ y cuatro rayos, calculado con un método independiente (cuadrática + Snell con ángulos). Imagen de $P_1$ en $y = 16.029$ (paraxial: $16.187$) e imagen de $P_2$ en $(0.530,\ 15.987)$ (paraxial: $(0.535,\ 16.187)$). Coincide con el trazador vectorial hasta $2\times10^{-16}$.
- En el paquete: intersección exacta para caras cónicas y el módulo `lentes.a_mano`. 79 pruebas.
- fig01: construcción vectorial en cada cara (tangente, normal del enunciado, normal usada y ángulos).
- Se corrigió la decisión 0002: la normal del enunciado falla en las dos caras, no en una.
- No hay fecha exacta ni rúbrica oficial; el formato del póster se confirma la próxima semana.

## 2026-10-18
- Estructura del repositorio, entorno fijado (Python 3.12) y CI en Linux y Windows.
- Núcleo de trazado vectorial (`src/lentes`): caras cónicas o por fórmula, Snell vectorial con reflexión total, trazado completo, imagen por cruce de rayos, predicción paraxial (matrices ABCD) y de lente delgada.
- 63 pruebas automáticas contra límites analíticos ([decisión 0006](decisiones/0006-validar-contra-teoria.md)).
- Boceto (fig00 y notebook 00) con $R = 10$, espesor 2, $n_L = 1.5$ y objeto a 30 unidades: la paraxial de lente gruesa pone la imagen en $y = 16.19$ y la de lente delgada en $y = 15.00$ (la diferencia se debe solo al espesor); el rayo marginal cruza el eje en $y = 13.7$. La aberración crece como $h^2$: $\Delta y \approx -0.154\,h^2$ con caras parabólicas y $-0.269\,h^2$ con caras esféricas.
- Decisiones 0001 a 0006.
