#!/usr/bin/env python3
"""
recortar_figuras.py — Recorta de cada lámina del compendio SOLO el dibujo que
corresponde a cada código, en vez de mostrar la página entera.

Cómo funciona: en el compendio cada figura lleva su código impreso ENCIMA,
como pie de la descripción. `pdftotext -bbox` da la posición exacta de esa
etiqueta; el dibujo ocupa la banda que hay justo debajo. Se recorta esa banda
de la página renderizada.

Salida: content/figuras/cod/<codigo>.jpg  (el código con / y . saneados)

Uso:  python3 tools/recortar_figuras.py <ruta_al_pdf>
"""

import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
COD_JSON = RAIZ / "content" / "aoota_codigos.json"
FIG = RAIZ / "content" / "figuras"
DEST = FIG / "cod"
DPI = 150                # resolución de render para el recorte
ANCHO_PT = 175           # ancho típico de una columna de figuras, en puntos PDF
ALTO_PT = 132           # alto del dibujo bajo su etiqueta
MARGEN = 4


def nombre_archivo(codigo: str) -> str:
    return re.sub(r"[^0-9A-Za-z._-]", "-", codigo) + ".jpg"


def cajas_por_pagina(pdf: Path):
    """{pagina: [(codigo, x0, y0, x1, y1, ancho_pag, alto_pag)]}"""
    salida = Path("/tmp/_bbox.xml")
    subprocess.run(["pdftotext", "-bbox", str(pdf), str(salida)], check=True)
    xml = salida.read_text(encoding="utf-8", errors="ignore")
    out, pagina = {}, 0
    dims = (0, 0)
    for trozo in re.split(r'<page ', xml)[1:]:
        pagina += 1
        m = re.match(r'width="([\d.]+)" height="([\d.]+)"', trozo)
        if m:
            dims = (float(m.group(1)), float(m.group(2)))
        for w in re.finditer(
                r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]+)</word>',
                trozo):
            texto = w.group(5).strip().rstrip("*")
            if re.fullmatch(r"[0-9]{1,2}[RUF]?[0-9.]*[A-Z]?[0-9]?(\.[0-9])?", texto) and any(ch.isalpha() for ch in texto):
                out.setdefault(pagina, []).append(
                    (texto, float(w.group(1)), float(w.group(2)),
                     float(w.group(3)), float(w.group(4)), dims[0], dims[1]))
    return out


def main():
    if len(sys.argv) < 2:
        raise SystemExit("Uso: recortar_figuras.py <ruta_al_pdf>")
    pdf = Path(sys.argv[1])
    doc = json.loads(COD_JSON.read_text(encoding="utf-8"))
    codigos = doc["codigos"]
    DEST.mkdir(parents=True, exist_ok=True)

    cajas = cajas_por_pagina(pdf)
    escala = DPI / 72.0
    hechos, sin_etiqueta = 0, []

    # agrupar códigos por página para abrir cada imagen una sola vez
    por_pagina = {}
    for c, v in codigos.items():
        if v.get("pagina"):
            por_pagina.setdefault(v["pagina"], []).append(c)

    for pag, lista in sorted(por_pagina.items()):
        png = Path("/tmp/_pag")
        subprocess.run(["pdftoppm", "-q", "-f", str(pag), "-l", str(pag), "-r", str(DPI),
                        "-jpeg", "-jpegopt", "quality=82", str(pdf), str(png)], check=True)
        candidatos = sorted(Path("/tmp").glob("_pag-*.jpg"))
        if not candidatos:
            continue
        img = Image.open(candidatos[0])
        etiquetas = cajas.get(pag, [])
        for c in lista:
            # el código tal cual está impreso (los _ del compendio son ejemplos)
            posibles = [e for e in etiquetas if e[0] == c]
            if not posibles and "_" in c:
                patron = re.compile("^" + re.escape(c).replace(r"\_", r"\d") + "$")
                posibles = [e for e in etiquetas if patron.match(e[0])]
            if not posibles:
                sin_etiqueta.append(c)
                continue
            # si hay varias, la más baja de la página suele ser la del dibujo
            _, x0, y0, x1, y1, pw, ph = max(posibles, key=lambda e: e[2])
            izq = max(0, (x0 - MARGEN) * escala)
            der = min(img.width, (x0 + ANCHO_PT) * escala)
            arr = max(0, (y0 - MARGEN) * escala)
            aba = min(img.height, (y1 + ALTO_PT) * escala)
            if der - izq < 40 or aba - arr < 40:
                sin_etiqueta.append(c)
                continue
            img.crop((int(izq), int(arr), int(der), int(aba))).save(
                DEST / nombre_archivo(c), quality=82)
            hechos += 1
        for p in candidatos:
            p.unlink(missing_ok=True)

    # anotar en el JSON qué códigos tienen recorte
    for c in codigos:
        f = DEST / nombre_archivo(c)
        if f.exists():
            codigos[c]["figura"] = f"content/figuras/cod/{nombre_archivo(c)}"
    COD_JSON.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Recortes generados: {hechos}")
    print(f"Sin etiqueta localizable: {len(sin_etiqueta)}")
    if sin_etiqueta[:12]:
        print("  ejemplos:", " ".join(sin_etiqueta[:12]))


if __name__ == "__main__":
    main()
