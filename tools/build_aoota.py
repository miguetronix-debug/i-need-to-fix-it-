#!/usr/bin/env python3
"""
build_aoota.py — Genera content/aoota.json a partir de los datos del
folleto oficial «AO/OTA Fracture and Dislocation Classification —
Introduction to the classification of long-bone fractures»
(AOE-E1-018.10, © 2018 AO Foundation), aportado por el autor.

Los grupos transcritos aquí son los que el folleto ilustra. Algunos grupos
existen en el compendio completo pero no se ilustran en el folleto; se
marcan con "noIlustrado": true.

Uso:  python3 tools/build_aoota.py
"""

import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "content" / "aoota.json"

Q_DIAF_AB = [{"letra": "a", "texto": "Tercio proximal"},
             {"letra": "b", "texto": "Tercio medio"},
             {"letra": "c", "texto": "Tercio distal"}]
Q_DIAF_C = [{"letra": "i", "texto": "Diafisometafisaria proximal"},
            {"letra": "j", "texto": "Puramente diafisaria"},
            {"letra": "k", "texto": "Diafisometafisaria distal"}]


def diafisario(pref):
    """Grupos diafisarios de la revisión 2018. B1 y C1 ya no existen."""
    return {
        "clase": "diafisario",
        "tipos": [
            {"letra": "A", "nombre": "Simple",
             "definicion": "Trazo único circunferencial.",
             "grupos": [
                 {"n": "1", "nombre": "Espiroidea"},
                 {"n": "2", "nombre": "Oblicua (≥ 30°)"},
                 {"n": "3", "nombre": "Transversa (< 30°)"}],
             "calificaciones": Q_DIAF_AB},
            {"letra": "B", "nombre": "En cuña",
             "definicion": "Uno o más fragmentos intermedios; tras la reducción queda contacto cortical entre los fragmentos principales.",
             "grupos": [
                 {"n": "2", "nombre": "Cuña intacta"},
                 {"n": "3", "nombre": "Cuña fragmentaria"}],
             "calificaciones": Q_DIAF_AB},
            {"letra": "C", "nombre": "Multifragmentaria",
             "definicion": "Uno o más fragmentos intermedios; tras la reducción NO queda contacto entre los fragmentos principales.",
             "grupos": [
                 {"n": "2", "nombre": "Segmentaria intacta"},
                 {"n": "3", "nombre": "Segmentaria fragmentaria"}],
             "calificaciones": Q_DIAF_C}
        ]
    }


def seg(codigo, nombre, clase, tipos, **extra):
    d = {"id": "s-" + codigo, "codigo": codigo, "nombre": nombre, "clase": clase, "tipos": tipos}
    d.update(extra)
    return d


def diaf_seg(codigo, nombre="Diáfisis"):
    d = diafisario(codigo)
    return seg(codigo, nombre, "diafisario", d["tipos"])


T = lambda letra, nombre, grupos, **kw: dict({"letra": letra, "nombre": nombre, "grupos": grupos}, **kw)
G = lambda n, nombre, **kw: dict({"n": n, "nombre": nombre}, **kw)
FALTA = {"noIlustrado": True, "nota": "Existe en el compendio; el folleto no lo ilustra."}

