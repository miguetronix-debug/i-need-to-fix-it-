#!/usr/bin/env python3
"""
extraer_docx.py — Extrae la Parte I de LIBRO_Los_10_pasos_completo.docx
a JSON estructurado por bloques ("crudo"), preservando el orden real
de párrafos y tablas.

Salida: content/_crudo/paso-NN-*.json

Este JSON crudo NO es el que consume el app: es el insumo fiel del libro
sobre el que luego se hace la condensación editorial orientada a decisión.
Mantenerlo permite re-condensar en el futuro sin volver a tocar el .docx.

Uso:
    python3 tools/extraer_docx.py [ruta_al_docx]
"""

import json
import re
import sys
import unicodedata
from pathlib import Path

import docx
from docx.table import Table
from docx.text.paragraph import Paragraph

RAIZ = Path(__file__).resolve().parent.parent
DOCX_POR_DEFECTO = RAIZ.parent / "LIBRO_Los_10_pasos_completo.docx"
SALIDA = RAIZ / "content" / "_crudo"

# Recuadros que el libro usa como cajas de una sola celda.
# La primera línea de la caja define su variante.
VARIANTES = [
    (r"^mapa del", "mapa"),
    (r"^s[ií]ntesis", "sintesis"),
    (r"^evidencia", "evidencia"),
    (r"^atenci[oó]n|^cuidado|^error", "error"),
    (r"^no confundir", "error"),
    (r"^plan b", "planB"),
    (r"^regla|^la pregunta de control", "regla"),
    (r"^idea|^la idea|^la f[oó]rmula|^corolario", "idea"),
]


def sin_acentos(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
    ).lower()


def variante_de(titulo: str) -> str:
    t = sin_acentos(titulo.strip())
    for patron, nombre in VARIANTES:
        if re.search(sin_acentos(patron), t):
            return nombre
    return "info"


def bloques_en_orden(doc):
    """Recorre el cuerpo respetando el orden real de párrafos y tablas."""
    salida = []
    for hijo in doc.element.body.iterchildren():
        if hijo.tag.endswith("}p"):
            salida.append(("p", Paragraph(hijo, doc)))
        elif hijo.tag.endswith("}tbl"):
            salida.append(("t", Table(hijo, doc)))
    return salida


def estilo(par) -> str:
    return par.style.name if par.style is not None else ""


def nivel_heading(par):
    s = estilo(par)
    m = re.match(r"Heading (\d)", s)
    return int(m.group(1)) if m else None


def tabla_a_dict(tabla):
    filas = [[c.text.strip() for c in fila.cells] for fila in tabla.rows]

    # Caja de una sola celda -> recuadro
    if len(tabla.rows) == 1 and len(tabla.columns) == 1:
        celda = tabla.rows[0].cells[0]
        lineas = [p.text.strip() for p in celda.paragraphs if p.text.strip()]
        titulo = lineas[0] if lineas else ""
        return {
            "tipo": "recuadro",
            "variante": variante_de(titulo),
            "titulo": titulo,
            "lineas": lineas[1:],
        }

    return {
        "tipo": "tabla",
        "encabezados": filas[0] if filas else [],
        "filas": filas[1:],
    }


def parrafo_a_dict(par):
    txt = par.text.strip()
    if not txt:
        return None
    est = estilo(par)
    if est == "List Paragraph":
        return {"tipo": "vinheta", "texto": txt}
    return {"tipo": "parrafo", "texto": txt}


def extraer(ruta_docx: Path):
    doc = docx.Document(str(ruta_docx))
    items = bloques_en_orden(doc)

    # Delimitar Parte I: desde el Heading 1 "PARTE I" hasta "PARTE II"
    ini = fin = None
    for i, (clase, obj) in enumerate(items):
        if clase == "p" and nivel_heading(obj) == 1:
            t = obj.text.strip().upper()
            if t.startswith("PARTE I") and ini is None:
                ini = i
            elif t.startswith("PARTE II"):
                fin = i
                break
    if ini is None or fin is None:
        raise SystemExit("No se localizaron los límites de la Parte I.")

    parte1 = items[ini + 1 : fin]

    # Trocear por Heading 2 (cada paso / capítulo complementario)
    capitulos = []
    actual = None
    for clase, obj in parte1:
        if clase == "p" and nivel_heading(obj) == 2:
            if actual:
                capitulos.append(actual)
            actual = {"titulo": obj.text.strip(), "bloques": []}
            continue
        if actual is None:
            continue

        if clase == "t":
            actual["bloques"].append(tabla_a_dict(obj))
        else:
            n = nivel_heading(obj)
            if n in (3, 4) and obj.text.strip():
                actual["bloques"].append(
                    {"tipo": "seccion", "nivel": n, "texto": obj.text.strip()}
                )
            else:
                d = parrafo_a_dict(obj)
                if d:
                    actual["bloques"].append(d)
    if actual:
        capitulos.append(actual)

    return capitulos


def slug(texto: str) -> str:
    s = sin_acentos(texto)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:48]


def main():
    ruta = Path(sys.argv[1]) if len(sys.argv) > 1 else DOCX_POR_DEFECTO
    if not ruta.exists():
        raise SystemExit(f"No se encontró el docx: {ruta}")

    SALIDA.mkdir(parents=True, exist_ok=True)
    capitulos = extraer(ruta)

    print(f"Parte I: {len(capitulos)} capítulos\n")
    resumen = []
    for i, cap in enumerate(capitulos, start=1):
        m = re.match(r"Paso\s+(\d+)", cap["titulo"])
        numero = int(m.group(1)) if m else None
        nombre = f"paso-{numero:02d}-{slug(cap['titulo'].split('·')[-1])}" if numero \
            else f"extra-{i:02d}-{slug(cap['titulo'])}"

        datos = {
            "origen": ruta.name,
            "titulo": cap["titulo"],
            "numeroPaso": numero,
            "bloques": cap["bloques"],
        }
        (SALIDA / f"{nombre}.json").write_text(
            json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        cuenta = {}
        for b in cap["bloques"]:
            cuenta[b["tipo"]] = cuenta.get(b["tipo"], 0) + 1
        palabras = sum(
            len(b.get("texto", "").split())
            for b in cap["bloques"]
            if b["tipo"] in ("parrafo", "vinheta")
        )
        resumen.append((nombre, palabras, cuenta))
        print(f"  {nombre:44s} {palabras:5d} palabras  {cuenta}")

    print(f"\nEscrito en: {SALIDA}")


if __name__ == "__main__":
    main()
