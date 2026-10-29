# Registro de decisiones

Cada decisión que cambia el modelo, las convenciones o la forma de trabajar queda escrita aquí, con su contexto y sus consecuencias. Sirve para que cualquiera del grupo (o del jurado) entienda por qué el proyecto es como es.

| # | Decisión | Estado |
|---|---|---|
| [0001](0001-eje-optico-y-sentido-de-la-luz.md) | El eje óptico es el eje $y$ y la luz viaja en $+y$ | aceptada |
| [0002](0002-normal-y-snell-vectorial.md) | La normal se orienta hacia el medio de incidencia; Snell en forma vectorial | aceptada |
| [0003](0003-caras-conicas-o-formula.md) | Las caras son cónicas o cualquier fórmula en $x$ | aceptada |
| [0004](0004-python-entorno-fijado-y-paquete.md) | Python 3.12 con versiones fijadas y la física en un solo paquete | aceptada |
| [0005](0005-figuras-solo-por-codigo.md) | Las figuras solo se generan con código | aceptada |
| [0006](0006-validar-contra-teoria.md) | Todo resultado se valida contra un límite analítico | aceptada |
| [0007](0007-simulacion-web-en-javascript.md) | La simulación web es el trazador traducido a JavaScript y se valida contra Python | aceptada |
| [0008](0008-poster-en-html-a-tamano-real.md) | El póster es una página HTML a tamaño real sobre la plantilla de UTEC | propuesta |

## Plantilla para una decisión nueva

Copiar en `NNNN-titulo-corto.md` (número siguiente, nombre sin tildes) y agregar una fila a la tabla.

```markdown
# NNNN · Título en una línea

- **Fecha:** AAAA-MM-DD
- **Estado:** propuesta | aceptada | reemplazada por NNNN

## Contexto
Qué problema o pregunta obliga a decidir.

## Decisión
Qué se decidió, en concreto.

## Consecuencias
Qué cambia, qué se gana y qué se pierde.

## Alternativas consideradas
Qué otras opciones había y por qué no se eligieron.
```
