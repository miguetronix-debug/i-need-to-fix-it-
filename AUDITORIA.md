# Auditoría técnica · 5 de agosto de 2026

Revisión completa del app tras cerrar el bilingüe. Lo que sigue está ordenado por
lo que yo arreglaría primero, no por gravedad teórica.

---

## Estado actual

| | |
|---|---|
| **Pruebas automáticas** | 6 suites, todas en verde |
| **Contenido** | 10 pasos · 77 decisiones · 4 925 opciones · 148 alertas · 26 reglas de coherencia · 29 derivados · 94 preguntas de examen |
| **Datos AO** | 695 códigos · 604 figuras · 48 referencias |
| **Casos por fallo** | 10 |
| **Idiomas** | español e inglés, completos |
| **Peso** | `index.html` 1,5 MB · sitio publicado 14 MB · repositorio 36 MB |
| **Publicado** | ineedtofixit.vercel.app, con despliegue automático desde GitHub |

Las seis suites: `validar.py` (integridad del contenido), `probar.js` (60 casos de
lógica clínica), `probar_render.js` (15 puntos de render), `probar_kfuri.js`
(cuadrantes y abordajes), `probar_idioma.js` (bilingüe, ~45 comprobaciones) y
`probar_sw.js` (service worker).

---

## Lo que arreglaría, por orden

### 1 · El arranque descarga 1,5 MB antes de mostrar nada · **alto impacto**

**Qué pasa.** Todo el contenido va incrustado en `index.html`: 1,44 MB de JSON,
de los cuales **el Paso 2 solo son 32 112 palabras** —el 60 % del contenido del
app— y las traducciones inglesas otros 371 KB. Un residente en el móvil, con
datos móviles del hospital, espera a que baje todo eso aunque solo quiera abrir
el Paso 3.

**Por qué está así.** Fue una decisión deliberada y correcta al principio: un
archivo único que se abre con doble clic, sin servidor. Esa razón desapareció el
día que se publicó en Vercel.

**Cómo lo arreglaría.** Sacar el compendio AO (`codigos`) y las traducciones a
archivos aparte y cargarlos bajo demanda: el compendio solo cuando se entra al
Paso 2, el inglés solo si el idioma es inglés. El HTML bajaría de 1,5 MB a unos
250 KB. El service worker ya está preparado para cachearlos. **Es el cambio con
mejor relación beneficio/riesgo de toda la lista.**

### 2 · Accesibilidad: cero atributos ARIA y foco apenas visible · **alto impacto**

**Qué pasa.** El app tiene **0 atributos `aria-`** y **una sola regla `:focus`**.
Las opciones son `<button>` —bien— pero nada indica cuáles están seleccionadas a
un lector de pantalla, y navegar con teclado es prácticamente a ciegas.

**Por qué importa aquí.** No es una casilla de cumplimiento: es un app que se usa
de pie, con guantes, con el móvil en una mano. El foco visible ayuda a cualquiera,
no solo a quien usa lector de pantalla.

**Cómo lo arreglaría.** `aria-pressed` en cada opción seleccionable, `role="alert"`
en las alertas críticas, `aria-live` en el bloque de avisos para que un cambio se
anuncie, y un `:focus-visible` con contorno claro. Es media tarde de trabajo y no
toca la lógica.

### 3 · 27 `onclick` en línea y 11 `innerHTML` completos · **medio**

**Qué pasa.** Cada render reconstruye bloques enteros de HTML y vuelve a crear
todos los botones. En el Paso 2, con 4 592 opciones, eso se nota al escribir en el
buscador.

**Cómo lo arreglaría.** Delegación de eventos: un único escuchador en `#decs` que
lea `data-dec` y `data-opt`. Y render incremental en las listas largas. **Esto es
exactamente la «deuda técnica de la Tanda 3» que quedó anotada y sigue abierta.**

### 4 · El JSON viaja como literal JavaScript, no como datos · **medio, seguridad**

