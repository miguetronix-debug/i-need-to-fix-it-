# Cómo funciona el AO Surgery Reference — y qué copiar para "I Need To Fix It"

**Fecha:** 4 de agosto de 2026 · Evaluación hecha navegando el sitio, no de memoria.
Ruta auditada de punta a punta: tibia proximal → fractura por hundimiento (41-B2) → ORIF con placa convencional.

---

## 1. Su arquitectura, en una línea

```
Esqueleto → Región → Diagnóstico (patrón + código AO) → Indicación (opciones de tratamiento) → Tratamiento
                                                                                                    ↓
                          1/6 Principios · 2/6 Preparación · 3/6 Abordaje · 4/6 Reducción · 5/6 Fijación · 6/6 Postoperatorio
```

Cinco niveles de navegación y, al final, **una sola página con seis capítulos numerados**. Ese último tramo es lo mejor del sitio: el cirujano llega a una hoja de ruta completa y ordenada de una operación concreta.

## 2. Los cinco aciertos que conviene robar

**a) El stepper numerado con nombre.** No dice "siguiente": dice `3/6 – Abordaje`. Sabes cuánto falta y qué viene. Nuestro asistente de 10 pasos ya hace esto, pero el suyo enseña una lección de diseño: **los capítulos tienen nombre de acto quirúrgico**, no de concepto abstracto.

**b) La selección es visual.** Se elige el patrón de fractura y el tratamiento pinchando una ilustración, no leyendo una lista. Para una app de fracturas esto no es cosmético: el reconocimiento del patrón *es* visual.

**c) "Learn more" antes de comprometerse.** Cada opción ofrece una definición previa antes de que elijas. Reduce el miedo a equivocarse de rama y convierte la navegación en aprendizaje.

**d) Los módulos compartidos.** Ésta es la decisión de arquitectura más importante del sitio, y la más fácil de pasar por alto. Los abordajes, las preparaciones, las técnicas básicas y la imagen intraoperatoria **no se repiten en cada fractura**: viven una sola vez y se enlazan desde donde hagan falta (`/proximal-tibia/approach/all-approaches`, `/basic-technique/...`). Un abordaje anterolateral se escribe una vez y lo usan todas las fracturas que lo necesiten.

**e) El postoperatorio es un capítulo, no una nota al pie.** Le dedica el mismo peso que a la fijación: compartimental, profilaxis de TVP, carga, seguimiento, retirada de material.

## 3. Las tres cosas que NO hace — y que son nuestra razón de existir

**No tiene Paso 1.** Entra directo por el hueso. No pregunta cómo está el paciente, ni en qué categoría fisiológica, ni cómo están las partes blandas. Da por supuesto que eso ya se resolvió. Tu libro empieza justo ahí, y ésa es la diferencia de fondo entre una referencia y un método.

**No razona: recita.** Es un árbol: navegas hasta una hoja y lees una receta excelente. No sabe qué elegiste antes, no acumula estado, no detecta contradicciones. Si eliges una vía imposible para ese paciente, no te dice nada, porque no sabe nada del paciente.

**No gradúa la evidencia.** El texto es autoridad experta sin nivel ni referencia numerada. Tu libro sí distingue 1a de 4 y lo etiqueta.

En resumen: **el Surgery Reference es un árbol de referencia; nosotros hacemos un motor de decisión.** No competimos con él, y conviene decirlo así.

## 4. El hallazgo importante: sus seis capítulos SON tus diez pasos

| Surgery Reference | Los 10 pasos |
|---|---|
| Diagnóstico (patrón + código AO) | **Paso 2** · Clasificación |
| Indicaciones — operatorio vs no operatorio | **Paso 2** · Vía de tratamiento |
| 1/6 Principios | **Pasos 3, 4 y 5** · Estabilidad, reducción, principios biomecánicos |
| 1/6 Principios → "potential complications" | **Paso 10** · Complicaciones previsibles |
| 2/6 Preparación del paciente | **Paso 7** · Posición |
| 3/6 Abordaje | **Paso 8** · Abordaje |
| 4/6 Reducción | **Paso 9** · Técnicas de reducción |
| 5/6 Fijación | **Pasos 5 y 6** · Principio e implante |
| 6/6 Postoperatorio | Capítulo de rehabilitación + **Paso 10** |
| *(no existe)* | **Paso 1** · Evaluación del huésped, partes blandas y timing |

Que la referencia mundial de la AO haya convergido en la misma secuencia es la mejor validación externa que puede tener tu método. Y la casilla vacía de arriba —el Paso 1— es literalmente tu aportación.

## 5. Qué cambia en nuestra arquitectura a partir de esto

### 5.1 Biblioteca de módulos compartidos (lo que más urge)

Hoy cada paso guarda su contenido completo. Debe pasar a haber una biblioteca transversal que los pasos **referencian**:

```
content/
├── pasos/            (los 10 pasos del método)
├── biblioteca/
│   ├── abordajes.json     ← anterolateral, posteromedial, Kocher-Langenbeck…
│   ├── posiciones.json    ← supino, decúbito lateral, prono, mesa de tracción…
│   ├── maniobras.json     ← tu Anexo de reducción, ya escrito
│   ├── implantes.json     ← placas, clavos, tornillos, fijadores
│   └── complicaciones.json
└── regiones/         (cuando lleguemos a la Parte II)
```

Ventaja concreta: el abordaje anterolateral de la tibia proximal se escribe una vez y lo usan meseta, pilón y diáfisis. Y tu **Anexo de maniobras de reducción** ya es exactamente esta biblioteca — solo hay que estructurarlo.

### 5.2 Selección visual

Las decisiones de patrón de fractura deberían mostrar un esquema, no solo texto. Empezar por el Paso 2: nueve esquemas por segmento (A1…C3) que se pinchan. Es el punto donde más se gana.

### 5.3 Vista previa antes de elegir

Añadir un "ver más" por opción, con la definición y el criterio, sin salir de la pantalla. Ya tenemos el dato (`criterios` de cada opción); falta el gesto.

### 5.4 Lo que NO copiamos

Su navegación de cinco niveles antes de llegar al contenido. Nosotros entramos por el paciente y llegamos al plan en una sola pasada; ése es el valor del asistente.

---

## 6. Qué se puede extraer del Surgery Reference

Verificado: las páginas de tratamiento se leen íntegras (probado con `ORIF - Conventional plating for Depression fracture`). Cada una entrega principios, preparación, abordaje, reducción, fijación y postoperatorio, con los códigos AO al nivel de subgrupo (`41B3.1`).

Es material excelente para alimentar los pasos 5 a 10 de la Parte II. El coste es el volumen: unas 30 regiones × varios patrones × varios tratamientos = varios cientos de páginas. Propuesta: raspado **región por región**, empezando por meseta tibial, con revisión tuya de cada una — la misma cadencia que ya usamos.

Nota legal: el contenido del Surgery Reference es propiedad de la AO Foundation. Sirve como **fuente para redactar y contrastar**, con cita; no como texto a reproducir literalmente en un producto distribuible.

---

*Evaluación basada en navegación directa del sitio el 4 de agosto de 2026.*
