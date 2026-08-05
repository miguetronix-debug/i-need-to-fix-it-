#!/usr/bin/env python3
"""
traducir_paso2.py — Genera el inglés del Paso 2 en `content/traducciones_en.json`.

Por qué el Paso 2 es un caso aparte. El resto de los pasos son la voz del autor
y su traducción exige revisión clínica (eso es la Fase 2). El Paso 2, en cambio,
es el vocabulario de la propia AO, que **nació en inglés**: traducirlo no es
traducir, es devolverlo a su idioma original.

De dónde sale cada cosa:
  · Los 80 segmentos con figura salen **del compendio**, campo `texto`, que es
    el documento original de la AO. No se inventa nada.
  · Los huesos, los modificadores universales y los 5 segmentos que el compendio
    no nombra van en las tablas de abajo, con la terminología oficial.
  · Las clasificaciones regionales llevan sus términos epónimos estándar.

Lo que NO toca: alertas, criterios, recuadros y desarrollo del Paso 2, que sí
son texto redactado. Esos esperan a la Fase 2.

Uso:  python3 tools/traducir_paso2.py && python3 tools/build_prototipo.py
"""

import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "content" / "traducciones_en.json"

PREGUNTAS = {
    "hueso": "Which bone?",
    "segmento": "Which segment?",
    "identificador": "Which one?",
    "tipo": "Which type?",
    "grupo": "Which group?",
    "subgrupo": "Which subgroup?",
    "calificaciones": "Qualifications",
    "modificadores": "Universal modifiers",
    "cl-schatzker": "Tibial plateau · Schatzker as modified by Kfuri: which type?",
    "cl-columnas": "Tibial plateau · Schatzker as modified by Kfuri: which quadrants are broken?",
    "cl-garden": "Femoral neck · Garden",
    "cl-pauwels": "Femoral neck · Pauwels",
    "cl-neer": "Proximal humerus · Neer",
    "cl-hertel": "Proximal humerus · any predictors of head ischaemia?",
    "cl-hawkins": "Talus · Hawkins",
    "cl-sanders": "Calcaneus · Sanders",
    "cl-letournel": "Acetabulum · Letournel and Judet",
    "cl-young-burgess": "Pelvic ring · Young and Burgess",
    "cl-tile": "Pelvic ring · Tile stability",
    "cl-vancouver": "Is it periprosthetic? · Vancouver",
    "cl-winquist": "Femoral shaft · Winquist and Hansen comminution",
    "cl-mason": "Radial head · Mason",
    "cl-lauge-hansen": "Ankle · Lauge-Hansen mechanism",
}

HUESOS = {
    "h-1": "1 · Humerus", "h-14": "14 · Scapula", "h-15": "15 · Clavicle",
    "h-16": "16 · Thorax — ribs and sternum", "h-2R": "2R · Radius", "h-2U": "2U · Ulna",
    "h-3": "3 · Femur", "h-34": "34 · Patella", "h-4": "4 · Tibia", "h-4F": "4F · Fibula",
    "h-6": "6 · Pelvis and acetabulum", "h-7": "7 · Hand and carpus", "h-8": "8 · Foot",
    "h-5": "5 · Spine",
}

# Los cinco que el compendio no nombra por su cuenta
SEGMENTOS_EXTRA = {
    "s-2R1": "2R1 · Radius, proximal end segment",
    "s-2R3": "2R3 · Radius, distal end segment",
    "s-51._": "51._ · Cervical spine · ._",
    "s-53": "53 · Lumbar spine",
    "s-78._.1": "78._.1 · Phalanges of the hand · ._.1",
}

