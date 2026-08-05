#!/usr/bin/env python3
"""
build_paso2.py — Regenera las DECISIONES y los DERIVADOS del Paso 2 a partir
de content/aoota_codigos.json (compendio AO/OTA 2018 completo), conservando
el contenido redactado a mano (esencial, autoevaluación, evidencia, síntesis).

Navega por PREFIJOS de código en vez de asumir una jerarquía uniforme, porque
la del compendio no lo es: la escápula usa la letra como localización, la
clavícula segmenta con decimales, y la mano y el pie llevan un identificador
de radio o dedo.

Uso:  python3 tools/build_paso2.py
"""

import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
COD = json.loads((RAIZ / "content" / "aoota_codigos.json").read_text(encoding="utf-8"))["codigos"]
AO = json.loads((RAIZ / "content" / "aoota.json").read_text(encoding="utf-8"))
DEST = RAIZ / "content" / "pasos" / "02-clasificacion.json"
P = json.loads(DEST.read_text(encoding="utf-8"))

# ------------------------------------------------------------------ nombres
HUESOS = [
    ("1", "Húmero", ["11", "12", "13"]),
    ("14", "Escápula", ["14"]),
    ("15", "Clavícula", ["15"]),
    ("16", "Tórax — costillas y esternón", ["16"]),
    ("2R", "Radio", ["2R1", "2R2", "2R3"]),
    ("2U", "Cúbito", ["2U1", "2U2", "2U3"]),
    ("3", "Fémur", ["31", "32", "33"]),
    ("34", "Rótula", ["34"]),
    ("4", "Tibia", ["41", "42", "43", "44"]),
    ("4F", "Peroné", ["4F1", "4F2", "4F3"]),
    ("6", "Pelvis y acetábulo", ["61", "62"]),
    ("7", "Mano y carpo", ["71", "72", "73", "74", "75", "76", "77", "78"]),
    ("8", "Pie", ["81", "82", "83", "84", "85", "87", "88"]),
    ("5", "Columna", ["51", "52", "53"]),
]
SEG_ES = {
    "11": "Húmero proximal", "12": "Diáfisis humeral", "13": "Húmero distal",
    "14": "Escápula", "15": "Clavícula", "16": "Tórax",
    "2R1": "Radio proximal", "2R2": "Diáfisis del radio", "2R3": "Radio distal",
    "2U1": "Cúbito proximal", "2U2": "Diáfisis del cúbito", "2U3": "Cúbito distal",
    "31": "Fémur proximal", "32": "Diáfisis femoral", "33": "Fémur distal", "34": "Rótula",
    "41": "Tibia proximal", "42": "Diáfisis tibial", "43": "Tibia distal (pilón)",
    "44": "Segmento maleolar", "4F1": "Peroné proximal", "4F2": "Diáfisis del peroné",
    "4F3": "Peroné distal", "51": "Cervical", "52": "Torácica", "53": "Lumbar",
    "61": "Anillo pélvico", "62": "Acetábulo",
    "71": "Semilunar", "72": "Escafoides", "73": "Grande", "74": "Ganchoso",
    "75": "Trapecio", "76": "Otros carpianos", "77": "Metacarpianos", "78": "Falanges de la mano",
    "81": "Astrágalo", "82": "Calcáneo", "83": "Escafoides tarsiano", "84": "Cuboides",
    "85": "Cuñas", "87": "Metatarsianos", "88": "Falanges del pie",
}
IDENT = {
    "77": ("¿Qué metacarpiano?", ["Pulgar (1)", "Índice (2)", "Medio (3)", "Anular (4)", "Meñique (5)"]),
    "78": ("¿Qué dedo y qué falange?", None),
    "87": ("¿Qué metatarsiano?", ["1.º", "2.º", "3.º", "4.º", "5.º"]),
    "88": ("¿Qué dedo y qué falange?", None),
    "16": ("¿Qué costilla y qué zona?", None),
    "51": ("¿Qué vértebra cervical?", None),
    "52": ("¿Qué vértebra torácica?", None),
    "53": ("¿Qué vértebra lumbar?", None),
}


