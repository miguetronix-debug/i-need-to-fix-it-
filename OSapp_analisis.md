# OSapp de la AO — qué es, qué hace bien, y qué nos llevamos

**Revisado el 4 de agosto de 2026** · https://osapp.aofoundation.org
Recorrido: Free Configurator, los 7 casos, el índice de lecciones y la ficha del equipo.

---

## Qué es

**OSapp = Osteosynthesis app.** Es un simulador biomecánico gratuito del AO Research Institute, con dirección médica de un comité (Schuetz, Babst, Gebhard, Lambert, Jäger) e ingeniería de Varga y Gueorguiev en Davos. Tiene tres piezas:

1. **Free Configurator** — un laboratorio. Configuras fractura (localización, tipo, tamaño de brecha, estado de consolidación), placa (material, tipo y número de agujeros, elevación sobre el hueso, tipo de tornillo, **y qué agujeros llenas**) y carga. Pulsas *Evaluate* y una simulación de elementos finitos pinta el estrés sobre el modelo 3D y mueve un marcador en una barra de **Mean Gap Strain** de 0 a 100 %.
2. **Lecciones guiadas** — Basics, fijación interna, fijación externa y contenido especial, en formato de libro digital con modelos 3D incrustados.
3. **Casos** — 7 discusiones de casos clínicos **fallidos**, simulados y resueltos virtualmente.

---

## Lo que hace brillantemente

### 1 · Convierte la fórmula de Perren en una sensación

Esto es lo importante. Cambias un parámetro, pulsas *Evaluate*, y el marcador de deformación se mueve. No estás leyendo que la deformación es movimiento dividido entre brecha: lo estás viendo. Un residente que juega veinte minutos con eso entiende el Paso 3 mejor que leyéndolo tres veces.

### 2 · Los casos están construidos sobre fallos, no sobre éxitos

Los siete casos son complicaciones: *«Wrong plate working length»*, *«Wrong working length with large fracture gap»*, *«Femoral shaft fracture: hypertrophic non-union»*, *«Lack of far cortical support»*. Y todos siguen la misma estructura de tres tiempos:

| Tiempo | Qué muestra |
|---|---|
| **El caso** | Radiografía real del fallo, con la fuente citada |
| **Por qué falló** | El mismo montaje simulado en 3D, con el estrés en rojo y verde |
| **La resolución** | El montaje corregido **encima** del fallido, lado a lado, más un *«Take home message»* de una línea |

Ver los dos constructos uno sobre otro es la mitad del valor pedagógico.

### 3 · Es honesto sobre los límites de su propio modelo

En medio de un caso avisan: *«el modelo muestra solo dos tornillos en un fragmento, lo cual no es buena práctica y se usa aquí únicamente para ilustrar la idea»*. Esa honestidad es rara y es exactamente el tono que queremos.

### 4 · Valida nuestro contenido

Al quitar los tornillos vecinos al foco, OSapp lanzó un aviso: **«Using at least three screws per fragment is recommended»**. Es literalmente la regla que pusimos en el Paso 3 a partir de Stoffel. Confirmación independiente de que las cifras que metimos son las correctas.

### 5 · El widget de configuración de tornillos

Una tira de ocho agujeros que se encienden y apagan con un clic. Convierte la longitud de trabajo y la densidad de tornillos en algo que se toca en lugar de un número que se lee. Es la mejor idea de interfaz de todo el producto, y es la más barata de copiar.

---

## Sus límites — y por qué somos complementarios, no competencia

| Lo que OSapp no hace | Lo que nosotros ya hacemos |
|---|---|
| No hay paciente: ni fisiología, ni partes blandas, ni tiempos quirúrgicos | Paso 1 completo |
| No hay clasificación | Paso 2, con 695 códigos y 506 figuras |
| Solo modela **diáfisis sobre un cilindro**: no existe el bloque articular ni el constructo de dos zonas | Es justo el eje del Paso 3 |
| No hay reducción, ni posición, ni abordaje, ni complicaciones | Pasos 4, 7, 8, 9 y 10 |
| **No produce un plan.** Se entra a experimentar y se sale sin decisión | El plan consolidado es nuestro producto |
| Solo en inglés | Nuestro objetivo es el residente hispanohablante |

