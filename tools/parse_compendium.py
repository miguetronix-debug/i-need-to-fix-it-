#!/usr/bin/env python3
"""
parse_compendium.py — Extrae el árbol COMPLETO de códigos AO/OTA 2018 desde
el PDF oficial del compendio (AOOTA_Classification_2018_Compendium.pdf).

Salida: content/aoota_codigos.json — un mapa plano código → {texto, nivel,
calificaciones}. Se guarda plano a propósito: la jerarquía real no es
uniforme (la escápula usa la letra como localización, no como tipo; el
glenoides tiene un grupo 0; el peroné solo llega a tipo), así que el app
navega por prefijos en vez de asumir una estructura rígida.

Uso:  python3 tools/parse_compendium.py <ruta_al_pdf>
"""

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "content" / "aoota_codigos.json"

# Huesos y segmentos válidos del compendio 2018
SEGMENTOS = (r"1[1-6]|2R[1-3]|2U[1-3]|3[1-4]|4[1-4]|4F[1-3]|"
             r"6[12]|7[1-8]|8[1-8]|9[1-3]|5[1-3]")
# El segmento admite sufijos con punto: clavícula 15.1, metacarpiano 77.3.1,
# falange 78.1.1.1. Los puntos POSTERIORES a la letra son el subgrupo.
RE_CODIGO = re.compile(
    rf"\b((?:{SEGMENTOS})(?:\.(?:_{{1,2}}|[0-9])){{0,3}})\.?([A-Z])?([0-9])?(\.[0-9])?(\*+)?\s*$")
RE_ESPACIOS_COD = re.compile(r"(\d)\.\s+(\d)")
RE_CALIF = re.compile(r"^([a-z])\s+(.{3,})$")
RUIDO = re.compile(r"jorthotrauma|Copyright ©|^S\d+\s*\||^\s*$|Volume 32|"
                   r"AO Foundation, Davos|Orthopaedic Trauma Association, IL")
ETIQUETAS = re.compile(r"^(Location|Type|Types|Group|Groups|Subgroup|Subgroups|"
                       r"Qualifications|\*Qualifications|Bone)\s*:?\s*", re.I)

NIVEL = {0: "segmento", 1: "tipo", 2: "grupo", 3: "subgrupo"}


def texto_del_pdf(ruta: Path) -> str:
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
        salida = tmp.name
    subprocess.run(["pdftotext", "-q", str(ruta), salida], check=True)
    return Path(salida).read_text(encoding="utf-8", errors="ignore")


# Descripciones que en realidad son bibliografía o texto corrido colado
BASURA = re.compile(r"et al\.|\d{4};|\bSurg\b|\bAnn Chir\b|Journal of|Auflage|"
                    r"\bpp?\.\s*\d|www\.|doi:|ISBN|AO/OTA codes|"
                    r"Fracture and Dislocation|Compendium", re.I)


def util(s: str) -> bool:
    return bool(s) and len(s) <= 200 and not BASURA.search(s)


def limpia(s: str) -> str:
    s = ETIQUETAS.sub("", s).strip(" .,;:")
    s = re.sub(r"\s+", " ", s)
    # En algunas láminas el encabezado de página («Bone: Clavicle») queda pegado
    # al nombre del segmento y produce «Clavicle Bone: Clavicle». Nos quedamos
    # con lo que va detrás de la etiqueta, que es la forma completa.
    m = re.match(r"^.*?\bBone:\s*(.+)$", s)
    if m:
        s = m.group(1).strip()
    return s.strip()