MODIFICADORES = {
    "m-1": "[1] Undisplaced", "m-2": "[2] Displaced",
    "m-3a": "[3a] Articular impaction", "m-3b": "[3b] Metaphyseal impaction",
    "m-4": "[4] No impaction",
    "m-5a": "[5a] Anterior (volar, palmar, plantar)", "m-5b": "[5b] Posterior (dorsal)",
    "m-5c": "[5c] Medial (ulnar)", "m-5d": "[5d] Lateral (radial)",
    "m-5e": "[5e] Inferior (at the hip, also obturator)", "m-5f": "[5f] Multidirectional",
    "m-6a": "[6a] Anterior (volar, palmar, plantar)", "m-6b": "[6b] Posterior (dorsal)",
    "m-6c": "[6c] Medial (ulnar)", "m-6d": "[6d] Lateral (radial)",
    "m-6e": "[6e] Inferior (at the hip, also obturator)", "m-6f": "[6f] Multidirectional",
    "m-7": "[7] Diaphyseal extension",
    "m-8a": "[8a] ICRS grade 0 — normal",
    "m-8b": "[8b] ICRS grade 1 — superficial indentation and/or superficial fissures and cracks",
    "m-8c": "[8c] ICRS grade 2 — abnormal lesions extending down to less than 50% of cartilage depth",
    "m-8d": "[8d] ICRS grade 3 — severely abnormal, defects extending down more than 50% of cartilage depth; down to the calcified layer; down to but not through the subchondral bone; includes blisters",
    "m-8e": "[8e] ICRS grade 4 — cartilage loss extending through the subchondral bone",
    "m-9": "[9] Poor bone quality", "m-10": "[10] Replantation",
    "m-11": "[11] Amputation associated with the fracture",
    "m-12": "[12] Associated with a non-prosthetic implant",
    "m-13": "[13] Spiral-type fracture", "m-14": "[14] Bending-type fracture",
}

CLASIFICACIONES = {
    "cl-schatzker": {
        "sch-I": "I · Pure lateral split", "sch-II": "II · Lateral split-depression",
        "sch-III": "III · Pure lateral depression", "sch-IV": "IV · Medial plateau",
        "sch-V": "V · Bicondylar",
        "sch-VI": "VI · Bicondylar with metaphyseal-diaphyseal dissociation"},
    "cl-columnas": {
        "col-antero-lat": "Anterolateral", "col-antero-med": "Anteromedial",
        "col-post-lat": "Posterolateral", "col-post-med": "Posteromedial"},
    "cl-garden": {
        "gar-nd": "Undisplaced · Garden I-II", "gar-d": "Displaced · Garden III-IV"},
    "cl-pauwels": {
        "pau-I": "I · less than 30°", "pau-II": "II · 30 to 50°", "pau-III": "III · more than 50°"},
    "cl-neer": {
        "neer-1": "1 part · undisplaced", "neer-2cq": "2 parts · surgical neck",
        "neer-2tro": "2 parts · greater tuberosity", "neer-3": "3 parts",
        "neer-4": "4 parts", "neer-lux": "Fracture-dislocation"},
    "cl-hertel": {
        "her-calcar": "Metaphyseal head extension shorter than 8 mm",
        "her-bisagra": "Medial hinge disrupted, displaced more than 2 mm",
        "her-basi": "Basicervical fracture line", "her-no": "None of the three"},
    "cl-hawkins": {
        "haw-I": "I · Undisplaced neck",
        "haw-II": "II · With subtalar subluxation or dislocation",
        "haw-III": "III · Subtalar and tibiotalar dislocation",
        "haw-IV": "IV · Adds talonavicular dislocation"},
    "cl-sanders": {
        "san-I": "I · Undisplaced", "san-II": "II · Two articular fragments",
        "san-III": "III · Three fragments", "san-IV": "IV · Four or more fragments"},
    "cl-letournel": {
        "let-pared-post": "Posterior wall", "let-columna-post": "Posterior column",
        "let-pared-ant": "Anterior wall", "let-columna-ant": "Anterior column",
        "let-transversa": "Transverse", "let-t": "T-shaped",
        "let-post-post": "Posterior column with posterior wall",
        "let-transv-pp": "Transverse with posterior wall",
        "let-hemitransv": "Anterior column with posterior hemitransverse",
        "let-ambas": "Both-column"},
    "cl-young-burgess": {
        "yb-lc1": "Lateral compression I", "yb-lc2": "Lateral compression II",
        "yb-lc3": "Lateral compression III · windswept",
        "yb-apc1": "Anteroposterior compression I",
        "yb-apc2": "Anteroposterior compression II · open book",
        "yb-apc3": "Anteroposterior compression III",
        "yb-vs": "Vertical shear", "yb-cm": "Combined mechanism"},
    "cl-tile": {
        "tile-A": "A · Stable",
        "tile-B": "B · Rotationally unstable, vertically stable",
        "tile-C": "C · Rotationally and vertically unstable"},
    "cl-vancouver": {
        "van-no": "Not periprosthetic", "van-A": "A · Trochanteric",
        "van-B1": "B1 · Around the stem, stem well fixed",
        "van-B2": "B2 · Stem loose, adequate bone stock",
        "van-B3": "B3 · Stem loose and poor bone stock",
        "van-C": "C · Distal to the tip of the stem"},
    "cl-winquist": {
        "win-0": "0 · No comminution", "win-I": "I · Small fragment",
        "win-II": "II · Between 25 and 50%", "win-III": "III · More than 50%",
        "win-IV": "IV · Segmental, no cortical contact"},
    "cl-mason": {
        "mas-I": "I · Undisplaced", "mas-II": "II · Displaced, single fragment",
        "mas-III": "III · Comminuted", "mas-IV": "IV · With elbow dislocation"},
    "cl-lauge-hansen": {
        "lh-sa": "Supination-adduction", "lh-ser": "Supination-external rotation",
        "lh-pa": "Pronation-abduction", "lh-per": "Pronation-external rotation"},
}