def hueso_de(seg):
    base = seg.split(".")[0]
    for cod, _, segs in HUESOS:
        if seg in segs or base in segs:
            return cod
    return base


def nombre_seg(seg):
    base = seg.split(".")[0]
    es = SEG_ES.get(seg) or SEG_ES.get(base) or base
    extra = seg[len(base):]
    return f"{es}{' · ' + extra if extra else ''}"


# --------------------------------------------------------------- decisiones
segmentos = sorted({v["segmento"] for v in COD.values()})
d_hueso = {"id": "hueso", "pregunta": "¿Qué hueso?",
           "ayuda": "Primer dígito del código. Desde 2018 los huesos pareados se codifican por separado: radio 2R, cúbito 2U, peroné 4F.",
           "tipo": "opcionUnica", "opciones": []}
for cod, nombre, segs in HUESOS:
    presentes = [s for s in segmentos if hueso_de(s) == cod]
    if not presentes:
        continue
    d_hueso["opciones"].append({
        "id": "h-" + cod, "etiqueta": f"{cod} · {nombre}", "codigo": "",
        "criterios": [" · ".join(sorted({s.split('.')[0] for s in presentes}))]})

d_seg = {"id": "segmento", "pregunta": "¿Qué segmento?",
         "ayuda": "Determina qué significará la letra que viene después.",
         "tipo": "opcionUnica", "opciones": []}
for s in segmentos:
    reg = COD.get(s, {})
    crit = [reg["texto"]] if reg.get("texto") else []
    if "_" in s:
        crit.append("Lleva identificador: se completa en el paso siguiente.")
    d_seg["opciones"].append({
        "id": "s-" + s, "etiqueta": f"{s} · {nombre_seg(s)}", "codigo": s,
        "soloSi": {"hueso": ["h-" + hueso_de(s)]}, "criterios": crit})

# identificador (radio, dedo, costilla, vértebra)
d_id = {"id": "identificador", "pregunta": "¿Cuál?",
        "ayuda": "El compendio deja un hueco entre puntos para el número de radio, dedo, costilla o vértebra.",
        "tipo": "opcionUnica", "opciones": []}
for s in segmentos:
    if "_" not in s:
        continue
    base = s.split(".")[0]
    n = s.count("_")
    etiquetas = (IDENT.get(base) or (None, None))[1]
    valores = [str(i) for i in range(1, 6)] if n == 1 else [f"{i}.{j}" for i in range(1, 6) for j in range(1, 4)]
    for v in valores:
        et = v
        if n == 1 and etiquetas and v.isdigit() and int(v) <= len(etiquetas):
            et = etiquetas[int(v) - 1]
        elif n == 2:
            dedo, fal = v.split(".")
            et = f"Dedo {dedo} · falange {['proximal','media','distal'][int(fal)-1]}"
        d_id["opciones"].append({
            "id": f"i-{s}-{v}", "etiqueta": et, "codigo": v,
            "soloSi": {"segmento": ["s-" + s]}, "criterios": []})

# tipo / grupo / subgrupo por prefijo
def hijos(nivel, padre_codigo):
    out = []
    for c, v in COD.items():
        if v["nivel"] != nivel:
            continue
        if nivel == "tipo" and v["segmento"] != padre_codigo:
            continue
        if nivel in ("grupo", "subgrupo") and not c.startswith(padre_codigo):
            continue
        if nivel == "grupo" and len(c) != len(padre_codigo) + 1:
            continue
        if nivel == "subgrupo" and not re.fullmatch(re.escape(padre_codigo) + r"\.\d", c):
            continue
        out.append((c, v))
    return sorted(out)


d_tipo = {"id": "tipo", "pregunta": "¿Qué tipo?",
          "ayuda": "La letra. Significa cosas distintas según el segmento: en diáfisis habla de fragmentación, en segmento terminal de afectación articular, en la escápula de localización.",
          "tipo": "opcionUnica", "opciones": []}
d_grupo = {"id": "grupo", "pregunta": "¿Qué grupo?", "ayuda": "El número tras la letra.",
           "tipo": "opcionUnica", "opciones": []}