HUESOS = [
    {"id": "h1", "codigo": "1", "nombre": "Húmero", "segmentos": [
        seg("11", "Segmento proximal", "terminal", [
            T("A", "Extraarticular, unifocal, 2 partes", [
                G("1", "Tuberosidad"), G("2", "Cuello quirúrgico"), G("3", "Vertical")]),
            T("B", "Extraarticular, bifocal, 3 partes", [
                G("1", "Cuello quirúrgico")],
              nota="No es una fractura intraarticular."),
            T("C", "Articular o de 4 partes", [
                G("1", "Cuello anatómico"),
                G("3", "Cuello anatómico con fractura metafisaria asociada")])
        ], excepcion=True, nota2018="La clasificación de Neer quedó integrada: 11A = 2 partes, 11B = 3 partes, 11C = articular o 4 partes."),
        diaf_seg("12"),
        seg("13", "Segmento distal", "terminal", [
            T("A", "Extraarticular", [
                G("1", "Avulsión"), G("2", "Simple"), G("3", "En cuña o multifragmentaria")]),
            T("B", "Articular parcial", [
                G("1", "Sagital lateral"), G("2", "Sagital medial"), G("3", "Plano frontal/coronal")]),
            T("C", "Articular completa", [
                G("1", "Articular simple, metafisaria simple"),
                G("2", "Articular simple, metafisaria en cuña o multifragmentaria"),
                G("3", "Articular multifragmentaria, metafisaria en cuña o multifragmentaria")])
        ])
    ]},

    {"id": "h14", "codigo": "14", "nombre": "Escápula", "segmentos": [],
     "nota": "Incluida en el compendio 2018. El folleto de huesos largos no la desarrolla."},
    {"id": "h15", "codigo": "15", "nombre": "Clavícula", "segmentos": [],
     "nota": "Incluida en el compendio 2018. El folleto de huesos largos no la desarrolla."},
    {"id": "h16", "codigo": "16", "nombre": "Tórax", "segmentos": [],
     "nota": "Costillas y esternón. Fuera del alcance del libro."},

    {"id": "h2R", "codigo": "2R", "nombre": "Radio", "segmentos": [
        seg("2R1", "Segmento proximal", "terminal", [
            T("A", "Extraarticular", [
                G("1", "Avulsión de la tuberosidad bicipital"),
                G("2", "Cuello, simple"), G("3", "Cuello, multifragmentaria")]),
            T("B", "Articular parcial", [
                G("1", "Simple"), G("3", "Fragmentaria")]),
            T("C", "Articular completa", [
                G("1", "Simple"), G("3", "Multifragmentaria")])
        ]),
        diaf_seg("2R2"),
        seg("2R3", "Segmento distal", "terminal", [
            T("A", "Extraarticular", [
                G("1", "Avulsión de la estiloides radial"),
                G("2", "Simple"), G("3", "En cuña o multifragmentaria")]),
            T("B", "Articular parcial", [
                G("1", "Sagital"),
                G("2", "Reborde dorsal (Barton)"),
                G("3", "Reborde volar (Barton invertida, Goyrand-Smith II)")]),
            T("C", "Articular completa", [
                G("1", "Articular y metafisaria simples"),
                G("2", "Metafisaria multifragmentaria"),
                G("3", "Articular multifragmentaria, metafisaria simple o multifragmentaria")])
        ])
    ]},

    {"id": "h2U", "codigo": "2U", "nombre": "Cúbito", "segmentos": [
        seg("2U1", "Segmento proximal", "terminal", [
            T("A", "Extraarticular", [
                G("1", "Avulsión de la inserción del tríceps"),
                G("2", "Metafisaria simple"), G("3", "Metafisaria multifragmentaria")]),
            T("B", "Articular parcial", [
                G("1", "Olécranon", calificaciones=[
                    {"letra": "d", "texto": "Simple"}, {"letra": "e", "texto": "Multifragmentaria"}]),
                G("2", "Coronoides", calificaciones=[
                    {"letra": "n", "texto": "Afecta a la faceta sublime"},
                    {"letra": "o", "texto": "Punta (avulsión)"},
                    {"letra": "p", "texto": "< 50 %"},
                    {"letra": "q", "texto": "≥ 50 %"}])]),
            T("C", "Articular completa", [
                G("3", "Olécranon y coronoides", calificaciones=[
                    {"letra": "d", "texto": "Simple"},
                    {"letra": "r", "texto": "Olécranon multifragmentario"}])])
        ]),
        diaf_seg("2U2"),
        seg("2U3", "Segmento distal", "terminal", [
            T("A", "Extraarticular", [
                G("1", "Apófisis estiloides"), G("2", "Simple"), G("3", "Multifragmentaria")]),
            T("B", "Articular parcial", [], **FALTA),
            T("C", "Articular completa", [], **FALTA)
        ])
    ]},

    {"id": "h3", "codigo": "3", "nombre": "Fémur", "segmentos": [
        seg("31", "Segmento proximal", "terminal", [
            T("A", "Región trocantérea", [
                G("1", "Pertrocantérea simple"),
                G("2", "Pertrocantérea multifragmentaria, pared lateral incompetente (≤ 20,5 mm)"),
                G("3", "Intertrocantérea (oblicuidad invertida)")]),
            T("B", "Cuello femoral", [
                G("1", "Subcapital"), G("2", "Transcervical"), G("3", "Basicervical")]),
            T("C", "Cabeza femoral", [
                G("2", "Hundimiento")])
        ], excepcion=True,
            definicion="No se define por la regla del cuadrado: es la zona por encima de una línea perpendicular a la diáfisis situada en el borde inferior del trocánter menor."),
        diaf_seg("32"),
        seg("33", "Segmento distal", "terminal", [
            T("A", "Extraarticular", [
                G("1", "Avulsión"), G("2", "Simple"), G("3", "En cuña o multifragmentaria")]),
            T("B", "Articular parcial", [
                G("1", "Cóndilo lateral, sagital"),
                G("2", "Cóndilo medial, sagital"),
                G("3", "Frontal/coronal (Hoffa)")]),
            T("C", "Articular completa", [
                G("1", "Articular simple, metafisaria simple"),
                G("2", "Articular simple, metafisaria en cuña o multifragmentaria"),
                G("3", "Articular multifragmentaria")])
        ])
    ]},
    {"id": "h34", "codigo": "34", "nombre": "Rótula", "segmentos": [],
     "nota": "Código propio en el compendio 2018. El folleto de huesos largos no la desarrolla."},

    {"id": "h4", "codigo": "4", "nombre": "Tibia", "segmentos": [
        seg("41", "Segmento proximal", "terminal", [
            T("A", "Extraarticular", [
                G("1", "Avulsión"), G("2", "Simple"), G("3", "En cuña o multifragmentaria")]),
            T("B", "Articular parcial", [
                G("1", "Separación (split)"), G("2", "Hundimiento"), G("3", "Separación-hundimiento")]),
            T("C", "Articular completa", [
                G("1", "Articular simple, metafisaria simple"),
                G("2", "Articular simple, metafisaria en cuña o multifragmentaria"),
                G("3", "Metafisaria fragmentaria o multifragmentaria")])
        ], satelite="schatzker-kfuri"),
        diaf_seg("42"),
        seg("43", "Segmento distal (pilón)", "terminal", [
            T("A", "Extraarticular", [
                G("1", "Simple"), G("2", "En cuña"), G("3", "Multifragmentaria")]),
            T("B", "Articular parcial", [
                G("1", "Separación (split)"), G("2", "Separación-hundimiento"), G("3", "Hundimiento")]),
            T("C", "Articular completa", [
                G("1", "Articular simple, metafisaria simple"),
                G("2", "Articular simple, metafisaria multifragmentaria"),
                G("3", "Articular multifragmentaria")])
        ]),
        seg("44", "Segmento maleolar", "terminal", [
            T("A", "Lesión peronea infrasindesmal", [
                G("1", "Lesión peronea aislada"),
                G("2", "Con fractura del maléolo medial"),
                G("3", "Con fractura posteromedial")]),
            T("B", "Fractura peronea transindesmal", [
                G("1", "Fractura peronea simple"),
                G("2", "Con lesión medial"),
                G("3", "Con lesión medial y fractura del reborde posterolateral (fragmento de Volkmann)")]),
            T("C", "Fractura peronea suprasindesmal", [
                G("1", "Fractura diafisaria peronea simple"),
                G("2", "Fractura diafisaria peronea en cuña o multifragmentaria"),
                G("3", "Lesión peronea proximal")])
        ], excepcion=True, nota="Cuarto segmento propio de tibia y peroné.")
    ]},

    {"id": "h4F", "codigo": "4F", "nombre": "Peroné", "segmentos": [
        seg("4F1", "Segmento proximal", "terminal", [
            T("A", "Simple", [], calificaciones=[
                {"letra": "n", "texto": "Extraarticular"}, {"letra": "o", "texto": "Intraarticular"}]),
            T("B", "Multifragmentaria", [], calificaciones=[
                {"letra": "n", "texto": "Extraarticular"}, {"letra": "o", "texto": "Intraarticular"}])
        ], nota="Solo se clasifica hasta tipo."),
        seg("4F2", "Diáfisis", "diafisario", [
            T("A", "Simple", [], calificaciones=Q_DIAF_AB),
            T("B", "En cuña o multifragmentaria", [], calificaciones=Q_DIAF_AB)
        ], nota="Solo se clasifica hasta tipo."),
        seg("4F3", "Segmento distal", "terminal", [
            T("A", "Simple", []), T("B", "En cuña o multifragmentaria", [])
        ], nota="Solo se clasifica hasta tipo.")
    ]},

    {"id": "h5", "codigo": "5", "nombre": "Columna", "segmentos": [
        {"id": "s-51", "codigo": "51", "nombre": "Cervical"},
        {"id": "s-52", "codigo": "52", "nombre": "Torácica"},
        {"id": "s-53", "codigo": "53", "nombre": "Lumbar"}],
     "nota": "Se clasifica con el sistema AO Spine. Fuera del alcance del libro."},

    {"id": "h6", "codigo": "6", "nombre": "Pelvis y acetábulo", "segmentos": [
        {"id": "s-61", "codigo": "61", "nombre": "Anillo pélvico", "clase": "terminal", "tipos": [
            T("A", "Estable", [G("1", "Avulsión"), G("2", "Ala ilíaca o rama aislada"), G("3", "Transversa de sacro o cóccix")]),
            T("B", "Parcialmente estable (inestabilidad rotacional)", [G("1", "Libro abierto unilateral"), G("2", "Compresión lateral unilateral"), G("3", "Bilateral")]),
            T("C", "Inestable (rotacional y vertical)", [G("1", "Unilateral"), G("2", "Bilateral, un lado B y otro C"), G("3", "Bilateral tipo C")])],
         "nota": "Transcrito de la lógica Tile; confirmar el detalle contra el compendio 2018."},
        {"id": "s-62", "codigo": "62", "nombre": "Acetábulo", "clase": "terminal", "tipos": [
            T("A", "Articular parcial, una columna o pared", [G("1", "Pared posterior"), G("2", "Columna posterior"), G("3", "Pared o columna anterior")]),
            T("B", "Articular parcial, transversa", [G("1", "Transversa"), G("2", "Transversa con pared posterior o en T"), G("3", "Anterior con hemitransversa posterior")]),
            T("C", "Articular completa, ambas columnas", [G("1", "Trazo alto en el ilíaco"), G("2", "Trazo bajo en el ilíaco"), G("3", "Con extensión a la sacroilíaca")])],
         "nota": "Transcrito de la lógica Letournel-Judet; confirmar el detalle contra el compendio 2018."}
    ]},

    {"id": "h7", "codigo": "7", "nombre": "Mano y carpo", "segmentos": [
        {"id": "s-71", "codigo": "71", "nombre": "Semilunar"},
        {"id": "s-72", "codigo": "72", "nombre": "Escafoides"},
        {"id": "s-73", "codigo": "73", "nombre": "Grande"},
        {"id": "s-74", "codigo": "74", "nombre": "Ganchoso"},
        {"id": "s-75", "codigo": "75", "nombre": "Trapecio"},
        {"id": "s-76", "codigo": "76", "nombre": "Otros carpianos"},
        {"id": "s-77", "codigo": "77", "nombre": "Metacarpianos"},
        {"id": "s-78", "codigo": "78", "nombre": "Falanges"}],
     "nota": "Códigos de segmento pendientes de confirmar contra el compendio 2018; el folleto de huesos largos no desarrolla la mano."},

    {"id": "h8", "codigo": "8", "nombre": "Pie", "segmentos": [
        {"id": "s-81", "codigo": "81", "nombre": "Astrágalo"},
        {"id": "s-82", "codigo": "82", "nombre": "Calcáneo"},
        {"id": "s-83", "codigo": "83", "nombre": "Escafoides tarsiano"},
        {"id": "s-84", "codigo": "84", "nombre": "Cuboides"},
        {"id": "s-85", "codigo": "85", "nombre": "Cuñas"},
        {"id": "s-87", "codigo": "87", "nombre": "Metatarsianos"},
        {"id": "s-88", "codigo": "88", "nombre": "Falanges"}],
     "nota": "Códigos de segmento pendientes de confirmar contra el compendio 2018; el folleto de huesos largos no desarrolla el pie."},

    {"id": "h9", "codigo": "9", "nombre": "Craneomaxilofacial", "segmentos": [], "nota": "Fuera del alcance del libro."}
]