Dicho en una línea: **OSapp es un microscopio sobre la mitad de nuestro Paso 3 y parte del 5 y el 6.** Profundiza donde nosotros tenemos que decidir. No cubre el método; lo ilumina en un punto.

Y hay algo estructural: ellos enseñan **por qué funciona la mecánica**, nosotros enseñamos **cómo se decide**. Un simulador no te dice si operar hoy o esperar la ventana de partes blandas.

---

## Cómo lo incorporamos

Tres ideas son portables. Ninguna exige elementos finitos.

### A · Los casos por fallo — y aquí tenemos una ventaja que ellos no tienen

Esto cambia lo que teníamos previsto en la Tanda 2. Yo había propuesto diez casos *resueltos*. **El patrón de OSapp es mejor: casos construidos sobre el error.**

Y hay algo que nosotros podemos hacer y ellos no: **nuestro caso ya es un enlace**. Como el estado del caso viaja en la URL, un caso de la biblioteca no necesita motor nuevo — es un estado precargado con las decisiones equivocadas, y el propio app dispara sus alertas críticas explicando el fallo. Después, un segundo enlace con el estado corregido.

```
Caso 3 · «Placa puente sobre trazo simple»
  ├─ Enlace 1 → 42A + estabilidad relativa + placa larga sin longitud de trabajo
  │             el app dispara solas dos alertas críticas
  ├─ Radiografía del fallo real (fatiga de la placa en un agujero vacío)
  └─ Enlace 2 → el mismo caso con compresión, o con longitud de trabajo ampliada
```

Cero código nuevo. El motor que ya tenemos *es* el «por qué falló».

### B · El widget de la tira de tornillos

Copiable en unas sesenta líneas y sin simulación: los tres números que enseñamos son aritmética pura.

- Relación de cobertura = longitud de placa / longitud de fractura
- Densidad de tornillos = tornillos colocados / agujeros
- Longitud de trabajo = distancia entre los tornillos más internos

El residente enciende y apaga agujeros y ve los tres números en vivo, con el objetivo de Gautier y Sommer al lado en verde o en rojo. Convierte nuestro Paso 3 de una lista de criterios en algo que se manipula.

### C · Enlazar, no reconstruir

Desde las palancas del Paso 3 y desde los principios del Paso 5, un enlace: *«compruébalo en el simulador de la AO»*. Es gratuito, es de la AO, y citarlo nos suma credibilidad en lugar de restarla. Lo que no debemos hacer es intentar competir con una simulación de elementos finitos hecha por un instituto de investigación.

### D · Dos detalles menores que valen la pena

- **Términos con definición en línea.** OSapp resalta *working length* o *stresses* dentro del texto y los abre. Nosotros vamos a construir un glosario de todas formas para traducir el compendio: el mismo glosario puede alimentar esto.
- **«Take home message».** Ya tenemos `sintesis` en cada paso, pero está enterrada al final del plan en gris pequeño. Merece el mismo peso que le dan ellos.

---

## Lo que NO deberíamos hacer

**No construir simulación.** Es un instituto de investigación con ingenieros dedicados y financiación propia. Ese terreno está perdido y además no es el nuestro.

**No copiar sus modelos ni sus figuras.** Enlazar sí; reproducir no.

**No ampliar hacia la biomecánica pura.** Nuestra ventaja es que somos el único sitio donde el razonamiento va del paciente al plan. Cada paso que damos hacia el laboratorio nos aleja de eso.

---

## Recomendación

Adoptar **A** y **B**, enlazar en **C**.

De los tres, **A es el de mayor retorno**: cierra la carencia pedagógica más grave que detectamos —no hay ni un caso resuelto de principio a fin—, usa un patrón ya validado por la AO, y en nuestra arquitectura cuesta escribir texto, no código.

## Fuentes

- [OSapp — plataforma](https://osapp.aofoundation.org/)
- [OSapp — About y comité asesor](https://osapp.aofoundation.org/about/)
- [Beyond Textbooks: Interactive Learning of Biomechanical Principles of Osteosynthesis with an Online Tool for Orthopaedic Residents — *Journal of Surgical Education*](https://www.sciencedirect.com/science/article/pii/S1931720424004987)