d_sub = {"id": "subgrupo", "pregunta": "¿Qué subgrupo?",
         "ayuda": "El decimal final. Máximo detalle; la concordancia entre observadores baja mucho a este nivel.",
         "tipo": "opcionUnica", "opciones": []}
d_calif = {"id": "calificaciones", "pregunta": "Calificaciones",
           "ayuda": "Letras minúsculas entre paréntesis, propias de esta fractura. Opcionales y acumulables.",
           "tipo": "opcionMultiple", "opciones": []}

vistos_q = set()


def añade_califs(codigo, dec_padre, id_padre):
    for q in COD.get(codigo, {}).get("calificaciones", []):
        qid = f"q-{codigo}-{q['letra']}"
        if qid in vistos_q:
            continue
        vistos_q.add(qid)
        d_calif["opciones"].append({
            "id": qid, "etiqueta": f"({q['letra']}) {q['texto']}", "codigo": q["letra"],
            "soloSi": {dec_padre: [id_padre]}, "criterios": []})


for s in segmentos:
    for ct, vt in hijos("tipo", s):
        tid = "t-" + ct
        d_tipo["opciones"].append({
            "id": tid, "etiqueta": f"{vt.get('letra','')} — {ct}", "codigo": vt.get("letra", ""),
            "codigoCompleto": ct,
            "soloSi": {"segmento": ["s-" + s]}, "criterios": [vt["texto"]] if vt["texto"] else []})
        añade_califs(ct, "tipo", tid)
        for cg, vg in hijos("grupo", ct):
            gid = "g-" + cg
            d_grupo["opciones"].append({
                "id": gid, "etiqueta": f"{vt.get('letra','')}{vg.get('grupo','')} — {cg}",
                "codigo": vg.get("grupo", ""), "codigoCompleto": cg, "soloSi": {"tipo": [tid]},
                "criterios": [vg["texto"]] if vg["texto"] else []})
            añade_califs(cg, "grupo", gid)
            for cs, vs in hijos("subgrupo", cg):
                sid = "sg-" + cs
                d_sub["opciones"].append({
                    "id": sid, "etiqueta": f".{vs.get('subgrupo','')} — {cs}",
                    "codigo": "." + vs.get("subgrupo", ""), "codigoCompleto": cs,
                    "soloSi": {"grupo": [gid]},
                    "criterios": [vs["texto"]] if vs["texto"] else []})
                añade_califs(cs, "subgrupo", sid)

d_mod = {"id": "modificadores", "pregunta": "Modificadores universales",
         "ayuda": "Entre corchetes al final. Se aplican a casi cualquier fractura y son opcionales.",
         "tipo": "opcionMultiple", "opciones": []}
for m in AO["estructura"]["modificadoresUniversales"]["lista"]:
    for x in (m.get("sub") or [m]):
        d_mod["opciones"].append({
            "id": f"m-{x['n']}", "etiqueta": f"[{x['n']}] {x['texto']}", "codigo": x["n"],
            "criterios": [m["texto"]] if m.get("sub") else []})

P["decisiones"] = [d_hueso, d_seg, d_id, d_tipo, d_grupo, d_sub, d_calif, d_mod]

# ---------------------------------------------------------------- derivados
P["derivados"] = [
    {"id": "codigo", "titulo": "Código AO/OTA 2018", "tipo": "codigoAO",
     "campos": {"segmento": "segmento", "identificador": "identificador", "tipo": "tipo",
                "grupo": "grupo", "subgrupo": "subgrupo",
                "calificaciones": "calificaciones", "modificadores": "modificadores"},
     "nota": "Sin guion: la revisión 2018 lo eliminó. Orden: hueso · localización · tipo · grupo · subgrupo · (calificaciones) · [modificadores]."},
    {"id": "oficial", "titulo": "Descripción oficial del compendio", "tipo": "textoCodigo"},
]

# ------------------------------------------------------------------ alertas
DIAF = [s for s in segmentos if s in ("12", "2R2", "2U2", "32", "42", "4F2")]
ART = [s for s in segmentos if s in ("11", "13", "2R1", "2R3", "2U1", "2U3", "31", "33",
                                     "34", "41", "43", "44", "62")]
