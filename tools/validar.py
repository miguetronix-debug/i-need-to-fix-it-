#!/usr/bin/env python3
"""
validar.py — Auditoría del contenido del app.

Comprueba, para todos los pasos:
  · IDs únicos de decisiones y de opciones
  · Que todo soloSi / mostrarSi apunte a una decisión y opción que existan
  · Que las reglas de coherencia y los derivados apunten a ids existentes
  · Que las referencias citadas estén definidas
  · Que la autoevaluación tenga índices de respuesta válidos
  · Alcanzabilidad: que cada opción condicionada pueda llegar a mostrarse
  · Contraste del dataset AO/OTA con el folleto oficial

Uso:  python3 tools/validar.py
"""

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
errores, avisos = [], []


def err(m): errores.append(m)
def avi(m): avisos.append(m)


# ------------------------------------------------------------------ dataset
AO = json.loads((RAIZ / "content" / "aoota.json").read_text(encoding="utf-8"))

# El folleto oficial AOE-E1-018.10 ilustra exactamente estos grupos.
ESPERADO = {
    "11": {"A": ["1", "2", "3"], "B": ["1"], "C": ["1", "3"]},
    "12": {"A": ["1", "2", "3"], "B": ["2", "3"], "C": ["2", "3"]},
    "13": {"A": ["1", "2", "3"], "B": ["1", "2", "3"], "C": ["1", "2", "3"]},
    "2R1": {"A": ["1", "2", "3"], "B": ["1", "3"], "C": ["1", "3"]},
    "2R2": {"A": ["1", "2", "3"], "B": ["2", "3"], "C": ["2", "3"]},
    "2R3": {"A": ["1", "2", "3"], "B": ["1", "2", "3"], "C": ["1", "2", "3"]},
    "2U1": {"A": ["1", "2", "3"], "B": ["1", "2"], "C": ["3"]},
    "2U2": {"A": ["1", "2", "3"], "B": ["2", "3"], "C": ["2", "3"]},
    "2U3": {"A": ["1", "2", "3"], "B": [], "C": []},
    "31": {"A": ["1", "2", "3"], "B": ["1", "2", "3"], "C": ["2"]},
    "32": {"A": ["1", "2", "3"], "B": ["2", "3"], "C": ["2", "3"]},
    "33": {"A": ["1", "2", "3"], "B": ["1", "2", "3"], "C": ["1", "2", "3"]},
    "41": {"A": ["1", "2", "3"], "B": ["1", "2", "3"], "C": ["1", "2", "3"]},
    "42": {"A": ["1", "2", "3"], "B": ["2", "3"], "C": ["2", "3"]},
    "43": {"A": ["1", "2", "3"], "B": ["1", "2", "3"], "C": ["1", "2", "3"]},
    "44": {"A": ["1", "2", "3"], "B": ["1", "2", "3"], "C": ["1", "2", "3"]},
    "4F1": {"A": [], "B": []},
    "4F2": {"A": [], "B": []},
    "4F3": {"A": [], "B": []},
}

print("=" * 62)
print("1. DATASET AO/OTA frente al folleto oficial")
print("=" * 62)
for h in AO["huesos"]:
    for s in h.get("segmentos", []):
        cod = s["codigo"]
        if cod not in ESPERADO:
            if s.get("tipos"):
                avi(f"{cod}: no está en la tabla de contraste del folleto (pelvis/acetábulo se transcribieron aparte)")
            continue
        real = {t["letra"]: [g["n"] for g in t.get("grupos", [])] for t in s.get("tipos", [])}
        esp = ESPERADO[cod]
        if set(real) != set(esp):
            err(f"{cod}: tipos {sorted(real)} ≠ esperados {sorted(esp)}")
        for L in esp:
            if L in real and real[L] != esp[L]:
                err(f"{cod}{L}: grupos {real.get(L)} ≠ esperados {esp[L]}")
        ok = set(real) == set(esp) and all(real.get(L) == esp[L] for L in esp)
        print(f"   {'OK ' if ok else '!! '}{cod:5s} " +
              " · ".join(f"{L}{''.join(esp[L]) or '—'}" for L in sorted(esp)))

# ------------------------------------------------------------------- pasos
print()
print("=" * 62)
print("2. PASOS — integridad de decisiones, alertas y derivados")
print("=" * 62)
REFS = json.loads((RAIZ / "content" / "referencias.json").read_text(encoding="utf-8"))["referencias"]

