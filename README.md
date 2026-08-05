# I Need To Fix It

Asistente metodológico de planificación quirúrgica en ortopedia y traumatología, basado en el libro **«Los 10 pasos para resolver cualquier fractura»**, del Dr. Michael David Kushner Shrem.

No es un árbol de decisión ni un catálogo de técnicas. Es un modelo del razonamiento: el app acompaña por los diez pasos del método y **detecta incoherencias entre decisiones tomadas en pasos distintos**. Si eliges estabilidad relativa en el Paso 3 y compresión en el Paso 5, te lo dice, y te explica por qué.

## Qué contiene

- **Los diez pasos** del método, de la evaluación del paciente a la anticipación de las complicaciones.
- **La clasificación AO/OTA 2018 completa**: 695 códigos, 506 figuras recortadas por código y las descripciones oficiales traducidas al español.
- **Quince clasificaciones regionales** —Schatzker modificada por Kfuri, Garden, Pauwels, Neer, Hertel, Hawkins, Sanders, Letournel-Judet, Young-Burgess, Tile, Vancouver, Winquist-Hansen, Mason y Lauge-Hansen—, cada una con su concordancia interobservador a la vista y conectada al razonamiento de los pasos siguientes.
- **141 alertas y 26 reglas de coherencia** que responden a lo que el usuario acaba de elegir.
- **Diez casos por fallo**: planificaciones que salieron mal, con las decisiones cargables en el app para que el motor señale el error solo.
- **Plan quirúrgico consolidado**, que se copia o se imprime.
- **94 preguntas de autoevaluación** con puntuación y repaso de lo fallado.

## Cómo se construye

```bash
python3 tools/build_prototipo.py     # genera prototipo.html desde content/
python3 tools/publicar.py            # arma sitio/, que es lo que se publica
```

El contenido vive en `content/` como JSON y está separado del motor: se puede corregir un criterio clínico sin tocar una línea de JavaScript.

Otros generadores, en orden de dependencia:

```bash
python3 tools/parse_compendium.py <pdf>      # compendio AO/OTA → aoota_codigos.json
python3 tools/recortar_figuras.py <pdf>      # una figura por código
python3 tools/traducir_ao.py                 # compone las descripciones en español
python3 tools/build_paso2.py                 # Paso 2 desde el dataset
python3 tools/build_clasificaciones.py       # inyecta las regionales en el Paso 2
python3 tools/patch_alertas_regionales.py    # las conecta con los demás pasos
```

## Cómo se verifica

```bash
python3 tools/validar.py          # integridad del contenido: sin errores
node tools/probar.js              # 60 casos clínicos sobre el motor
node tools/probar_render.js       # que cada pieza de la interfaz se pinta
node tools/probar_descripcion.js  # encadenado de las descripciones AO
```

`validar.py` audita que ninguna condición apunte a una opción inexistente, que ninguna alerta sea inalcanzable y que los casos por fallo disparen de verdad su error. Nada se da por bueno sin pasar estas cuatro.

## Publicación

`sitio/` es una carpeta estática: se puede arrastrar a Netlify Drop o a Vercel, o servirse desde cualquier alojamiento. Incluye `manifest.webmanifest` y `sw.js`, así que una vez servida por https se instala como aplicación y funciona sin conexión.

Para probarlo en local:

```bash
cd sitio && python3 -m http.server 8000
```

## Aviso

Material con fines educativos y de apoyo metodológico. No constituye indicación clínica ni sustituye el juicio del cirujano responsable ni los protocolos de cada institución.

La clasificación AO/OTA y sus figuras se reproducen con fines educativos. La OTA y la AO autorizan su reproducción para investigación, docencia o uso médico sin solicitar permiso; **el uso comercial o con ánimo de lucro requiere autorización del editor**, así que este proyecto se distribuye de forma gratuita.

## Licencia

Dos licencias, porque hay dos cosas distintas dentro:

- **Contenido** (`content/`, `manual/`, la documentación): **CC BY-NC-SA 4.0**. Libre para enseñar, copiar, traducir y adaptar citando la fuente; sin uso comercial; las adaptaciones llevan la misma licencia. Ver [`LICENSE`](LICENSE).
- **Código** (`tools/`, `sw.js`, `manifest.webmanifest`): **MIT**. Ver [`tools/LICENSE`](tools/LICENSE).

El detalle y el porqué de la combinación, en [`LICENCIA.md`](LICENCIA.md).

Cita sugerida:

> Kushner Shrem MD. *Los 10 pasos para resolver cualquier fractura* — I Need To Fix It. https://ineedtofixit.vercel.app · CC BY-NC-SA 4.0
