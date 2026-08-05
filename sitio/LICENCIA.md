# Licencia

Este proyecto tiene **dos licencias**, porque tiene dos cosas distintas dentro:
el contenido médico, que es obra de autor, y el programa que lo presenta, que es
código.

| Qué | Dónde | Licencia |
|---|---|---|
| **El contenido**: los diez pasos, las decisiones, las alertas, los casos por fallo, las traducciones | `content/`, `manual/`, los `.md` de la raíz | **CC BY-NC-SA 4.0** — ver [`LICENSE`](LICENSE) |
| **El programa**: el generador, el motor de decisión, las pruebas | `tools/`, `sw.js`, `manifest.webmanifest` | **MIT** — ver [`tools/LICENSE`](tools/LICENSE) |

El HTML publicado (`prototipo.html`, `sitio/index.html`) contiene ambas cosas:
el código va bajo MIT y el contenido incrustado bajo CC BY-NC-SA 4.0.

---

## Por qué esta combinación

**El contenido no comercial.** Dentro del app se reproduce la clasificación
AO/OTA 2018, cuya licencia autoriza la reproducción con fines de investigación,
educativos o médicos **sin pedir permiso**, pero exige autorización del editor
para el uso comercial o con ánimo de lucro. Si el contenido de este proyecto se
publicara con una licencia que permitiera el uso comercial, estaría dando un
permiso que no está en mi mano dar. La cláusula NC no es una preferencia: es
coherencia con lo que hay dentro.

**El código con MIT.** El motor de decisión, el generador y las pruebas no
contienen nada de terceros. Que alguien pueda tomar `tools/` y construir otra
cosa con él —otro método, otra especialidad— no perjudica a nadie y es la mejor
forma de que el trabajo de ingeniería sirva más allá de este libro.

---

## Qué puedes hacer con el contenido (CC BY-NC-SA 4.0)

**Sí, libremente:**

- Usarlo para enseñar: residencia, curso, congreso, clase.
- Usarlo en la práctica clínica propia o de tu servicio.
- Copiarlo, redistribuirlo, traducirlo, adaptarlo.
- Extraer partes para material docente propio.

**Con tres condiciones:**

1. **BY — Atribución.** Citar al autor: Dr. Michael David Kushner Shrem, *Los 10
   pasos para resolver cualquier fractura*, con enlace a la fuente y aviso de si
   hiciste cambios.
2. **NC — No comercial.** Nada de venderlo, incluirlo en un producto de pago,
   en un curso de pago ni en publicidad. La docencia dentro de una institución,
   incluso privada, no es uso comercial; cobrar por el acceso al material, sí.
3. **SA — Compartir igual.** Si lo adaptas y lo distribuyes, tu versión lleva
   esta misma licencia.

**Para uso comercial** hace falta permiso por escrito del autor **y**, por la
parte AO/OTA, del editor de la clasificación.

---

## Cómo citar

> Kushner Shrem MD. *Los 10 pasos para resolver cualquier fractura* — I Need To
> Fix It. https://ineedtofixit.vercel.app · CC BY-NC-SA 4.0

---

## Lo que esta licencia no es

No es una garantía. El app es material educativo y de apoyo metodológico: no
constituye indicación clínica ni sustituye el juicio del cirujano responsable ni
los protocolos de la institución. El contenido se ofrece «tal cual», sin
garantías de ningún tipo, y el autor no responde de decisiones clínicas tomadas
a partir de él.

---

© 2026 Michael David Kushner Shrem. Todos los derechos no cedidos expresamente
por estas licencias quedan reservados.