# Vocabulario de hechos que las propias opciones declaran con «emite»: así el
# validador no hay que tocarlo cada vez que se añade una clasificación.
EMITIDOS = set()
for _f in sorted((RAIZ / "content" / "pasos").glob("*.json")):
    for _d in json.loads(_f.read_text(encoding="utf-8"))["decisiones"]:
        for _o in _d["opciones"]:
            EMITIDOS.update(_o.get("emite") or [])

for f in sorted((RAIZ / "content" / "pasos").glob("*.json")):
    P = json.loads(f.read_text(encoding="utf-8"))
    nom = f.name
    decs = {d["id"]: d for d in P["decisiones"]}
    opts = {d["id"]: {o["id"] for o in d["opciones"]} for d in P["decisiones"]}

    if len(decs) != len(P["decisiones"]):
        err(f"{nom}: hay ids de decisión repetidos")
    for d in P["decisiones"]:
        vistos = set()
        for o in d["opciones"]:
            if o["id"] in vistos:
                err(f"{nom}: opción repetida {o['id']} en {d['id']}")
            vistos.add(o["id"])
            if not o.get("etiqueta"):
                err(f"{nom}: opción sin etiqueta en {d['id']}")

    CTX_OK = {"artic", "diaf", "maleolar", "pelvis"} | \
             {f"tipo{L}" for L in "ABCDEF"} | \
             {f"{c}-{L}" for c in ("artic", "diaf", "maleolar", "pelvis") for L in "ABCDEF"} | \
             {"zonas-una", "zonas-dos", "est-absoluta", "est-relativa",
              "art-absoluta", "art-relativa", "meta-absoluta", "meta-relativa"} | \
             {"reg-" + r for r in ("hombro", "torax", "humero", "codo", "antebrazo",
                                   "muneca", "mano", "cadera", "femur", "rodilla",
                                   "tibia", "tobillo", "pie", "columna", "pelvis")} | \
             {"red-anatomica", "red-funcional",
              "via-directa", "via-percutanea", "via-indirecta",
              "usa-compresion", "usa-banda", "usa-sosten", "usa-ferulaje",
              "usa-neutralizacion", "comp-tornillo", "comp-placa",
              "fer-clavo", "fer-puente", "fer-tutor",
              "imp-tornillo", "imp-placa", "imp-clavo", "imp-tutor", "imp-agujas",
              "placa-bloqueada", "placa-no-bloqueada"} | EMITIDOS

    def chequea(cond, donde):
        for k, v in (cond or {}).items():
            if k in ("ctx", "ctxTodos"):
                for x in v:
                    if x not in CTX_OK and not x.startswith("seg-"):
                        err(f"{nom}: {donde} usa un hecho de contexto desconocido «{x}»")
                continue
            if k not in decs:
                err(f"{nom}: {donde} apunta a la decisión inexistente «{k}»")
                continue
            if not v:
                err(f"{nom}: {donde} tiene lista vacía para «{k}» (nunca se cumplirá)")
            for x in v:
                if x not in opts[k]:
                    err(f"{nom}: {donde} apunta a la opción inexistente «{x}» de {k}")

    for d in P["decisiones"]:
        chequea(d.get("mostrarSi"), f"decisión {d['id']}.mostrarSi")
        for cond in (d.get("mostrarSiAlguno") or []):
            chequea(cond, f"decisión {d['id']}.mostrarSiAlguno")
        for o in d["opciones"]:
            chequea(o.get("soloSi"), f"opción {o['id']}.soloSi")
    for a in P.get("alertas", []):
        chequea(a.get("mostrarSi"), f"alerta {a['id']}")
        chequea(a.get("noSi"), f"alerta {a['id']}.noSi")
        chequea(a.get("noSiTodo"), f"alerta {a['id']}.noSiTodo")
        for cond in (a.get("mostrarSiAlguno") or []):
            chequea(cond, f"alerta {a['id']}.mostrarSiAlguno")
        for cond in (a.get("noSiAlguno") or []):
            chequea(cond, f"alerta {a['id']}.noSiAlguno")
        if not a.get("mostrarSiempre") and not a.get("mostrarSi") \
                and not a.get("mostrarSiAlguno"):
            avi(f"{nom}: la alerta {a['id']} no se mostrará nunca")
    for r in P.get("reglasCoherencia", []):
        si = {k: v for k, v in r["si"].items() if k in decs or not isinstance(v, list)}
        chequea({k: v for k, v in r["si"].items() if isinstance(v, list)}, f"regla {r['id']}")
        chequea(r.get("noSi"), f"regla {r['id']}.noSi")
        chequea(r.get("noSiTodo"), f"regla {r['id']}.noSiTodo")
    for d in P.get("derivados", []):
        for r in d.get("reglas", []):
            chequea(r.get("si"), f"derivado {d['id']}")
        for c in (d.get("campos") or {}).values():
            if c and c not in decs:
                err(f"{nom}: derivado {d['id']} usa el campo inexistente «{c}»")
        for c in (d.get("requiere") or []):
            if c not in decs:
                err(f"{nom}: derivado {d['id']} requiere la decisión inexistente «{c}»")
        if d.get("tipo") == "plantilla" and not (d.get("plantilla") or d.get("texto")):
            err(f"{nom}: derivado {d['id']} es de tipo plantilla y no tiene texto")
        if d.get("tipo") == "reglas" and not d.get("reglas"):
            err(f"{nom}: derivado {d['id']} es de tipo reglas y no tiene reglas")

    # alcanzabilidad de opciones condicionadas
    for d in P["decisiones"]:
        for o in d["opciones"]:
            for k, v in (o.get("soloSi") or {}).items():
                if k in opts and not (set(v) & opts[k]):
                    err(f"{nom}: la opción {o['id']} nunca podrá mostrarse")

    for q in P.get("autoevaluacion", []):
        if not (0 <= q["correcta"] < len(q["opciones"])):
            err(f"{nom}: índice de respuesta fuera de rango en «{q['pregunta'][:40]}…»")
    for rid in P.get("refs", []) + [x for e in P.get("evidencia", []) for x in e.get("refs", [])]:
        if rid not in REFS:
            err(f"{nom}: referencia no definida «{rid}»")

    dup = [d["id"] for d in P.get("derivados", [])]
    if len(dup) != len(set(dup)):
        err(f"{nom}: derivados duplicados {dup}")

    print(f"   {nom:22s} {len(P['decisiones'])} decisiones · "
          f"{sum(len(d['opciones']) for d in P['decisiones'])} opciones · "
          f"{len(P.get('alertas', []))} alertas · {len(P.get('derivados', []))} derivados · "
          f"{len(P.get('autoevaluacion', []))} preguntas")

