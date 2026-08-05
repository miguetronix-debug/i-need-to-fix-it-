#!/usr/bin/env python3
"""
hoja_revision.py — Genera un documento legible con todas las clasificaciones
regionales para que el autor pueda revisarlas de una sentada.

Hace falta porque en el app cada clasificación solo aparece cuando la región
la hace pertinente: para ver Neer hay que clasificar un húmero proximal, para
ver Hawkins un astrágalo. Eso está bien para usarlo y es imposible para
revisarlo.

Uso:  python3 tools/hoja_revision.py
"""

import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SRC = json.loads((RAIZ / "content" / "clasificaciones.json").read_text(encoding="utf-8"))
REFS = json.loads((RAIZ / "content" / "referencias.json").read_text(encoding="utf-8"))["referencias"]
SALIDA = RAIZ / "REVISION_clasificaciones.md"

REGION = {
    "seg-41": "Meseta tibial · 41", "seg-31": "Fémur proximal · 31",
    "seg-11": "Húmero proximal · 11", "seg-81": "Astrágalo · 81",
    "seg-82": "Calcáneo · 82", "seg-62": "Acetábulo · 62",
    "seg-61": "Anillo pélvico · 61", "seg-32": "Diáfisis femoral · 32",
    "seg-2R1": "Cabeza radial · 2R1", "seg-44": "Segmento maleolar · 44",
    "reg-cadera": "Cadera", "reg-femur": "Fémur",
}


def main():
    L = ["# Revisión de las clasificaciones regionales",
         "",
         "Quince clasificaciones que complementan a la AO/OTA en el Paso 2.",
         "",
         "**Criterio de entrada:** que cambie el manejo, el abordaje o el pronóstico. "
         "La concordancia interobservador no filtra — se muestra en la propia pregunta, "
         "porque saber lo que vale una clasificación forma parte de saber usarla.",
         "",
         "**Cómo revisar:** marca con ✅ lo que apruebas, escribe encima lo que corrija, "
         "y tacha lo que sobre. Me interesan sobre todo tres cosas: si falta algún grado, "
         "si el «qué decide» es exacto, y si las notas de concordancia son justas.",
         "",
         "---", ""]

    for i, c in enumerate(SRC["clasificaciones"], 1):
        regiones = " · ".join(REGION.get(x, x) for x in c["ctx"])
        L += [f"## {i}. {c['nombre']}", "",
              f"**Región:** {regiones}  ",
              f"**Aparece como:** «{c['pregunta']}»  ",
              f"**Selección:** {'varias a la vez' if c.get('multiple') else 'una sola'}", "",
              f"**Qué decide.** {c['decide']}", "",
              f"> **Concordancia mostrada al usuario.** {c['concordancia']}", "",
              "| Grado | Criterios que se muestran | Avisa a otros pasos |",
              "|---|---|---|"]
        for g in c["grados"]:
            crit = "<br>".join("· " + x for x in g.get("criterios", []))
            emite = ", ".join("`" + e + "`" for e in g.get("emite", [])) or "—"
            L.append(f"| **{g['etiqueta']}** | {crit} | {emite} |")
        L.append("")
        for r in c.get("refs", []):
            if r in REFS:
                L.append(f"*{REFS[r]['cita']}*")
                L.append("")
        L += ["**Tu veredicto:** ⬜ apruebo · ⬜ corrijo · ⬜ fuera", "", "---", ""]

    # Qué hace cada hecho emitido, para que se vea que no son decorativos
    L += ["## Qué provoca cada aviso en los pasos siguientes", "",
          "Los hechos de la última columna no son etiquetas: encienden alertas en otros pasos. "
          "Esto es lo que convierte a las clasificaciones en parte del razonamiento y no en una "
          "tabla de consulta.", "",
          "| Hecho | Dónde salta | Qué dice |", "|---|---|---|"]
    PASOS = RAIZ / "content" / "pasos"
    filas = []
    for f in sorted(PASOS.glob("*.json")):
        P = json.loads(f.read_text(encoding="utf-8"))
        for a in P.get("alertas", []):
            if not a["id"].startswith("rg-"):
                continue
            conds = [a.get("mostrarSi") or {}] + (a.get("mostrarSiAlguno") or [])
            hechos = sorted({x for cd in conds for x in (cd.get("ctx") or []) + (cd.get("ctxTodos") or [])})
            if hechos:
                filas.append((", ".join("`" + h + "`" for h in hechos),
                              f"Paso {P['numero']}", a["titulo"]))
    for h, p, t in filas:
        L.append(f"| {h} | {p} | {t} |")
    L += ["", "---", "",
          f"Generado desde `content/clasificaciones.json` · {len(SRC['clasificaciones'])} clasificaciones · "
          f"{sum(len(c['grados']) for c in SRC['clasificaciones'])} grados · {len(filas)} alertas conectadas.",
          ""]

    SALIDA.write_text("\n".join(L), encoding="utf-8")
    print(f"Generada: {SALIDA.name} · {len(SRC['clasificaciones'])} clasificaciones · {len(filas)} alertas conectadas")


if __name__ == "__main__":
    main()