**Qué pasa.** El generador escribe `const DATA={...}` dentro de un `<script>`.
Hoy es seguro porque hay un escape de `</` que evita cerrar la etiqueta, pero es
una defensa frágil: depende de que nadie toque esa línea.

**Cómo lo arreglaría.** `<script type="application/json">` más `JSON.parse`. El
navegador entonces trata el bloque como datos y no como código, y el riesgo
desaparece por construcción en vez de por vigilancia.

### 5 · Sin archivo de licencia · **bajo, pero conviene cerrarlo**

El repositorio es público y no tiene `LICENSE`. El aviso legal del app dice lo
correcto sobre la AO/OTA —uso educativo permitido, comercial requiere permiso—
pero no dice nada sobre **tu** contenido, que es el 90 % del trabajo. Sin licencia
explícita, quien lo encuentre no sabe si puede usarlo en su servicio.

Recomendación: licencia Creative Commons BY-NC-SA para el contenido —permite
enseñar con él, exige atribución, prohíbe el uso comercial, y obliga a compartir
las mejoras igual—, y una nota separada aclarando que la clasificación AO/OTA
tiene su propia licencia.

### 6 · Fragilidades del método de trabajo, ya conocidas

Tres cosas que ya nos mordieron y conviene tener presentes:

**Las traducciones se emparejan por posición donde no hay `id`.** Bloques de
texto, reglas derivadas y preguntas de examen. Si se inserta un bloque en medio
del español sin ajustar el inglés, todo lo que sigue se desplaza. La prueba lo
detecta porque encuentra español suelto, pero conviene saberlo antes de editar.

**Las reglas de las clasificaciones regionales ya no se mantienen a mano**: se
generan en inglés con la misma fórmula que en español, desde `clasificaciones.json`.
Eso se corrigió hoy, después de que la versión posicional se desalineara.

**El service worker puede congelar a un usuario en una versión antigua.** Pasó
hoy: la versión del caché era la fecha, así que dos publicaciones el mismo día
generaban un `sw.js` idéntico. Ahora la versión es una huella del contenido y el
app se sirve a red primero. `probar_sw.js` vigila que no vuelva.

---

## Lo que está bien y conviene no tocar

**La separación contenido/código.** Es lo que ha permitido todo lo demás: añadir
un idioma fue crear un JSON, no reescribir el motor. Corregir a Kfuri fue editar
`clasificaciones.json`, no buscar cadenas en el código.

**Las pruebas cazan errores clínicos, no solo técnicos.** La biblioteca de casos
por fallo funciona como invariante: «el plan corregido no debe dejar alertas
graves». Eso destapó cuatro fallos del motor y uno de contenido donde el app
penalizaba una práctica correcta. Ninguna prueba unitaria convencional lo habría
visto.

**El validador cruzado.** Comprueba que toda condición apunte a decisiones y
opciones que existen. Hoy mismo cazó una referencia huérfana al borrar un
abordaje.

**El inglés del compendio AO no es traducción.** Es el documento original de la
AO, que ya estaba dentro. 80 de los 85 segmentos salen de ahí, no de mí.

---

## Lo que sigue pendiente del producto

- **Verificar en un móvil** que el arreglo del service worker llega: borrar el
  icono, recargar, volver a añadirlo. Es lo único que no puedo comprobar yo.
- **Los enlaces de caso compartidos**: nunca se probaron en dos dispositivos.
- **El manual de usuario en PDF**, con 19 capturas ya tomadas y el guion escrito
  en `manual/PENDIENTE.md`.
- **El nombre y el dominio** siguen sin verificarse como marca.
- **Material del libro sin sitio en el app**: postoperatorio y rehabilitación
  (410 palabras) y escenarios especiales (375).

---

## Si tuviera que elegir tres cosas

1. **Partir el contenido y cargarlo bajo demanda.** Es lo que más nota el usuario.
2. **Accesibilidad básica.** Media tarde, cero riesgo, beneficio para todos.
3. **Poner una licencia.** Cinco minutos, y sin ella el trabajo queda en un limbo
   legal justo cuando empieza a circular.