# -------------------------------------------------------------------- casos
CASOS_F = RAIZ / "content" / "casos.json"
if CASOS_F.exists():
    print()
    print("=" * 62)
    print("3. CASOS POR FALLO — los estados apuntan a decisiones reales")
    print("=" * 62)
    CASOS = json.loads(CASOS_F.read_text(encoding="utf-8"))["casos"]
    PASOS = {}
    for f in sorted((RAIZ / "content" / "pasos").glob("*.json")):
        p = json.loads(f.read_text(encoding="utf-8"))
        PASOS[p["numero"]] = {d["id"]: {o["id"] for o in d["opciones"]} for d in p["decisiones"]}

    vistos = set()
    for c in CASOS:
        if c["id"] in vistos:
            err(f"caso {c['id']}: id repetido")
        vistos.add(c["id"])
        for campo in ("titulo", "region", "resumen", "loQueSeHizo", "porQue", "loQueTocaba", "mensaje"):
            if not c.get(campo):
                err(f"caso {c['id']}: falta «{campo}»")
        if c.get("pasoClave") not in PASOS:
            err(f"caso {c['id']}: pasoClave {c.get('pasoClave')} no existe")
        for cual in ("estadoError", "estadoCorrecto"):
            est = c.get(cual)
            if not est:
                err(f"caso {c['id']}: falta {cual}")
                continue
            for n, dec in est.items():
                if int(n) not in PASOS:
                    err(f"caso {c['id']}.{cual}: el paso {n} no existe")
                    continue
                for k, v in dec.items():
                    if k not in PASOS[int(n)]:
                        err(f"caso {c['id']}.{cual}: paso {n} no tiene la decisión «{k}»")
                        continue
                    for x in (v if isinstance(v, list) else [v]):
                        if x not in PASOS[int(n)][k]:
                            err(f"caso {c['id']}.{cual}: «{x}» no es opción de {k} (paso {n})")
        for rid in c.get("refs", []):
            if rid not in REFS:
                err(f"caso {c['id']}: referencia no definida «{rid}»")
        print(f"   {c['id']:34s} paso {c.get('pasoClave')} · "
              f"{sum(len(d) for d in c.get('estadoError', {}).values())} decisiones erróneas · "
              f"{sum(len(d) for d in c.get('estadoCorrecto', {}).values())} corregidas")

# ------------------------------------------------------------------ informe
print()
print("=" * 62)
if errores:
    print(f"ERRORES ({len(errores)})")
    for e in errores:
        print("   ✗ " + e)
else:
    print("Sin errores.")
if avisos:
    print(f"\nAvisos ({len(avisos)})")
    for a in avisos:
        print("   · " + a)
print("=" * 62)
sys.exit(1 if errores else 0)