MODIFICADORES = [
    {"n": "1", "texto": "No desplazada"},
    {"n": "2", "texto": "Desplazada"},
    {"n": "3", "texto": "Impactación", "sub": [
        {"n": "3a", "texto": "Articular"}, {"n": "3b", "texto": "Metafisaria"}]},
    {"n": "4", "texto": "Sin impactación"},
    {"n": "5", "texto": "Luxación", "sub": [
        {"n": "5a", "texto": "Anterior (volar, palmar, plantar)"},
        {"n": "5b", "texto": "Posterior (dorsal)"},
        {"n": "5c", "texto": "Medial (cubital)"},
        {"n": "5d", "texto": "Lateral (radial)"},
        {"n": "5e", "texto": "Inferior (en la cadera, también obturatriz)"},
        {"n": "5f", "texto": "Multidireccional"}]},
    {"n": "6", "texto": "Subluxación / inestabilidad ligamentosa", "sub": [
        {"n": "6a", "texto": "Anterior (volar, palmar, plantar)"},
        {"n": "6b", "texto": "Posterior (dorsal)"},
        {"n": "6c", "texto": "Medial (cubital)"},
        {"n": "6d", "texto": "Lateral (radial)"},
        {"n": "6e", "texto": "Inferior (en la cadera, también obturatriz)"},
        {"n": "6f", "texto": "Multidireccional"}]},
    {"n": "7", "texto": "Extensión diafisaria"},
    {"n": "8", "texto": "Lesión del cartílago articular (escala ICRS)", "sub": [
        {"n": "8a", "texto": "ICRS grado 0 — normal"},
        {"n": "8b", "texto": "ICRS grado 1 — indentación superficial y/o fisuras y grietas superficiales"},
        {"n": "8c", "texto": "ICRS grado 2 — lesiones anormales que llegan hasta el 50 % del espesor del cartílago"},
        {"n": "8d", "texto": "ICRS grado 3 — muy anormal, defectos de más del 50 % del espesor; hasta la capa calcificada; hasta el hueso subcondral sin atravesarlo; incluye ampollas"},
        {"n": "8e", "texto": "ICRS grado 4 — pérdida de cartílago que atraviesa el hueso subcondral"}]},
    {"n": "9", "texto": "Mala calidad ósea"},
    {"n": "10", "texto": "Reimplante"},
    {"n": "11", "texto": "Amputación asociada a la fractura"},
    {"n": "12", "texto": "Asociada a un implante no protésico"},
    {"n": "13", "texto": "Fractura de tipo espiroideo"},
    {"n": "14", "texto": "Fractura de tipo por flexión"}
]

