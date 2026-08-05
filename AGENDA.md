# Agenda de trabajo — «I Need To Fix It»

Iniciada el 4 de agosto de 2026 · **Tanda 1 cerrada el 4 de agosto de 2026**, a partir de la evaluación del app.
Criterio de reparto: **todo lo que sea ingeniería, diseño o mecánica lo hago yo sin consultar; solo te paso lo que exija criterio clínico tuyo.**

---

## Tanda 1 · Lo hago yo, ahora mismo

| # | Tarea | Estado |
|---|---|---|
| 2 | Persistencia en `localStorage` — el caso sobrevive al cierre del navegador | ✅ |
| 5 | Ocultar el Paso 10 mientras no exista | ✅ |
| 6 | Contraste `--ink3` a nivel AA y cadena de versión generada del contenido | ✅ |
| 1 | **Plan consolidado de los 9 pasos**, con copiar e imprimir | ✅ |
| 4 | Separar «Principio del paso» de las alertas reales | ✅ |
| 12 | Botón «por qué» en cada alerta, que abre el desarrollo | ✅ |
| 9 | Estado del caso en la URL — compartir y retomar | ✅ |
| 7 | Buscador en el Paso 2 por código o por nombre | ✅ |
| 11 | Modo examen con puntuación, historial y repaso de lo fallado | ✅ |
| 10 | PWA: manifest, service worker y figuras en caché | ✅ |

## Tanda 2 · Lo preparo yo, lo revisas tú

| # | Tarea | Qué necesito de ti |
|---|---|---|
| 3 | Traducir las descripciones AO | ✅ **Hecho.** 665 descripciones compuestas desde un glosario de 489 fragmentos. Para revisar: `REVISION_glosario.md`, ordenado por frecuencia — los 40 primeros cubren la mitad del texto. |
| 8 | Biblioteca de casos por fallo | ✅ **Hecho y revisado.** Diez casos, cada uno sobre un error distinto del método. |

## Tanda 2b · A partir de OSapp (revisado el 4 de agosto de 2026)

| Idea | Estado |
|---|---|
| **B** · Tira de tornillos interactiva en el Paso 3 — cobertura, densidad, tornillos por fragmento y longitud de trabajo en vivo | ✅ |
| **C** · Enlaces al simulador de la AO desde los pasos 3, 5 y 6 | ✅ |
| **A** · Maquinaria de casos por fallo: `casos.json`, biblioteca, carga del estado erróneo y del corregido | ✅ |
| **A** · Los 10 casos escritos y revisados por el autor | ✅ |

Los diez, cada uno enganchando un error distinto del método: placa puente sobre trazo simple (42A), comprimir la metáfisis conminuta (41C), banda de tensión sin cortical opuesta (2U1), operar el pilón sin ventana (43C), placa sobre vástago suelto (Vancouver B2), reducir la superficie por ligamentotaxis (33C), puentear el bloque articular (13C), pared posterior en supino (62B), comprimir la sindesmosis (44C) y cirugía definitiva en un inestable (politrauma).

Escribirlos destapó cuatro fallos del motor que la prueba automática cazó: una regla de abordaje que reclamaba la vía aunque ya estuviera elegida, dos alertas que usaban `ctx` como Y cuando es una lista alternativa, y la falta de una opción para decir «el implante es un vástago de revisión».

## Tanda 2c · Clasificaciones regionales (4 de agosto de 2026)

Criterio de entrada acordado: **que cambie el manejo, el abordaje o el pronóstico.**
La concordancia interobservador NO filtra: se muestra en la propia pregunta, porque saber que Neer tiene kappa 0,30 forma parte de saber usarla.

| Clasificación | Región | Qué decide | ✅ |
|---|---|---|---|
| Schatzker modificada por Kfuri | Meseta 41 | Tipo e implante, y columna para el abordaje | ✅ |
| Garden, dicotomizada | Cuello 31 | Fijar o protetizar | ✅ |
| Pauwels | Cuello 31 | Cizallamiento → ángulo fijo | ✅ |
| Neer | Húmero prox. 11 | Vocabulario y umbrales | ✅ |
| Hertel | Húmero prox. 11 | Isquemia de la cabeza | ✅ |
| Hawkins | Astrágalo 81 | Necrosis y urgencia | ✅ |
| Sanders | Calcáneo 82 | Abordaje y artrodesis | ✅ |
| Letournel-Judet | Acetábulo 62 | El abordaje | ✅ |
| Young-Burgess | Pelvis 61 | Sangrado y reanimación | ✅ |
| Tile | Pelvis 61 | Fijación posterior | ✅ |
| Vancouver | Periprotésica | Revisar o fijar | ✅ |
| Winquist-Hansen | Diáfisis fem. 32 | Estático o dinámico | ✅ |
| Mason | Cabeza radial 2R1 | Fijar, protetizar, reparar | ✅ |
| Lauge-Hansen | Maleolar 44 | Maniobra de reducción | ✅ |

Excluida por no cambiar el manejo: Frykman. Superadas por la AO 2018: Evans y Jensen (el concepto de pared lateral ya está en 31A).

**Para revisarlas:** `REVISION_clasificaciones.md`, generado con `tools/hoja_revision.py`. En el app cada una solo aparece en su región, así que revisarlas ahí es imposible.

## Tanda 2d · Paso 10 (4 de agosto de 2026)

| Tarea | Estado |
|---|---|
| Paso 10 · Las complicaciones — 4 decisiones, 28 opciones, 10 alertas, 8 preguntas | ✅ |
| Los hechos de pronóstico de las clasificaciones aterrizan en el Paso 10 | ✅ |
| `emite` en Pasos 1 y 6 para que el 10 sepa si es abierta, osteoporótica o de carga soportada | ✅ |

**El método está completo: los diez pasos en el app.**

Sigue sin sitio el material del libro sobre postoperatorio y rehabilitación (410 palabras) y escenarios especiales (375).

## Tanda 2e · Traducción del compendio (4 de agosto de 2026)

| Tarea | Estado |
|---|---|
| Glosario de 489 fragmentos, con cobertura completa del corpus | ✅ |
| 665 de 684 descripciones compuestas en español | ✅ |
| 19 códigos sin descripción: solo traían texto instructivo del compendio | ✅ |
| El app sirve el español y conserva el inglés como respaldo | ✅ |
| Glosario revisado y aprobado por el autor | ✅ |

El inglés no se pierde: queda en `texto` y el español en `texto_es`. Corregir una entrada del glosario y volver a ejecutar `tools/traducir_ao.py` recompone las 665 descripciones.

## Tanda 3 · Deuda técnica, cuando el producto esté cerrado

- Render incremental en vez de `innerHTML` total.
- Delegación de eventos con `data-*` en lugar de `onclick` en línea.
- `aria-pressed` y foco visible en las opciones.
- Agrupación visual de las multiselección largas (Paso 3 por implante, Paso 8 por región).

---

## Regla de trabajo

Cada tanda termina con `validar.py` sin errores y `probar.js` en verde antes de darla por cerrada.
