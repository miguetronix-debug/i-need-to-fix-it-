#!/usr/bin/env python3
"""
build_clasificaciones.py — Convierte content/clasificaciones.json en decisiones
del Paso 2, filtradas por región.

Las clasificaciones regionales complementan a la AO: no la sustituyen. Por eso
viven en el Paso 2, aparecen solo cuando el segmento las hace pertinentes, y
cada opción puede emitir hechos de contexto para que los pasos siguientes
razonen sobre ellas.

La concordancia interobservador NO se usa como filtro de inclusión: se muestra
en la propia pregunta. El criterio de entrada es otro: que cambie el manejo,
el abordaje o el pronóstico.

Es idempotente: borra las decisiones «cl-*» anteriores y las vuelve a escribir.

Uso:  python3 tools/build_clasificaciones.py
"""

import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FUENTE = RAIZ / "content" / "clasificaciones.json"
DESTINO = RAIZ / "content" / "pasos" / "02-clasificacion.json"

PREFIJO = "cl-"


def main():
    src = json.loads(FUENTE.read_text(encoding="utf-8"))
    P = json.loads(DESTINO.read_text(encoding="utf-8"))

    # fuera las anteriores, para poder regenerar sin duplicar
    P["decisiones"] = [d for d in P["decisiones"] if not d["id"].startswith(PREFIJO)]

    nuevas, opciones = [], 0
    for c in src["clasificaciones"]:
        opts = []
        for g in c["grados"]:
            o = {"id": g["id"], "etiqueta": g["etiqueta"], "criterios": g.get("criterios", [])}
            if g.get("emite"):
                o["emite"] = g["emite"]
            opts.append(o)
        opciones += len(opts)
        nuevas.append({
            "id": PREFIJO + c["id"],
            "pregunta": c["pregunta"],
            "ayuda": c["decide"],
            "nota": "Concordancia — " + c["concordancia"],
            "tipo": "opcionMultiple" if c.get("multiple") else "opcionUnica",
            "opcional": True,
            "mostrarSi": {"ctx": c["ctx"]},
            "opciones": opts,
        })

    P["decisiones"] += nuevas

    # un derivado que resume lo que la clasificación regional aporta al plan
    reglas = []
    for c in src["clasificaciones"]:
        for g in c["grados"]:
            if not g.get("emite"):
                continue
            reglas.append({
                "si": {PREFIJO + c["id"]: [g["id"]]},
                "texto": c["nombre"] + " " + g["etiqueta"] + " — " + g["criterios"][0]
                         + (". " + g["criterios"][1] if len(g["criterios"]) > 1 else "")
            })
    P["derivados"] = [d for d in P["derivados"] if d["id"] != "regionales"]
    P["derivados"].append({
        "id": "regionales",
        "titulo": "Lo que añade la clasificación regional",
        "tipo": "reglas",
        "modo": "todas",
        "reglas": reglas,
    })

    # las referencias que citen las clasificaciones tienen que existir
    refs = json.loads((RAIZ / "content" / "referencias.json").read_text(encoding="utf-8"))["referencias"]
    faltan = sorted({r for c in src["clasificaciones"] for r in c.get("refs", []) if r not in refs})

    DESTINO.write_text(json.dumps(P, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Clasificaciones inyectadas: {len(nuevas)} · {opciones} opciones · "
          f"{len(reglas)} reglas derivadas")
    if faltan:
        print("Referencias que faltan en referencias.json:")
        for r in faltan:
            print("   ·", r)


if __name__ == "__main__":
    main()