DOC = {
    "version": "AO/OTA 2018 — transcrito del folleto oficial AOE-E1-018.10",
    "fuentes": [
        "AO Foundation. AO/OTA Fracture and Dislocation Classification — Introduction to the classification of long-bone fractures. Folleto oficial AOE-E1-018.10, © 2018. Aportado por el autor.",
        "AO Trauma Basic Principles Course. AO/OTA Fracture and Dislocation Classification 2018—Review (presentación oficial FINAL 2019). Aportada por el autor.",
        "Meinberg EG, Agel J, Roberts CS, Karam MD, Kellam JF. Fracture and Dislocation Classification Compendium — 2018. J Orthop Trauma. 2018;32(Suppl 1):S1–S170."
    ],
    "pendiente": "Subgrupos (.1/.2/.3) de cada grupo, y el desarrollo de escápula (14), clavícula (15), rótula (34), mano (7x) y pie (8x): solo están en el compendio completo, no en el folleto.",
    "estructura": {
        "orden": ["hueso", "segmento", "tipo", "grupo", "subgrupo", "calificaciones", "modificadoresUniversales"],
        "plantilla": "Hueso · Localización · Tipo · Grupo · Subgrupo · (Calificaciones) · [Modificadores universales]",
        "sinGuion": "El guion se eliminó en la revisión 2018 por riesgo de error en la introducción de datos: se escribe 32A3, no 32-A3.",
        "descripcion": {
            "hueso": "1.er dígito. En 2018 los huesos pareados se codifican por separado: radio 2R, cúbito 2U, peroné 4F.",
            "segmento": "2.º dígito. 1 proximal · 2 diafisario · 3 distal. Tibia y peroné añaden el 4 para los maléolos.",
            "tipo": "Letra A/B/C. Significado distinto en diáfisis y en segmento terminal.",
            "grupo": "Número tras la letra. Refina la morfología dentro del tipo.",
            "subgrupo": "Decimal .1/.2/.3. Máximo detalle; solo en el compendio completo."
        },
        "definicionSegmentoTerminal": "Los segmentos proximal y distal se definen por un cuadrado cuyos lados miden lo mismo que la parte más ancha de la epífisis. En los sistemas de dos huesos cada hueso se clasifica por separado, pero el segmento terminal se determina usando ambos huesos juntos. Excepciones: 31 y 44.",
        "excepciones": "No siguen la regla general de tipos: húmero proximal (11), fémur proximal (31) y maléolos (44).",
        "progresion": "La progresión de A a C denota complejidad morfológica creciente y mayor dificultad de manejo; lo mismo ocurre con la numeración de grupos y subgrupos.",
        "calificaciones": {
            "que": "Términos descriptivos de la morfología o la localización, específicos de cada fractura.",
            "notacion": "Letra minúscula entre paréntesis redondos, en la posición del asterisco. Opcionales y acumulables: (a, b).",
            "nota": "La mayoría se aplican a nivel de subtipo. Cada segmento tiene su propia lista; van anotadas en el propio segmento."
        },
        "modificadoresUniversales": {
            "que": "Términos descriptivos de morfología, desplazamiento, lesión asociada o localización, generalizables a casi todas las fracturas. Son opcionales.",
            "notacion": "Entre corchetes al final del código; varios separados por coma: [2, 5a, 8e, 9].",
            "lista": MODIFICADORES
        },
        "ejemplos": [
            {"codigo": "32A3(b)", "lectura": "Fémur, diafisaria, simple transversa (< 30°), tercio medio"},
            {"codigo": "2R2B2(b)", "lectura": "Radio, diafisaria, cuña intacta, tercio medio"},
            {"codigo": "2U2A2(b)", "lectura": "Cúbito, diafisaria, simple oblicua, tercio medio"},
            {"codigo": "2R3A2.2", "lectura": "Radio distal, extraarticular, metafisaria simple, desplazamiento dorsal"},
            {"codigo": "42B3(c)", "lectura": "Tibia, diafisaria, cuña fragmentaria, tercio distal"},
            {"codigo": "4F2A2(a)", "lectura": "Peroné, diafisaria, simple oblicua, tercio proximal"},
            {"codigo": "42C3(j)", "lectura": "Tibia, diafisaria, segmentaria fragmentaria, puramente diafisaria"},
            {"codigo": "33A3.2(f)", "lectura": "Fémur distal, en cuña o multifragmentaria, cuña fragmentada, lateral"},
            {"codigo": "11A1.2[2,5a,8e,9]", "lectura": "Húmero proximal con luxación: desplazada, luxación anterior, lesión cartilaginosa ICRS 4 y mala calidad ósea"},
            {"codigo": "42B3.2 IO4 MT2 NV1", "lectura": "Tibia diafisaria en cuña fragmentaria, con la clasificación AO de fractura abierta"}
        ]
    },
    "tiposPorSegmento": {
        "terminal": {
            "A": {"nombre": "Extraarticular", "definicion": "La fractura no afecta a la superficie articular."},
            "B": {"nombre": "Articular parcial", "definicion": "Afecta a una parte de la superficie articular; el resto permanece unido a la metáfisis y la diáfisis."},
            "C": {"nombre": "Articular completa", "definicion": "La superficie articular queda completamente separada de la diáfisis."}
        },
        "diafisario": {
            "A": {"nombre": "Simple", "definicion": "Fractura con un solo trazo circunferencial."},
            "B": {"nombre": "En cuña", "definicion": "Uno o más fragmentos intermedios; tras la reducción hay contacto cortical entre los fragmentos principales."},
            "C": {"nombre": "Multifragmentaria", "definicion": "Uno o más fragmentos intermedios; tras la reducción no hay contacto entre los fragmentos principales."},
            "notaGrupos2018": "Los grupos son A1 espiroidea, A2 oblicua (≥ 30°), A3 transversa (< 30°); B2 cuña intacta, B3 cuña fragmentaria; C2 segmentaria intacta, C3 segmentaria fragmentaria. Los antiguos B1 (cuña espiroidea) y C1 (compleja espiroidea) desaparecen."
        }
    },
    "fracturaAbierta": {
        "nota": "La OTA Open Fracture Classification se incorporó al compendio 2018: está validada y es más reproducible que las anteriores.",
        "aoOpenFractureClassification": {
            "notacion": "Se añade tras el código de fractura, por ejemplo 42B3.2 IO4 MT2 NV1.",
            "categorias": [
                {"sigla": "IO", "que": "Integument / open — estado de la cubierta cutánea"},
                {"sigla": "MT", "que": "Muscle and tendon — músculo y tendón"},
                {"sigla": "NV", "que": "Neurovascular — estado neurovascular"}],
            "pendiente": "Los valores numéricos de cada categoría están en el compendio."
        },
        "relacionGustilo": "Gustilo-Anderson se mantiene en paralelo: un mismo caso se etiqueta como IIIA y, a la vez, con la OTA-OFC y con el código AO de fractura abierta."
    },
    "huesos": HUESOS,
    "satelites": {
        "schatzker-kfuri": {
            "nombre": "Schatzker con la modificación de Kfuri-Luo",
            "aplicaA": ["s-41"],
            "justificacion": "Única clasificación satélite que el autor mantiene junto a la AO/OTA, por su valor para elegir abordaje y soporte.",
            "schatzker": [
                {"n": "I", "nombre": "Separación pura del platillo lateral", "nota": "Hueso joven y denso; sin hundimiento."},
                {"n": "II", "nombre": "Separación con hundimiento del platillo lateral", "nota": "El patrón más frecuente."},
                {"n": "III", "nombre": "Hundimiento puro del platillo lateral", "nota": "Cortical lateral íntegra; hueso osteoporótico."},
                {"n": "IV", "nombre": "Platillo medial", "nota": "Alta energía; descartar lesión vascular y luxación de rodilla."},
                {"n": "V", "nombre": "Bicondílea", "nota": "Ambos platillos; continuidad metafisodiafisaria conservada."},
                {"n": "VI", "nombre": "Bicondílea con disociación metafisodiafisaria", "nota": "La más grave; partes blandas comprometidas."}],
            "kfuriLuo": {
                "concepto": "Reformula la meseta en tres columnas —lateral, medial y posterior— evaluadas en TC axial, en lugar de la visión bipolar de la radiografía.",
                "aporte": "Identifica el fragmento posterior, invisible en la radiografía simple, que Schatzker no captura y que cambia el abordaje.",
                "columnas": [
                    {"id": "lateral", "nombre": "Columna lateral"},
                    {"id": "medial", "nombre": "Columna medial"},
                    {"id": "posterior", "nombre": "Columna posterior", "nota": "La aportación clave: su afectación exige abordaje posterior."}],
                "regla": "Nombrar las columnas afectadas y planear un abordaje por cada una que requiera soporte directo."
            }
        }
    }
}

SALIDA.write_text(json.dumps(DOC, ensure_ascii=False, indent=2), encoding="utf-8")

n_seg = sum(len(h.get("segmentos", [])) for h in HUESOS)
n_tipo = sum(len(s.get("tipos", [])) for h in HUESOS for s in h.get("segmentos", []))
n_gr = sum(len(t.get("grupos", [])) for h in HUESOS for s in h.get("segmentos", []) for t in s.get("tipos", []))
n_mod = len(MODIFICADORES) + sum(len(m.get("sub", [])) for m in MODIFICADORES)
print(f"Escrito: {SALIDA}")
print(f"  {len(HUESOS)} huesos · {n_seg} segmentos · {n_tipo} tipos · {n_gr} grupos")
print(f"  {n_mod} modificadores universales (con subniveles)")
