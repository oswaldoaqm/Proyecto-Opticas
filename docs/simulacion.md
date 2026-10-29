# Simulación (actividad 6)

La simulación traza rayos por la lente con el método vectorial y muestra los rayos incidentes, los tramos dentro del vidrio, los rayos emergentes y dónde se forma la imagen. Se usa de dos maneras:

| | Dónde | Para qué |
|---|---|---|
| Página web | <https://oswaldoaqm.github.io/Proyecto-Opticas/> (código en [`web/`](../web)) | Probarla desde el celular sin instalar nada. Es la del código QR del póster ([fig05](../figuras/fig05_qr_simulador.svg)). |
| Notebook | [`notebooks/03_simulacion.ipynb`](../notebooks/03_simulacion.ipynb) | Usarla dentro de Jupyter, sobre el paquete Python. |

## Qué se puede cambiar

| Lo que pide el enunciado | Control |
|---|---|
| Punto objeto $P = (x_P, y_P)$ | Deslizadores de $x_P$ e $y_P$. En la web también se arrastra $P$ en la figura, o se mueve con las flechas del teclado cuando la figura está seleccionada. |
| Índice $n_L$ | De 1 a 2.5. En la web se puede escribir el valor exacto, por ejemplo 1.5168. |
| Caras $g(x)$ y $f(x)$ | Cónicas (radio de vértice $R$ y constante cónica $k$ de cada cara, y espesor $d$) o cualquier fórmula en $x$. |
| Direcciones $\hat u_i$ | Ángulos $\alpha_1$ y $\alpha_2$ de los rayos 1 y 2, con $\hat u = (\sin\alpha, \cos\alpha)$, y un abanico de hasta 41 rayos repartidos sobre la lente. |

## Qué muestra

- Rayos incidentes en azul, tramos dentro del vidrio en naranja y rayos emergentes en verde azulado. Los rayos 1 y 2 van más gruesos que el abanico.
- La imagen como cruce de los rayos 1 y 2 (punto amarillo) y la imagen paraxial de lente gruesa (círculo vacío). Si los rayos salen separándose, la imagen es virtual y se dibujan sus prolongaciones.
- La diferencia entre las dos imágenes, que mide la aberración.
- Los focos $F$ y $F'$ sobre la regla del eje óptico. Si $P$ está en el foco, la imagen se va al infinito y la página lo dice en lugar de mostrar un número enorme.
- Avisos de reflexión total interna y de rayos que no tocan la lente.
- Solo en la web: dónde cruza cada rayo del abanico frente a la altura a la que entra (aberración esférica; con $P$ fuera del eje se ve la coma) y una tabla con los ángulos de incidencia y refracción y la dirección del rayo en cada cara.

En el celular el eje óptico va vertical, como en el enunciado; en pantallas anchas la luz va de izquierda a derecha, como en las figuras.

## Experimentos de la web

Cada experimento carga una lente, un punto objeto y dos rayos, y una nota dice qué mirar.

| Experimento | Qué se ve |
|---|---|
| Lente del ejemplo | El ejemplo resuelto del notebook 01: imagen en $y = 16.029$, paraxial en $16.187$. |
| Caras esféricas | La misma imagen paraxial, pero con rayos a $\pm 7^\circ$ la imagen se adelanta 3.72 unidades. |
| Asférica, $k = -2.33$ | La cónica que anula el tercer orden: con los mismos rayos la diferencia baja a 0.02. |
| Objeto fuera del eje | $P = (-1, -30)$ con los rayos C y D del notebook 01: imagen en $(0.530,\ 15.987)$. |
| Imagen virtual | Objeto dentro del foco: la imagen queda detrás del objeto. |
| Reflexión total | Con $n_L = 2.4$ el rayo 1 se refleja dentro de la lente. |
| Fórmula libre | Caras escritas como fórmula: una parábola más términos en $x^4$ y $x^6$, como se especifican las asféricas. Imita a la cónica que anula el tercer orden; sin el término en $x^6$ la lente queda sobrecorregida y el borde enfoca después que el centro. |

