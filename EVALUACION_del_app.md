# Evaluación del app «I Need To Fix It»

**Fecha:** 4 de agosto de 2026 · **Versión auditada:** prototipo.html, 1,03 MB, pasos 1-9
**Perspectivas:** pedagogía médica · ingeniería de software · diseño de producto

---

## Veredicto en una línea

El contenido y el motor de razonamiento están por encima de lo que se ve en el mercado; **el producto todavía no existe**. Hoy es un excelente simulador de método y un mal instrumento de trabajo, y la distancia entre las dos cosas es más corta de lo que parece.

---

## 1. Lo que está bien, y por qué no es trivial

### El motor razona de verdad

La mayoría de las apps de trauma son árboles de decisión: preguntan, y al final muestran una recomendación. Aquí hay algo distinto: **el app detecta incoherencias entre decisiones tomadas en pasos diferentes**. Si en el Paso 3 se elige estabilidad relativa y en el Paso 5 se elige comprimir, salta una alerta crítica. Si en el Paso 5 se elige ferulaje y en el Paso 8 un abordaje extenso, el app dice que el abordaje traiciona la estrategia.

Eso no es un árbol: es un modelo del razonamiento. Y es exactamente lo que un residente no aprende leyendo, porque el libro no le puede decir «lo que acabas de decir contradice lo que dijiste hace tres capítulos».

Los números: **112 alertas y 23 reglas de coherencia** repartidas en nueve pasos, todas con condiciones verificables y validadas automáticamente.

### La separación contenido/código está bien hecha

Los nueve pasos son JSON puro. El motor no sabe de ortopedia: sabe de condiciones. Eso significa que usted puede corregir un criterio clínico sin tocar una línea de JavaScript, y que el día que haya un traductor, un ilustrador o un segundo autor, pueden trabajar sin romper nada.

Es la decisión de arquitectura más importante del proyecto y está tomada correctamente.

### La red de seguridad existe

`validar.py` audita 5 000 referencias cruzadas —que ninguna condición apunte a una opción inexistente, que ninguna alerta sea inalcanzable, que ningún índice de respuesta esté fuera de rango—. `probar.js` ejecuta 26 casos clínicos y comprueba que salgan las alertas que deben salir. Ambos pasan en limpio.

Esto ya ha capturado errores clínicos reales: reglas que apuntaban a un tipo C del peroné que no existe, alertas huérfanas que nunca se habrían mostrado. Sin esa red, esos errores habrían llegado al residente.

### El dataset AO/OTA es completo

695 códigos, 506 figuras recortadas individualmente, descripción encadenada completa. No conozco ninguna app gratuita que tenga esto.

### El diseño visual está bien resuelto

Paleta cálida y sobria, modo oscuro, tipografía del sistema, jerarquía clara, cero decoración gratuita. Se lee bien y no cansa. Para un prototipo generado por script, el nivel es notablemente alto.

---

## 2. Lo que está mal

### 2.1 · Producto — los tres fallos que lo descalifican como herramienta

**No hay persistencia.** El estado vive solo en memoria. Un `F5`, un cierre de pestaña o un móvil que descarga la página en segundo plano, y se pierde todo el caso. Un adscrito planificando una meseta tibial a las once de la noche lo va a sufrir la primera vez, y no habrá una segunda.

**No hay plan consolidado.** El app muestra el plan *de cada paso*, pero al terminar el Paso 9 no existe ningún sitio donde ver las nueve decisiones juntas. Y ese documento —«fractura 41C2, dos zonas, absoluta al bloque y relativa a la metáfisis, anatómica directa arriba y funcional indirecta abajo, compresión más ferulaje, placa bloqueada lateral con densidad 0,4, supino con realce, parapatelar lateral, distractor»— **es el producto**. Es lo que se imprime, lo que se pega en la historia, lo que se discute en la sesión. Ahora mismo no se puede obtener.

**No es una PWA.** Cero `manifest`, cero *service worker*, cero `localStorage`. Además el HTML ya no es autónomo: necesita 12 MB de figuras al lado. Es decir: no se instala, no funciona sin conexión y no se puede llevar al quirófano, que es justo donde haría falta.

### 2.2 · Contenido

| Problema | Magnitud | Impacto |
|---|---|---|
| Descripciones AO en inglés | **601 de 695 códigos** | Es el defecto más visible del app. Un residente panameño navega en español hasta el tipo y de pronto lee *«complete articular, articular simple, metaphyseal multifragmentary»*. Rompe la ilusión de producto terminado. |
| Paso 10 sin contenido | Chip visible, vacío | Promete algo que no está. Peor que no mostrarlo. |
| Fatiga de alertas | 112 alertas, **12 siempre visibles** | En el Paso 9 hay tres alertas que salen siempre, pase lo que pase. El residente aprende en dos sesiones a saltárselas, y con ellas se salta las críticas. |
| Cadena de versión obsoleta | «Paso 1 · agosto 2026» | El aviso legal dice que el contenido es solo del Paso 1. Es falso y, en un aviso legal, importa. |

