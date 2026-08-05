#!/usr/bin/env python3
"""
traducir_ao.py — Compone la descripción en español de cada código AO/OTA a
partir de un glosario de fragmentos.

Por qué fragmentos y no frases enteras: las descripciones del compendio están
separadas por comas y cada trozo traduce de forma independiente, conservando el
orden. Eso permite traducir 684 descripciones con un glosario de unos 500
fragmentos que el autor puede revisar por frecuencia, en vez de leer 684 frases.

El inglés original se conserva siempre en «texto»; el español va en «texto_es».
Si mañana se corrige una entrada del glosario, basta con volver a ejecutar esto.

Uso:  python3 tools/traducir_ao.py
"""

import json
import re
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
COD = RAIZ / "content" / "aoota_codigos.json"
GLO = RAIZ / "content" / "glosario_ao.json"

# Texto instructivo del compendio que el parser arrastró y que no describe
# ninguna fractura: se descarta en lugar de traducirse.
BASURA = re.compile(
    r"→|example|indicated with an underline|is added|refer to the appendix|"
    r"identified as follows|\b\d[a-z][\d_]|\b5\d\.__|please refer|"
    r"\bis$|\((ie|eg)$|^(if the|it is classified)|"
    r"^(spine 5|cervical 51|thoracic 52|lumbar 53|and sacrum|s: |¹|thorax anatomical)",
    re.I)


def fragmentos(t):
    return [s.strip().strip(".") for s in re.split(r"\s*,\s*", t) if s.strip().strip(".")]


def main():
    doc = json.loads(COD.read_text(encoding="utf-8"))
    codigos = doc["codigos"]
    glo = json.loads(GLO.read_text(encoding="utf-8"))["glosario"]

    faltan, traducidos, descartados = Counter(), 0, 0
    for k, v in codigos.items():
        t = v.get("texto") or ""
        if not t:
            continue
        partes, hueco = [], False
        for f in fragmentos(t):
            if BASURA.search(f):
                continue                       # ruido del compendio: fuera
            es = glo.get(f.lower())
            if es is None:
                faltan[f.lower()] += 1
                hueco = True
            elif es:
                partes.append(es)
        if hueco:
            v.pop("texto_es", None)            # sin traducción completa, no se traduce
            continue
        if not partes:
            descartados += 1
            v.pop("texto_es", None)
            continue
        frase = ", ".join(partes)
        v["texto_es"] = frase[0].upper() + frase[1:]
        traducidos += 1

    COD.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    total = sum(1 for v in codigos.values() if v.get("texto"))
    print(f"Traducidos: {traducidos} de {total} códigos con descripción")
    print(f"Sin descripción útil (solo texto instructivo): {descartados}")
    if faltan:
        print(f"\nFragmentos sin entrada en el glosario ({len(faltan)}):")
        for f, c in faltan.most_common(40):
            print(f"   {c:3d}  {f}")
    else:
        print("El glosario cubre todos los fragmentos.")


if __name__ == "__main__":
    main()