P["alertas"] = [
    {"id": "volver-paso-1", "severidad": "media", "titulo": "La trampa mayor: clasificar sin evaluar",
     "texto": "Una etiqueta ósea perfecta sobre un huésped o unas partes blandas mal valoradas conduce al fracaso. Si no has completado el Paso 1, vuelve antes de seguir.",
     "mostrarSiempre": True},
    {"id": "letra-contexto", "severidad": "media", "titulo": "Lee la letra en su contexto",
     "texto": "Estás en un segmento articular: aquí A significa extraarticular, no «simple».",
     "mostrarSi": {"segmento": ["s-" + s for s in ART]}},
    {"id": "sin-b1-c1", "severidad": "media", "titulo": "En diáfisis ya no existen B1 ni C1",
     "texto": "La revisión 2018 eliminó la cuña espiroidea (B1) y la compleja espiroidea (C1). Los grupos diafisarios son A1, A2, A3, B2, B3, C2 y C3.",
     "mostrarSi": {"segmento": ["s-" + s for s in DIAF]}},
    {"id": "escapula-letra", "severidad": "alta", "titulo": "En la escápula la letra es la localización",
     "texto": "14A es el proceso, 14B el cuerpo y 14F la fosa glenoidea —con F, no con C—. El glenoides además tiene un grupo 0 (14F0) para el cuello extraarticular.",
     "mostrarSi": {"segmento": ["s-14"]}},
    {"id": "identificador", "severidad": "media", "titulo": "Este hueso lleva identificador",
     "texto": "El compendio deja un hueco entre puntos para el número de radio, dedo, costilla o vértebra. Sin rellenarlo el código queda incompleto.",
     "mostrarSi": {"segmento": ["s-" + s for s in segmentos if "_" in s]}},
    {"id": "tc-articular", "severidad": "alta", "titulo": "Articular: la TC afina y con frecuencia reclasifica",
     "texto": "En meseta, pilón, calcáneo, húmero distal, radio distal y acetábulo la tomografía cambia a menudo el tipo, revela fragmentos clave y guía el abordaje. No es requisito para clasificar, pero sin ella se subestima la lesión.",
     "mostrarSi": {"segmento": ["s-" + s for s in ("41", "43", "82", "13", "2R3", "62", "33")]}},
    {"id": "sindesmosis", "severidad": "alta", "titulo": "Comprobar la sindesmosis",
     "texto": "En el trazo transindesmal la lesión sindesmal es variable y en el suprasindesmal es constante. Su malreducción es la complicación clave del tobillo.",
     "mostrarSi": {"tipo": ["t-44B", "t-44C"]}},
    {"id": "pared-lateral", "severidad": "alta", "titulo": "Pared lateral incompetente",
     "texto": "El grupo 31A2 incorpora el umbral de pared lateral ≤ 20,5 mm. Con la pared lateral incompetente el DHS falla: la indicación es clavo cefalomedular.",
     "mostrarSi": {"grupo": ["g-31A2"]}},
    {"id": "subgrupos-finos", "severidad": "media", "titulo": "Fiabilidad: buena para el tipo, menor para el subgrupo",
     "texto": "La concordancia entre observadores es buena para la letra y disminuye en grupos y subgrupos. Sirve para decidir la estrategia, no para discutir distinciones milimétricas.",
     "mostrarSi": {"subgrupo": [o["id"] for o in d_sub["opciones"]]}},
]
P["reglasCoherencia"] = []
P["refs"] = ["ref-aoota-2018", "ref-giannoudis-clasif"]

DEST.write_text(json.dumps(P, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Escrito: {DEST}")
for d in P["decisiones"]:
    print(f"  {d['id']:16s} {d['tipo']:15s} {len(d['opciones']):5d} opciones")
print(f"  total: {sum(len(d['opciones']) for d in P['decisiones'])} opciones · "
      f"{len(P['alertas'])} alertas · {len(P['derivados'])} derivados")