### 2.3 · Ingeniería

**Re-render total en cada clic.** `render()` reconstruye todo el DOM por `innerHTML` en cada selección. Funciona, pero pierde el foco del teclado, rompe la posición de scroll y anula cualquier transición. En el Paso 2, además, filtra 4 592 opciones en cada pasada.

**`onclick` en línea con IDs concatenados.** Frágil e incompatible con cualquier política de seguridad de contenido. El `esc()` protege el texto, pero los identificadores entran crudos en el atributo.

**Sin rutas ni enlaces profundos.** No se puede compartir un caso, ni marcarlo, ni volver a él. «Mira esta 43C3» es imposible hoy.

**Sin `aria-*` ni gestión de foco.** Las opciones son `<button>`, que es correcto, pero no declaran `aria-pressed`. Un lector de pantalla no distingue seleccionado de no seleccionado.

**Un solo archivo generado por un script de 720 líneas.** Sostenible para nueve pasos; no lo será cuando entren los capítulos regionales.

### 2.4 · Diseño

**Contraste insuficiente.** El gris `--ink3` (#8b8a84 sobre #faf9f7) da **3,29:1**. WCAG AA exige 4,5:1 para texto normal. Afecta a los encabezados de sección, a los chips de paso y al contador de progreso —justamente los elementos de orientación—. Bajarlo a `#6f6e68` lo lleva a ~5:1 sin cambiar el carácter visual.

**Las alertas compiten con las decisiones.** Están debajo del bloque de preguntas y usan el mismo peso visual que el contenido principal. Una alerta crítica debería interrumpir; hoy se lee como una nota al pie de color.

**El progreso no orienta.** «3 de 5 decisiones» dice cuánto falta del paso actual, pero no dónde está uno en el conjunto ni cuánto queda. Los chips superiores no muestran cuáles se completaron.

**Densidad alta en las multiselección grandes.** El nuevo Paso 3 tiene 12 palancas y el Paso 8 tiene 31 abordajes. Sin agrupación visual, la lista se lee como un muro.

---

## 3. ¿A quién le sirve hoy, y cuánto?

### Residente de primer y segundo año — **valor alto**

Es el usuario para el que el app ya funciona. Le da lo que ningún libro le da: consecuencias inmediatas. Elige mal y algo se lo dice, con el argumento. Recorre el método completo en veinte minutos en lugar de en doce capítulos.

*Lo que le falta:* casos resueltos de ejemplo. Aprender un método sin ver ni una vez cómo se aplica de principio a fin es como aprender ajedrez con las reglas y sin partidas. **Es la carencia pedagógica más grave del app.**

### Residente de tercero a quinto — **valor medio**

Ya conoce el método; lo que necesita es afinar. Aquí el nuevo Paso 3 —longitud de trabajo, relación de cobertura, densidad de tornillos— y las estructuras en riesgo del Paso 8 sí le aportan.

*Lo que le falta:* poder guardar sus casos y revisarlos. Y un modo examen: la autoevaluación existe, pero no puntúa, no lleva historial y no repite lo fallado.

### Adscrito — **valor bajo hoy, potencialmente el más alto**

Un cirujano formado no necesita que le enseñen el método. Necesita tres cosas, y el app no da ninguna:

1. **Buscar rápido una clasificación.** Hoy hay que navegar hueso → segmento → tipo → grupo → subgrupo. Él quiere escribir «42B2» o «meseta» y llegar.
2. **Guardar y exportar un caso.** Para la historia, para la sesión, para el reporte.
3. **Enseñar con él.** Es el uso más valioso y el más fácil de habilitar: proyectar el app en la sesión, hacer que el residente decida en voz alta y que el app discuta. Para eso hace falta poder abrir un caso preconfigurado desde un enlace.

**Sin el adscrito, el app no se difunde.** Los residentes usan lo que su jefe usa.

---

## 4. Cómo mejorarlo, en orden

### Ahora — convierte un ejercicio en una herramienta

| # | Qué | Cómo | Esfuerzo |
|---|---|---|---|
| 1 | **Plan consolidado de los 9 pasos** | Pantalla final que recorre `S.porPaso` y compone el plan completo, con las alertas críticas que quedaron abiertas. Botón de copiar e imprimir. | Bajo |
| 2 | **Persistencia** | `localStorage` en cada `pick()`, restaurar al cargar. Veinte líneas. | Muy bajo |
| 3 | **Traducir las 601 descripciones AO** | Traducción automática + revisión suya por bloques. Es lo que más sube la percepción de calidad por unidad de esfuerzo. | Medio |
| 4 | **Sacar de «alerta» lo que no es alerta** | Las 12 `mostrarSiempre` son recordatorios doctrinales, no avisos sobre *este* caso. Muévalas a un bloque «Principio del paso», plegado, encima de las decisiones. Las alertas quedan solo para lo que responde a lo que el usuario acaba de elegir. | Bajo |
| 5 | **Ocultar el Paso 10 hasta que exista** | Una línea. | Trivial |
| 6 | **Arreglar el contraste y la cadena de versión** | `--ink3` → `#6f6e68`; versión generada desde los archivos de contenido. | Trivial |

### Después — convierte una herramienta en un producto

| # | Qué | Por qué |
|---|---|---|
| 7 | **Buscador en el Paso 2** | Campo único que acepte código (`42B2`) o texto (`meseta`, `pilón`). Es lo que convierte al adscrito en usuario. |
| 8 | **Biblioteca de 8-10 casos resueltos** | El método aplicado de principio a fin, con las decisiones ya tomadas y comentadas. Cierra la carencia pedagógica principal. Sugerencia de reparto: 42A espiroidea, 42C conminuta, 41C meseta, 43C pilón, 31A pertrocantérea, 33C fémur distal, 13C húmero distal, 62B acetábulo, 44B maleolar, y una abierta IIIB en control de daños. |
| 9 | **Estado en la URL** | Codificar `S.porPaso` en el *hash*. Habilita compartir, marcar y —sobre todo— que usted mande a un residente un caso preconfigurado. |
| 10 | **PWA de verdad** | `manifest` + *service worker* + figuras en caché. Sin esto no entra al quirófano. |
| 11 | **Modo examen** | La autoevaluación ya existe (86 preguntas). Falta puntuar, guardar historial y repetir lo fallado a los pocos días. |
| 12 | **Enlazar alerta → desarrollo** | Cada alerta debería poder abrir el bloque del desarrollo que la explica. Hoy el «por qué» está en el app, pero a dos clics y sin señalizar. |

### Deuda técnica, cuando toque

- Render incremental en lugar de `innerHTML` total, o adoptar una librería mínima (Preact o Lit, ~5 KB) antes de que entren los capítulos regionales.
- Delegación de eventos con `data-*` en lugar de `onclick` en línea.
- `aria-pressed` en las opciones y foco visible.
- Agrupar visualmente las multiselección largas (Paso 3 por implante, Paso 8 por región).

---

## 5. Lo que yo no haría

**No añadir más pasos ni más contenido antes de cerrar el ciclo.** El app tiene nueve pasos excelentes y ninguna salida. Un décimo paso no mejora esa proporción.

**No perseguir a Surgery Reference en cobertura.** Ellos tienen cientos de técnicas ilustradas y un equipo detrás. Su ventaja no es el catálogo: es que ellos enseñan *qué se hace* y usted enseña *cómo se decide*. Son cosas distintas, y la suya no la cubre nadie. Ampliar hacia el catálogo la diluye.

**No hacer login ni cuentas todavía.** `localStorage` y enlaces compartibles cubren el 90 % del valor con el 5 % del trabajo y sin obligaciones legales sobre datos.

---

## 6. Métricas del estado actual

```
Contenido      9 pasos · 231 opciones útiles (+4 592 de clasificación AO)
               112 alertas · 23 reglas de coherencia · 86 preguntas
Dataset        695 códigos AO/OTA 2018 · 506 figuras recortadas
Código         2 674 líneas (8 scripts Python + 1 de pruebas)
Entregable     prototipo.html 1,03 MB + 12 MB de figuras
Calidad        validar.py sin errores · probar.js 26/26 casos
Accesibilidad  contraste 3,29:1 en texto secundario (AA exige 4,5:1)
Pendiente      Paso 10 · traducción AO · persistencia · plan consolidado
```

---

## Conclusión

Lo difícil ya está hecho, y es la parte que casi nadie consigue: **un modelo computable del razonamiento quirúrgico**, con contenido separado del código, validado y probado. Eso no se improvisa y es lo que da valor al proyecto.

Lo que falta es, casi todo, trabajo de producto y de acabado. Los seis puntos de la lista «Ahora» son pocos días de trabajo y transforman la experiencia: de un ejercicio que se hace una vez a una herramienta que se abre cada semana.

El orden correcto es cerrar el ciclo antes de ampliarlo. Un app que termina en un plan imprimible y recuperable, con nueve pasos, vale mucho más que uno con diez pasos que no termina en nada.
