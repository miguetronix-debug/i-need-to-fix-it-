# Mejoras de experiencia y aprendizaje — septiembre de 2026

Esta entrega aplica al proyecto existente las mejoras de navegación, registro del razonamiento y aprendizaje del documento de revisión. Conserva el motor clínico, las clasificaciones, las preguntas, las referencias y las imágenes originales. No añade recomendaciones clínicas ni puntuaciones de competencia.

## Incluido

| Área | Comportamiento |
|---|---|
| Inicio | Tres caminos: resolver un caso, estudiar y autoevaluarse; acceso para continuar y guía breve de primera visita. |
| Diez pasos | Mapa con pendiente, en progreso, decisiones registradas y revisar tras un cambio; navegación con botones accesibles. |
| Caso educativo | Contexto libre sin identificadores, notas de datos, interpretación, justificación y preguntas pendientes. |
| Incertidumbre | Opción de información insuficiente: permite continuar y conserva las preguntas pendientes en el plan. |
| Revisión | Cambiar una elección marca los pasos posteriores trabajados. El usuario confirma su revisión; se conservan las decisiones anteriores hasta revisarlas. |
| Plan | Decisiones, notas y pendientes; edición por paso, copia e impresión; enlace docente que incluye únicamente opciones, sin contexto ni notas. |
| Estudio | Desarrollo abierto en modo estudio; filtros para tablas, conceptos y errores; marcar lectura. |
| Biblioteca | Búsqueda por palabras en los bloques y tablas de los diez pasos, filtros de tipo y apertura en el paso de origen. Acceso al buscador AO/OTA existente. |
| Autoevaluación | Entrada independiente con las 94 preguntas originales, explicación, repaso de errores e intentos por paso. No modifica el caso activo. |
| Progreso | Lecturas y estadísticas basadas en la última respuesta de cada pregunta. No se equipara completar contenido con dominarlo. |
| ES / EN | Las nuevas etiquetas están en `content/interfaz.json`. El cambio de idioma conserva las respuestas del bloque. Los casos por fallo originales permanecen en español y se indica. |
| Accesibilidad | Navegación mediante botones, foco visible, estados de selección, regiones de estado y salto al contenido. CSS adaptado a móvil y preferencias de movimiento reducido. |
| Difusión | Portada legible sin ejecutar JavaScript, metadatos para compartir, URL canónica y sitemap de la página principal. |

## Correcciones de integridad

- Cancelar Reiniciar no borra el paso actual.
- Recuperar un caso vuelve a vincular las decisiones activas al objeto guardado.
- Recargar la URL del caso propio conserva las notas; un enlace diferente no incorpora notas del caso local.
- Las decisiones inválidas y estructuras de almacenamiento malformadas se normalizan al recuperar.
- No se consideran completos los pasos por el simple hecho de contener una elección.
- Las opciones que ya no encajan se señalan para revisión y permanecen en el registro hasta revisar el paso.
- El texto libre se escapa antes de incluirlo en HTML y nunca se introduce en enlaces docentes.
- Si el navegador rechaza el guardado, la app lo comunica; no afirma que los datos se hayan guardado.
- Las respuestas del examen siguen mostrando su explicación tras cambiar idioma.

## Validación

El generador sigue siendo `python3 tools/build_prototipo.py`; `python3 tools/publicar.py` prepara `sitio/`, sin desplegarlo. Los módulos de experiencia se incrustan en el HTML autónomo para conservar el uso sin conexión.

Pruebas requeridas:

```bash
python3 tools/validar.py
node tools/probar.js
node tools/probar_render.js
node tools/probar_descripcion.js
node tools/probar_idioma.js
node tools/probar_casos.js
node tools/probar_sw.js
node tools/probar_experiencia.js
```

`probar_experiencia.js` contiene 28 pruebas de regresión de recuperación, cancelación, incertidumbre, revisión, búsqueda, idioma, persistencia e historial. Evalúa el JavaScript generado y los manejadores de interacción. Estas son pruebas automáticas con DOM simulado; no sustituyen una revisión visual en dispositivos reales.

## Alcance y siguiente iteración

1. **Validar comprensión con usuarios:** probar con 5–8 residentes y especialistas si encuentran la entrada adecuada, completan un caso, explican una alerta y retoman su progreso. Medir tiempo al primer caso y puntos de abandono antes de fijar objetivos cuantitativos.
2. **Casos progresivos:** redactar y revisar casos que revelen información por etapas. Requiere definir qué datos y respuestas se aceptan en cada etapa. Esta entrega no convierte las respuestas originales en nuevas reglas clínicas.
3. **Imágenes interactivas:** reutilizar imágenes revisadas y autorizadas con anotaciones e identificación de hallazgos. Las imágenes originales permanecen disponibles; no se agregan radiografías ficticias ni nuevas anotaciones médicas.
4. **Evaluación del razonamiento:** añadir explicaciones por distractor y admitir alternativas justificadas mediante una rúbrica revisada por el autor. La entrega reutiliza la explicación global existente de cada pregunta.
5. **Repetición espaciada y varios casos:** añadir una agenda de repaso y un archivo de casos educativos. Actualmente se guarda un caso activo con varias lesiones, sus notas y el historial de aprendizaje en el navegador.
6. **Alcance docente:** preparar un caso de demostración para clases, enlaces o QR hacia contenidos revisados y una guía para profesores. Los enlaces actuales comparten selecciones, no imágenes ni notas.
7. **Páginas públicas por tema:** crear páginas ES/EN con URL propia, contenido revisado y enlaces internos. El sitemap actual describe solo la portada; no representa cada paso como una página independiente.
8. **Sincronización:** decidir si se necesitan cuentas y acceso entre dispositivos antes de incorporar un servicio de datos. El almacenamiento actual puede borrarse al limpiar el navegador y no ofrece copia remota.
9. **Uso sin conexión:** se conserva el mecanismo existente. Las imágenes se guardan al consultarlas; no se promete que toda la biblioteca visual esté descargada desde la primera visita.

La propuesta se entrega como cambios revisables en GitHub. La web de Vercel se actualizará cuando estos cambios se integren en la rama conectada a su despliegue.


## Corrección: varias fracturas en el mismo caso

- El panel **Lesiones de este caso**, visible durante el recorrido de los pasos, permite añadir fracturas y cambiar la lesión activa.
- Al clasificar radio, cúbito, tibia o peroné aparece un acceso para añadir su hueso asociado. Solo se preselecciona el hueso: el usuario elige el segmento y el patrón de cada fractura.
- Cada lesión conserva por separado lado, clasificación, decisiones de los diez pasos, notas y pendientes. El contexto escrito del caso es común. La evaluación inicial también pertenece a cada lesión; no se copian decisiones automáticamente.
- El plan conjunto reúne las lesiones e incluye enlaces para editar el paso de cada una. Copia e impresión incluyen todas las lesiones; el enlace docente comparte únicamente opciones y lado.
- Los casos guardados en la versión anterior se recuperan como una sola lesión. Eliminar una lesión pide confirmación y conserva las demás.
- Las alertas se calculan con el contexto de la lesión activa. Esta entrega no introduce reglas sobre interacciones entre lesiones ni genera una estrategia conjunta automática.
- Se corrige el buscador para reconocer segmentos con letras (2R2, 2U2, 4F2); antes se cortaban en la primera letra.
- Diez regresiones nuevas verifican radio/cúbito, tibia/peroné, aislamiento de alertas y notas, restauración, migración, borrado, enlaces docentes y traducción. Son 28 pruebas de experiencia en total.