Si se cambia la lente, el experimento deja de estar marcado y la nota lo avisa; Restablecer vuelve a cargarlo. Mover $P$ o los rayos no cuenta como cambiar el experimento.

El experimento elegido queda en la dirección de la página, por ejemplo <https://oswaldoaqm.github.io/Proyecto-Opticas/#esferica>, así que se puede compartir un enlace que abre directo en ese experimento. Las claves son `esferica`, `asferica`, `fuera`, `virtual`, `total` y `formula`; sin clave se abre el ejemplo.

## Cómo está hecha la página

- **Vidrio sobre luz.** Los paneles son de vidrio esmerilado (`backdrop-filter`) y el fondo es la cáustica de la lente de trabajo con caras esféricas iluminada por un haz paralelo, calculada con el mismo `trazado.js` ([`web/fondo.js`](../web/fondo.js)).
- **El vidrio es solo el marco.** La figura, las lecturas y las tablas van sobre superficies casi opacas para que se lean igual con cualquier fondo detrás. El texto tiene contraste de al menos 4.5:1 (WCAG AA) y los colores de los rayos son los de las figuras del proyecto.
- **Rendimiento.** El marco de la figura no desenfoca el fondo: mientras se arrastra $P$ la figura cambia en cada cuadro y el navegador repetiría el desenfoque cada vez (en las pruebas con Chromium sin aceleración gráfica, 30 ms por cuadro en lugar de 17).
- **Preferencias del sistema.** Con "reducir transparencia", o en navegadores sin `backdrop-filter`, los paneles son opacos; con "reducir movimiento" no hay animaciones. Safari todavía no informa la preferencia de transparencia ([Chrome for Developers](https://developer.chrome.com/blog/css-prefers-reduced-transparency)).
- **Uso.** Los controles están en tres pestañas (Objeto P, Lente, Rayos). Al abrir la página, una pista sobre $P$ indica que se puede arrastrar y desaparece cuando se mueve por primera vez.

Las pautas de contraste y de desenfoque siguen a [Axess Lab](https://axesslab.com/?p=5111) y [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/backdrop-filter).

## Cómo sabemos que la página calcula bien

La página no ejecuta Python: usa `web/trazado.js`, el trazador traducido a JavaScript para que cargue al instante en un celular. Para que no haya dos físicas distintas, [`tests/test_web.py`](../tests/test_web.py) traza los mismos rayos con las dos versiones en 13 casos (cónicas, fórmulas, objeto fuera del eje, reflexión total, rayo que no toca la lente, rayos junto al borde y el experimento de la fórmula libre), con las mismas 601 muestras por cara que usa la página, y exige los mismos puntos de impacto y direcciones, con diferencias menores que $10^{-9}$ ($10^{-7}$ con fórmulas, porque la web deriva numéricamente). La prueba corre en el CI en cada cambio. El notebook usa el paquete Python directamente (`lentes.simulacion`, con pruebas en [`tests/test_simulacion.py`](../tests/test_simulacion.py)). Detalles en la [decisión 0007](decisiones/0007-simulacion-web-en-javascript.md).

## Límites

- Rayos en el plano del dibujo (meridionales).
- Luz de un solo color: no hay dispersión ni aberración cromática.
- No calcula intensidades (coeficientes de Fresnel): solo la geometría de los rayos.
- Las caras deben poder escribirse como $y = f(x)$.

## Usarla sin internet

La carpeta `web/` no necesita servidor: basta abrir `web/index.html` en el navegador. También se puede servir con `python -m http.server -d web` y abrir <http://localhost:8000>. Sin conexión solo cambian las fuentes tipográficas.

## Cómo se publica

[`.github/workflows/pages.yml`](../.github/workflows/pages.yml) publica `web/` en GitHub Pages cada vez que cambia en `main`. Se activa una vez en el repositorio: Settings → Pages → Source: GitHub Actions.
