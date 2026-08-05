#!/usr/bin/env python3
"""
hoja_glosario.py — Hoja de revisión del glosario AO, ordenada por frecuencia.

La idea: revisar 488 entradas seguidas es inviable, pero no hace falta. Los
primeros 40 fragmentos cubren la mitad del texto del compendio, así que se
revisan con lupa y el resto se ojea. La hoja lo dice explícitamente y marca
dónde está cada umbral de cobertura.

Uso:  python3 tools/hoja_glosario.py
"""

import json
import re
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "REVISION_glosario.md"


def main():
    cod = json.loads((RAIZ / "content" / "aoota_codigos.json").read_text(encoding="utf-8"))["codigos"]
    glo = json.loads((RAIZ / "content" / "glosario_ao.json").read_text(encoding="utf-8"))["glosario"]

    frec = Counter()
    for v in cod.values():
        for f in re.split(r"\s*,\s*", v.get("texto") or ""):
            f = f.strip().strip(".").lower()
            if f in glo:
                frec[f] += 1

    orden = sorted(glo, key=lambda f: (-frec.get(f, 0), f))
    total = sum(frec.values())

    L = ["# Revisión del glosario AO/OTA", "",
         f"**{len(glo)} fragmentos** que traducen las **{sum(1 for v in cod.values() if v.get('texto_es'))} "
         f"descripciones** del compendio.", "",
         "Las descripciones del compendio vienen separadas por comas, y cada fragmento traduce de forma "
         "independiente conservando el orden. Por eso corregir un fragmento corrige de golpe todas las "
         "frases donde aparece.", "",
         "**Cómo revisar sin morir en el intento.** Está ordenado por frecuencia de uso. Los primeros "
         "cuarenta cubren la mitad del texto: esos merecen lupa. A partir del umbral del 90 % lo que "
         "queda son nombres anatómicos y frases que salen una sola vez, y se ojean.", "",
         "Escribe la corrección al lado de la que quieras cambiar y me la devuelves; vuelvo a componer "
         "las 665 descripciones en un minuto.", "",
         "---", "",
         "| # | Veces | Inglés | Español |", "|---|---|---|---|"]

    acum, hitos = 0, {50: False, 75: False, 90: False}
    for i, f in enumerate(orden, 1):
        c = frec.get(f, 0)
        acum += c
        L.append(f"| {i} | {c or '—'} | {f} | **{glo[f]}** |")
        pct = acum * 100 / total if total else 0
        for h in (50, 75, 90):
            if not hitos[h] and pct >= h:
                hitos[h] = True
                L.append(f"| | | | *— aquí va cubierto el {h} % del texto del compendio —* |")

    L += ["", "---", "",
          "## Lo que se descarta a propósito", "",
          "El compendio trae, entre las descripciones, texto instructivo sobre cómo construir el código "
          "—«el número de localización se añade entre dos puntos», «el código de ejemplo del tercer "
          "metacarpiano se indica subrayado»—. El extractor lo arrastró y no describe ninguna fractura, "
          "así que se descarta en lugar de traducirse: 19 códigos se quedan sin descripción por este "
          "motivo, casi todos de tórax, columna y mano.", "",
          "## Qué pasa con el inglés", "",
          "No se pierde. El original queda guardado en el campo `texto` de cada código y el español en "
          "`texto_es`; el app muestra el español y conserva el inglés debajo como respaldo. Si mañana "
          "corriges una entrada del glosario, se vuelve a componer todo sin tocar la fuente.", ""]

    SALIDA.write_text("\n".join(L), encoding="utf-8")
    print(f"Generada: {SALIDA.name} · {len(glo)} entradas · {total} apariciones en el compendio")


if __name__ == "__main__":
    main()