def parsear(texto: str):
    codigos = {}
    buffer, en_calif, calif_actual = [], False, []
    pendiente_calif = None  # código al que se aplicarán las calificaciones

    pagina = 1
    for bruto in texto.split("\n"):
        if "\f" in bruto:
            pagina += bruto.count("\f")
            bruto = bruto.replace("\f", "")
        linea = RE_ESPACIOS_COD.sub(r"\1.\2", bruto.rstrip())
        if RUIDO.search(linea):
            if not linea.strip():
                buffer = []
            continue

        # bloque de calificaciones
        if re.match(r"^\*?Qualifications\s*:?\s*$", linea.strip(), re.I):
            en_calif, calif_actual = True, []
            continue
        if en_calif:
            m = RE_CALIF.match(linea.strip())
            if m:
                calif_actual.append({"letra": m.group(1), "texto": limpia(m.group(2))})
                continue
            if calif_actual and pendiente_calif:
                for c in pendiente_calif:
                    codigos.setdefault(c, {}).setdefault("calificaciones", []).extend(calif_actual)
            en_calif, calif_actual = False, []
            # sigue procesando la línea normalmente

        m = RE_CODIGO.search(linea)
        if m:
            seg, letra, grupo, sub, ast = m.groups()
            # mano y pie: el identificador de radio/dedo es un parámetro,
            # el compendio lo ilustra con un ejemplo. Se guarda como plantilla.
            # Huesos con identificador (radio, dedo, costilla, vértebra): el
            # compendio los ilustra con un ejemplo concreto; se normaliza a "_"
            # para guardar la plantilla genérica y no un caso particular.
            parametros = 0
            partes_seg = seg.split(".")
            if len(partes_seg) > 1 and partes_seg[0] in ("16", "77", "78", "87", "88",
                                                         "51", "52", "53"):
                if partes_seg[0] in ("51", "52", "53"):
                    ident = len(partes_seg) - 1
                else:
                    ident = len(partes_seg) - 2
                if ident > 0:
                    partes_seg[1:1 + ident] = ["_"] * ident
                    parametros = ident
                    seg = ".".join(partes_seg)
            codigo = seg + (letra or "") + (grupo or "") + (sub or "")
            # descripción: lo que queda en la línea + el buffer previo
            resto = linea[:m.start()].strip()
            partes = [p for p in buffer + [resto] if p]
            desc = limpia(" ".join(partes))
            nivel = NIVEL[sum(1 for x in (letra, grupo, sub) if x)]
            reg = codigos.setdefault(codigo, {})
            if util(desc) and len(desc) > len(reg.get("texto", "")):
                reg["texto"] = desc
            reg["nivel"] = nivel
            reg["segmento"] = seg
            reg.setdefault("pagina", pagina)
            if letra:
                reg["letra"] = letra
            if grupo:
                reg["grupo"] = grupo
            if sub:
                reg["subgrupo"] = sub[1:]
            if parametros:
                reg["parametros"] = parametros
                reg["plantilla"] = ("Cada _ es un identificador que se sustituye por su número: "
                                    "radio o dedo (pulgar 1, índice 2, medio 3, anular 4, "
                                    "meñique 5), costilla o vértebra según el hueso.")
            if ast:
                reg["tieneCalificaciones"] = True
                pendiente_calif = (pendiente_calif or []) + [codigo] \
                    if pendiente_calif is not None else [codigo]
            buffer = []
            if not ast:
                pendiente_calif = [codigo] if pendiente_calif is None else pendiente_calif
            continue

        t = limpia(linea)
        if t and not t.isdigit() and len(t) > 2:
            buffer.append(t)
            if len(buffer) > 6:
                buffer = buffer[-6:]
        if not linea.strip():
            pendiente_calif = None

    # limpieza: quitar entradas sin texto útil
    for c in list(codigos):
        if not codigos[c].get("texto"):
            codigos[c]["texto"] = ""
        cal = codigos[c].get("calificaciones")
        if cal:  # deduplicar
            vistos, out = set(), []
            for x in cal:
                k = (x["letra"], x["texto"])
                if k not in vistos:
                    vistos.add(k)
                    out.append(x)
            codigos[c]["calificaciones"] = out
    return codigos


def main():
    if len(sys.argv) < 2:
        raise SystemExit("Uso: parse_compendium.py <ruta_al_pdf>")
    ruta = Path(sys.argv[1])
    texto = texto_del_pdf(ruta) if ruta.suffix.lower() == ".pdf" else ruta.read_text(encoding="utf-8")
    codigos = parsear(texto)

    doc = {
        "version": "AO/OTA 2018 — extraído del compendio oficial completo",
        "fuente": ("Meinberg EG, Agel J, Roberts CS, Karam MD, Kellam JF. "
                   "Fracture and Dislocation Classification Compendium—2018. "
                   "J Orthop Trauma. 2018;32(Suppl 1):S1–S170. "
                   "PDF oficial AOOTA_Classification_2018_Compendium.pdf."),
        "licencia": ("La OTA y la AO autorizan reproducir la clasificación y sus figuras "
                     "con fines de investigación, educativos o médicos sin solicitar permiso. "
                     "El uso comercial o con ánimo de lucro requiere autorización del editor."),
        "nota": ("Mapa plano de códigos. La jerarquía real no es uniforme: la escápula usa "
                 "la letra como localización, el glenoides tiene un grupo 0 y algunos huesos "
                 "solo llegan a tipo. El app navega por prefijos."),
        "codigos": dict(sorted(codigos.items())),
    }
    SALIDA.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")

    por_nivel = {}
    for v in codigos.values():
        por_nivel[v["nivel"]] = por_nivel.get(v["nivel"], 0) + 1
    segs = sorted({v["segmento"] for v in codigos.values()})
    con_cal = sum(1 for v in codigos.values() if v.get("calificaciones"))
    print(f"Escrito: {SALIDA}")
    print(f"  {len(codigos)} códigos · {con_cal} con calificaciones")
    print(f"  por nivel: {por_nivel}")
    print(f"  {len(segs)} segmentos: {' '.join(segs)}")


if __name__ == "__main__":
    main()
