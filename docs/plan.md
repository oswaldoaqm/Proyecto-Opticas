# Plan de trabajo (tres semanas)

**Entrega:** sin fecha exacta todavía; planificamos con tres semanas desde el 18 de octubre.  
**Formato del póster:** los profesores lo confirman la semana del 19 de octubre.  
**Rúbrica:** no hay una oficial; usamos la matriz de cumplimiento y la rúbrica interna de [`enunciado.md`](enunciado.md).  
**Meta:** cumplir el enunciado al 100 % y un trabajo que un investigador revise y encuentre riguroso.

**Avance:**
- Semana 1: deducción ([`deduccion.md`](deduccion.md)) y ejemplo resuelto ([notebook 01](../notebooks/01_ejemplo_resuelto.ipynb)). Listo.
- Semana 2: comparación paraxial y aberraciones ([`aberraciones.md`](aberraciones.md), fig02 a fig04) con los extras 1 a 3, y la simulación interactiva (A6, [`simulacion.md`](simulacion.md)): página web con código QR (extra 6) y notebook 03. Listo.

## Hitos

| Semana | Fechas | Entregables | Listo cuando… |
|---|---|---|---|
| 1 | 19-25 oct | Deducción vectorial completa (A1, A2) · ejemplo resuelto a mano con dos puntos objeto (A3, E4) | cada número del ejemplo coincide con el código y cualquiera del grupo puede rehacerlo con calculadora |
| 2 | 26 oct-1 nov | Paraxial frente a vectorial y aberraciones (A4, A5, E5, E6) · simulación interactiva (A6, E3) · extras | las gráficas finales están en `figuras/`, la discusión está escrita y alguien que no programó la simulación puede usarla |
| 3 | 2-8 nov | Póster (E1) · ensayo de la defensa · revisión cruzada | póster exportado; cada integrante explica su parte en dos minutos y responde preguntas |

## Extras para el jurado (en orden de prioridad)

1. **Teoría de tercer orden frente a la simulación.** El coeficiente de $\Delta y \propto h^2$ que da el trazado se compara con la fórmula analítica de la aberración esférica (Seidel). Si coinciden, el código y la teoría se validan mutuamente.
2. **Forma óptima de la lente.** Con la misma focal, variar el reparto de curvatura entre las dos caras y encontrar la forma con menos aberración; contrastarla con el resultado clásico de los libros.
3. **Lentes asféricas.** Buscar la constante cónica que anula la aberración. Conecta con las lentes de las cámaras de los celulares y con el telescopio Hubble: en 1990 su espejo principal salió con constante cónica -1.0139 en lugar de -1.0023 y quedó con aberración esférica ([STScI](https://www.stsci.edu/instrument-news/handbooks/wfpc2/W2_47.html)).
4. **Diagramas profesionales.** Abanico de rayos (error transversal frente a altura), cáustica y círculo de mínima confusión: los mismos gráficos que usa el software de diseño óptico.
5. **Frente de onda y límite de difracción.** Camino óptico de cada rayo (principio de Fermat) → error del frente de onda; comparar el desenfoque geométrico con el disco de Airy y decidir cuándo la lente está "limitada por difracción". Une los temas 6.3.1 y 6.3.6 del curso.
6. **Simulación web con un código QR en el póster**, para que el jurado la pruebe desde su celular.
7. **Experimento (opcional).** Prueba de Hartmann con una lupa, un láser o LED y una máscara de cartón con agujeros a distintas alturas: medir dónde cruzan los rayos y compararlo con la simulación.

## Reparto propuesto

| Integrante | Parte que defiende |
|---|---|
| Diego Atoche | Deducción vectorial (A1, A2) |
| Angel Farro | Ejemplo resuelto (A3) |
| Fernando Guillén | Paraxial y aberraciones (A4, A5) |
| Oswaldo Alejandro Quispe | Simulación y póster (A6, E1) |

## Riesgos

- El formato del póster se conoce recién la próxima semana → preparar primero contenido y figuras (vectoriales, en `figuras/`), que sirven para cualquier tamaño.
- Sin fecha exacta → mantener el calendario de tres semanas; si la fecha llega antes, se recortan extras, no requisitos.
- Sin rúbrica oficial → la matriz de cumplimiento cubre cada requisito del enunciado y la rúbrica interna, lo demás.
