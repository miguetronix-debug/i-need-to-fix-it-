# Manual del usuario — trabajo en pausa

Aparcado el 5 de agosto de 2026, a medias. Esto es lo que hay hecho y por dónde se retoma.

## Decidido con el autor

- **Lector:** los dos, en secciones separadas — un recorrido para el residente que empieza y una sección corta al final para el adscrito con prisa (modo consulta, plan impreso, casos por fallo para enseñar).
- **Con capturas** de pantalla del app.
- **Formato:** PDF con índice navegable.

## Hecho ✅

**19 capturas** en `manual/capturas/`, tomadas del app real servido por HTTP, en proporción de móvil (430×932, densidad ×2) porque es como se va a usar:

| Archivo | Qué muestra |
|---|---|
| `01-portada` | Cómo se abre: cabecera, modos, fichas de los 10 pasos, Paso 1 |
| `02-pregunta` | Una decisión con sus opciones, sin desplegar |
| `03-criterios` | La misma, con «Ver más» abierto: los criterios de cada opción |
| `04-alerta` | Tres alertas reales de distinta severidad, con el enlace «Por qué» |
| `05-derivados` | Lo que el app deduce solo, sin preguntarlo |
| `06-principio` | El desplegable «Principio del paso» |
| `07-tira` | La tira de tornillos interactiva del Paso 3 |
| `08-buscador` | El buscador del compendio AO con resultados desplegados |
| `09-figura` | La lámina recortada del código construido (41C2.1) |
| `09b-galeria` | La galería de hijos: elegir viendo el dibujo |
| `10-casos` | La biblioteca de casos por fallo |
| `11-caso` | Un caso abierto: qué se hizo, por qué falla, qué tocaba |
| `12-plan` | El plan consolidado de los 10 pasos |
| `13-desarrollo` | El desarrollo largo con tablas (muy alta: hay que recortarla) |
| `14-quiz` | La autoevaluación |
| `15-barra` | La barra inferior: progreso, atrás, reiniciar, plan, siguiente |
| `16-pasos` | La tira de fichas de navegación |
| `17-modos` | El interruptor Consulta / Estudio |
| `18-derivado-ao` | El código AO montado y su descripción en español |

**Cómo se tomaron, por si hay que repetirlas:** Chromium headless de Playwright dentro del entorno, con la librería stub de `libXdamage` en `/tmp/stub` y las variables `LD_LIBRARY_PATH=/tmp/stub PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1`. El sitio se sirve con `python3 -m http.server -d sitio`. La interfaz se dirige llamando a sus propias funciones —`irPaso(n)`, `pick(dec,opt)`, `verCrit(id)`, `irACodigo('41C2.1')`, `cargarCaso(id,'error')`, `verCasos()`, `verResumen()`, `modo('estudio')`— y se captura **por elemento** (`#alerts`, `#tira`, `figure.lam`, `.deriv`, `#quiz`, `.barra`), nunca la página entera: en página completa salen imágenes de 10 000 píxeles de alto, inservibles.

## Falta ⬜

1. **Inventariar** todo lo que el app sabe hacer, para que el manual no se deje nada: los 10 pasos, las 15 clasificaciones regionales, los 10 casos por fallo, el compendio AO en español, las severidades de alerta, las reglas de coherencia, el plan consolidado, el modo examen, los enlaces compartibles, el modo sin conexión y los enlaces a OSapp.
2. **Redactar** las dos secciones.
3. **Generar el PDF** con marcadores e índice de enlaces internos, y verificar que los marcadores existen y que los enlaces saltan a la página correcta.