def main():
    paso2 = json.loads((RAIZ / "content" / "pasos" / "02-clasificacion.json").read_text(encoding="utf-8"))
    codigos = json.loads((RAIZ / "content" / "aoota_codigos.json").read_text(encoding="utf-8"))["codigos"]
    decs = {d["id"]: d for d in paso2["decisiones"]}

    salida = {"_nota": "Inglés del Paso 2, generado por tools/traducir_paso2.py. "
                       "Los segmentos vienen del compendio AO original; el resto, "
                       "de las tablas del script. No editar a mano: editar el script.",
              "pasos": {"2": {"decisiones": {}}}}
    dst = salida["pasos"]["2"]["decisiones"]

    for did, preg in PREGUNTAS.items():
        if did in decs:
            dst[did] = {"pregunta": preg, "opciones": {}}

    # huesos y modificadores, de tabla
    for did, tabla in (("hueso", HUESOS), ("modificadores", MODIFICADORES)):
        if did in dst:
            dst[did]["opciones"].update(tabla)

    # segmentos: del compendio, que es la fuente original
    delCompendio = 0
    if "segmento" in dst:
        for o in decs["segmento"]["opciones"]:
            c = o.get("codigo", "")
            en = (codigos.get(c) or {}).get("texto", "")
            if en:
                dst["segmento"]["opciones"][o["id"]] = f"{c} · {en}"
                delCompendio += 1
        dst["segmento"]["opciones"].update(SEGMENTOS_EXTRA)

    # clasificaciones regionales
    for did, tabla in CLASIFICACIONES.items():
        if did in dst:
            dst[did]["opciones"].update(tabla)

    # aviso si alguna opción se quedó sin pareja
    huecos = []
    for did, d in dst.items():
        if did in ("tipo", "grupo", "subgrupo", "identificador", "calificaciones"):
            continue   # son código o ya vienen en inglés del compendio
        faltan = [o["id"] for o in decs[did]["opciones"] if o["id"] not in d["opciones"]]
        if faltan:
            huecos.append((did, faltan))

    SALIDA.write_text(json.dumps(salida, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    total = sum(len(d["opciones"]) for d in dst.values())
    print(f"Generado: {SALIDA.name}")
    print(f"   {len(dst)} preguntas · {total} etiquetas")
    print(f"   {delCompendio} segmentos tomados del inglés original del compendio AO")
    if huecos:
        print("   AVISO — opciones sin traducir:")
        for did, f in huecos:
            print(f"      {did}: {len(f)} → {f[:6]}")
    else:
        print("   Sin huecos: todas las opciones traducibles tienen pareja.")


if __name__ == "__main__":
    main()
