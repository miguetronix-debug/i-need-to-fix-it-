#!/usr/bin/env python3
"""
patch_paso3.py — Reescribe la dosificación de la estabilidad relativa.

Sustituye la decisión «palancas» por las palancas reales de ingeniería del
montaje, con las cifras publicadas, y añade la decisión «brecha», que es el
denominador de la fórmula de Perren y la que explica la trampa clásica del
puenteo sobre trazo simple.

Uso:  python3 tools/patch_paso3.py
"""

import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
F = RAIZ / "content" / "pasos" / "03-estabilidad.json"
P = json.loads(F.read_text(encoding="utf-8"))

VISIBLE_SI_RELATIVA = [
    {"estabilidad": ["e-relativa"]},
    {"estab-metafisis": ["em-relativa"]},
    {"estab-articular": ["ea-relativa"]},
]

# ------------------------------------------------------------------ brecha
BRECHA = {
    "id": "brecha",
    "pregunta": "¿Qué va a quedar en el foco cuando termines de reducir?",
    "ayuda": "La deformación es movimiento dividido entre brecha. Con el mismo movimiento, una brecha estrecha da una deformación enorme y una brecha amplia la reparte. El denominador importa tanto como el numerador, y es lo que más se olvida.",
    "tipo": "opcionUnica",
    "mostrarSiAlguno": VISIBLE_SI_RELATIVA,
    "opciones": [
        {"id": "br-amplia", "etiqueta": "Brecha amplia repartida entre varios fragmentos", "criterios": [
            "La conminución reparte el movimiento total entre muchas interfases",
            "Cada una soporta solo una fracción de la deformación",
            "Es el escenario para el que el puenteo fue diseñado"]},
        {"id": "br-estrecha", "etiqueta": "Brecha estrecha: trazo simple casi reducido", "criterios": [
            "Es la trampa clásica: poca brecha con algo de movimiento da una deformación altísima",
            "Una sola interfase se lleva todo el movimiento del montaje",
            "Aquí no hay término medio: o comprimes, o alargas mucho la longitud de trabajo"]},
        {"id": "br-contacto", "etiqueta": "Contacto cortical restaurado", "criterios": [
            "El hueso comparte carga con el implante y lo protege de la fatiga",
            "Permite dinamizar y tolera mejor el apoyo precoz",
            "Es lo que convierte un montaje de carga soportada en uno de carga compartida"]},
    ],
}

# ------------------------------------------------------------------ palancas
PALANCAS = {
    "id": "palancas",
    "pregunta": "¿Cómo vas a dosificar la estabilidad relativa?",
    "ayuda": "No es «poca fijación»: es una cantidad de movimiento calculada. Estas son las palancas reales del montaje, y casi todas se deciden en la mesa, no en el catálogo.",
    "tipo": "opcionMultiple",
    "mostrarSiAlguno": VISIBLE_SI_RELATIVA,
    "opciones": [
        {"id": "p-longitud", "etiqueta": "Placa · Ampliar la longitud de trabajo", "criterios": [
            "Es la distancia entre los tornillos más internos a cada lado del foco: el tramo de placa que de verdad trabaja",
            "Es la palanca que más manda: gobierna la rigidez axial y la torsional por encima de cualquier otro factor",
            "Omitir el tornillo inmediato al foco a cada lado deja el montaje casi el DOBLE de flexible, en compresión y en torsión",
            "En la práctica: dejar dos o tres agujeros vacíos a cada lado del foco"]},
        {"id": "p-span", "etiqueta": "Placa · Subir la relación de cobertura (plate span ratio)", "criterios": [
            "Longitud de la placa dividida entre la longitud de la fractura",
            "Por encima de 2 o 3 en las conminutas; por encima de 8 o 10 si el trazo es simple",
            "Una placa larga reparte la carga y baja la que soporta cada tornillo"]},
        {"id": "p-densidad", "etiqueta": "Placa · Bajar la densidad de tornillos (plate screw density)", "criterios": [
            "Tornillos colocados dividido entre agujeros que tiene la placa",
            "Por debajo de 0,5 en conminutas; por debajo de 0,3 o 0,4 si el trazo es simple",
            "Llenar todos los agujeros no da más estabilidad: da más rigidez, menos callo y ningún margen"]},
        {"id": "p-tornillos", "etiqueta": "Placa · Tres tornillos por fragmento, bien repartidos", "criterios": [
            "A partir de tres por fragmento la rigidez axial ya no sube; a partir de cuatro tampoco sube la torsional",
            "Repartirlos a lo largo del fragmento en lugar de agruparlos junto al foco",
            "El cuarto y el quinto tornillo no compran estabilidad: gastan hueso y agujeros"]},
        {"id": "p-bloqueada", "etiqueta": "Placa · Bloqueada (ángulo fijo)", "criterios": [
            "Fijador interno: no comprime la placa contra el hueso y preserva la vascularización perióstica",
            "Sostiene hueso osteoporótico y metáfisis conminuta",
            "Pero suprime el movimiento en la cortical próxima: sin longitud de trabajo suficiente, es demasiado rígida"]},
        {"id": "p-separacion", "etiqueta": "Placa · Separarla del hueso 2 a 5 mm", "criterios": [
            "Solo con placa bloqueada, que no necesita apoyarse para estabilizar",
            "Reduce la rigidez del montaje y respeta el periostio",
            "Pasarse alarga el brazo de palanca sobre los tornillos y adelanta el fallo del material"]},
        {"id": "p-fcl", "etiqueta": "Placa · Tornillos de bloqueo dinámico o far cortical locking", "criterios": [
            "Solo agarran la cortical lejana; el vástago flexa dentro del canal medular",
            "Devuelven movimiento a la cortical próxima y con ello un callo simétrico",
            "Es la respuesta directa al callo asimétrico de la placa bloqueada convencional"]},
        {"id": "p-material", "etiqueta": "Placa · Titanio en lugar de acero", "criterios": [
            "Menor módulo elástico: el montaje trabaja algo más elástico",
            "Es un ajuste fino; no sustituye a la longitud de trabajo"]},
        {"id": "p-clavo-trabajo", "etiqueta": "Clavo · Longitud de trabajo del clavo", "criterios": [
            "Con contacto cortical, es la distancia entre las zonas donde el clavo apoya en el endostio",
            "Sin contacto cortical, es toda la distancia entre los pernos de bloqueo más internos",
            "Por eso una conminuta enclavada es siempre mucho menos rígida de lo que parece"]},
        {"id": "p-clavo", "etiqueta": "Clavo · Diámetro y fresado", "criterios": [
            "La rigidez a flexión crece con la cuarta potencia del radio",
            "Sube MUCHO la rigidez: es la palanca para pedir MENOS movimiento, no más",
            "Un clavo más grueso además ajusta mejor y acorta la longitud de trabajo efectiva"]},
        {"id": "p-clavo-bloqueo", "etiqueta": "Clavo · Número y posición de los pernos", "criterios": [
            "Estático en ambos extremos: controla longitud y rotación, que el clavo no garantiza solo",
            "Pernos más alejados del foco alargan la longitud de trabajo y flexibilizan",
            "Dinamizar permite compresión axial con la carga, pero exige contacto cortical"]},
        {"id": "p-tutor", "etiqueta": "Fijador externo · Mecánica del montaje", "criterios": [
            "Diámetro del pin: también a la cuarta potencia. Pasar de 5 a 6 mm cambia más que añadir un pin",
            "Más pines, más separados entre sí y más próximos al foco: más rígido",
            "Barra cerca del hueso: más rígido. Barra alejada: más elástico",
            "Segundo plano o segunda barra: más rígido"]},
    ],
}

# ------------------------------------------------------------------ aplicar
decs = P["decisiones"]
idx = next(i for i, d in enumerate(decs) if d["id"] == "palancas")
decs[idx] = PALANCAS
decs.insert(idx, BRECHA)

TODAS_PALANCAS = [o["id"] for o in PALANCAS["opciones"]]

# la alerta de «no has dosificado» debe mirar todas las palancas nuevas
for a in P["alertas"]:
    if a["id"] == "relativa-sin-dosificar":
        a["noSi"] = {"palancas": TODAS_PALANCAS}
        a["mostrarSiAlguno"] = VISIBLE_SI_RELATIVA
        a.pop("mostrarSi", None)
        a["texto"] = ("Elegiste estabilidad relativa pero aún no has definido cómo la dosificas. "
                      "La longitud de trabajo, la densidad de tornillos y la relación de cobertura "
                      "no son detalles de montaje: son la dosis. Sin decidirlas, la cantidad de "
                      "movimiento queda al azar.")

NUEVAS_ALERTAS = [
    {"id": "brecha-estrecha-strain", "severidad": "critica",
     "titulo": "Brecha estrecha con estabilidad relativa: es la receta de la no unión",
     "texto": "La deformación es movimiento dividido entre brecha. Con una sola interfase estrecha, "
              "cualquier micromovimiento produce una deformación que el callo no tolera, el foco "
              "reabsorbe y la placa termina fallando por fatiga. Es la trampa del trazo simple "
              "puenteado. Solo hay dos salidas coherentes: comprimir de verdad, o alargar mucho la "
              "longitud de trabajo para repartir ese movimiento en un tramo largo.",
     "mostrarSi": {"brecha": ["br-estrecha"]}},
    {"id": "brecha-estrecha-sin-trabajo", "severidad": "critica",
     "titulo": "Trazo simple puenteado y sin longitud de trabajo",
     "texto": "Has aceptado una brecha estrecha y no has alargado la longitud de trabajo. Este es "
              "exactamente el montaje que no consolida por ninguna de las dos vías: no comprime lo "
              "suficiente para curación directa, y deforma demasiado para curar por callo.",
     "mostrarSi": {"brecha": ["br-estrecha"]},
     "noSiAlguno": [{"palancas": ["p-longitud"]}, {"palancas": ["p-span"]}, {"palancas": ["p-clavo-trabajo"]}]},
    {"id": "trabajo-sin-contacto", "severidad": "alta",
     "titulo": "Longitud de trabajo larga sin contacto cortical: vigila la fatiga",
     "texto": "Alargar la longitud de trabajo flexibiliza el montaje, pero también reduce la carga "
              "que la placa aguanta antes de deformarse. Si además no hay contacto óseo que comparta "
              "carga, el implante falla antes en carga cíclica. Compénsalo con una placa más larga, "
              "restringiendo el apoyo, o restaurando algo de contacto.",
     "mostrarSi": {"palancas": ["p-longitud"]},
     "noSi": {"brecha": ["br-contacto"]}},
    {"id": "callo-asimetrico", "severidad": "alta",
     "titulo": "La placa bloqueada produce un callo asimétrico",
     "texto": "El montaje bloqueado convencional cierra la brecha de forma asimétrica: casi todo el "
              "movimiento ocurre en la cortical lejana y casi ninguno bajo la placa. El callo sigue "
              "esa asimetría y aparece escaso e irregular en la cortical próxima. Se corrige con "
              "tornillos de bloqueo dinámico o far cortical locking, separando la placa del hueso, "
              "o alargando la longitud de trabajo.",
     "mostrarSi": {"palancas": ["p-bloqueada"]},
     "noSiAlguno": [{"palancas": ["p-fcl"]}, {"palancas": ["p-separacion"]}, {"palancas": ["p-longitud"]}]},
    {"id": "densidad-alta", "severidad": "media",
     "titulo": "Llenar todos los agujeros no es más seguro",
     "texto": "Has planificado la longitud de trabajo pero no la densidad de tornillos. Con tres por "
              "fragmento la rigidez axial ya no sube, y con cuatro tampoco la torsional. Los que "
              "sobran solo añaden rigidez, gastan hueso y quitan opciones a una eventual revisión.",
     "mostrarSi": {"palancas": ["p-longitud"]},
     "noSiAlguno": [{"palancas": ["p-densidad"]}, {"palancas": ["p-tornillos"]}]},
    {"id": "contacto-dinamizar", "severidad": "info",
     "titulo": "Con contacto cortical el hueso trabaja contigo",
     "texto": "Restaurado el contacto, el hueso comparte carga y protege al implante de la fatiga. "
              "Es la situación que permite dinamizar y autorizar apoyo precoz con más margen.",
     "mostrarSi": {"brecha": ["br-contacto"]}},
]
ids_previas = {a["id"] for a in P["alertas"]}
P["alertas"] += [a for a in NUEVAS_ALERTAS if a["id"] not in ids_previas]

# ------------------------------------------------------------------ derivado
DOSIS = {
    "id": "dosis", "titulo": "La dosis que estás prescribiendo", "tipo": "reglas", "modo": "todas",
    "reglas": [
        {"si": {"palancas": ["p-longitud"]},
         "texto": "Longitud de trabajo ampliada. Es la palanca dominante: omitir el tornillo inmediato al foco a cada lado deja el montaje casi el doble de flexible, en compresión y en torsión. En la práctica, dos o tres agujeros vacíos a cada lado."},
        {"si": {"palancas": ["p-span"]},
         "texto": "Relación de cobertura = longitud de la placa / longitud de la fractura. Objetivo: por encima de 2-3 en conminutas y de 8-10 en trazos simples."},
        {"si": {"palancas": ["p-densidad"]},
         "texto": "Densidad de tornillos = tornillos colocados / agujeros de la placa. Objetivo: por debajo de 0,5 en conminutas y de 0,3-0,4 en trazos simples."},
        {"si": {"palancas": ["p-tornillos"]},
         "texto": "Tres tornillos por fragmento principal, repartidos a lo largo del fragmento. Más de tres no sube la rigidez axial y más de cuatro no sube la torsional."},
        {"si": {"palancas": ["p-fcl"]},
         "texto": "Bloqueo dinámico o far cortical locking: el vástago flexa en el canal y devuelve movimiento a la cortical próxima, con lo que el callo se forma simétrico en las dos corticales."},
        {"si": {"palancas": ["p-clavo-trabajo"]},
         "texto": "Longitud de trabajo del clavo: con contacto cortical es la distancia entre las zonas de apoyo endostal; sin contacto, toda la distancia entre los pernos más internos."},
        {"si": {"palancas": ["p-tutor"]},
         "texto": "Mecánica del pin: diámetro a la cuarta potencia, número de pines, separación entre ellos, distancia barra-hueso y número de planos. Subir el diámetro del pin cambia más que añadir un pin."},
        {"si": {"brecha": ["br-estrecha"]},
         "texto": "Brecha estrecha: el denominador de la fórmula es pequeño, así que cualquier movimiento se traduce en una deformación enorme. Este escenario exige decidir, no transigir."},
        {"si": {"brecha": ["br-amplia"]},
         "texto": "Brecha amplia: el movimiento se reparte entre varias interfases y cada una soporta una fracción. Es donde el puenteo funciona como está descrito."},
    ],
}
if not any(d["id"] == "dosis" for d in P["derivados"]):
    P["derivados"].append(DOSIS)

# ------------------------------------------------------------------ esencial
for b in P["esencial"]:
    if b.get("titulo") == "Los determinantes de la rigidez":
        b["titulo"] = "Las palancas del montaje, con sus cifras"
        b["encabezados"] = ["Palanca", "Qué es", "Objetivo o efecto"]
        b["filas"] = [
            ["Longitud de trabajo", "Distancia entre los tornillos más internos a cada lado del foco; en el clavo, entre las zonas de apoyo endostal o entre los pernos más internos.",
             "Es la palanca dominante. Omitir el tornillo inmediato al foco a cada lado deja el montaje casi el doble de flexible en compresión y en torsión."],
            ["Relación de cobertura", "Longitud de la placa / longitud de la fractura.",
             "Por encima de 2-3 en conminutas; por encima de 8-10 en trazos simples."],
            ["Densidad de tornillos", "Tornillos colocados / agujeros de la placa.",
             "Por debajo de 0,5 en conminutas; por debajo de 0,3-0,4 en trazos simples."],
            ["Tornillos por fragmento", "Cuántos y cómo repartidos en cada fragmento principal.",
             "Tres bastan: a partir de ahí no sube la rigidez axial, y a partir de cuatro tampoco la torsional."],
            ["Bloqueada o no bloqueada", "Ángulo fijo frente a fricción placa-hueso.",
             "La bloqueada preserva vascularización y sostiene hueso débil, pero suprime el movimiento en la cortical próxima."],
            ["Distancia placa-hueso", "Elevación de la placa bloqueada sobre la cortical.",
             "2 a 5 mm reducen rigidez y respetan el periostio; pasarse aumenta el brazo de palanca sobre los tornillos."],
            ["Far cortical locking / bloqueo dinámico", "Tornillos que solo agarran la cortical lejana y flexan en el canal.",
             "Devuelven movimiento a la cortical próxima y con ello un callo simétrico."],
            ["Diámetro del clavo y fresado", "Radio del implante intramedular.",
             "La rigidez a flexión crece con la cuarta potencia del radio: sube mucho la estabilidad, no la baja."],
            ["Mecánica del pin del fijador", "Diámetro, número, separación, distancia barra-hueso, planos.",
             "El diámetro también manda a la cuarta potencia: de 5 a 6 mm cambia más que añadir un pin."],
            ["Material", "Acero frente a titanio.",
             "El titanio tiene menor módulo elástico y trabaja algo más elástico. Ajuste fino, no sustituto de la longitud de trabajo."],
        ]

NUEVOS_BLOQUES = [
    {"tipo": "recuadro", "variante": "regla", "titulo": "La brecha es el denominador, y es lo que más se olvida",
     "texto": "La deformación es movimiento dividido entre brecha. Casi todo el mundo trabaja el numerador —cuánto se mueve el montaje— y se olvida del denominador. Una brecha amplia repartida entre varios fragmentos convierte un movimiento considerable en una deformación pequeña en cada interfase; una brecha estrecha convierte un movimiento mínimo en una deformación enorme. Por eso una conminuta puenteada consolida y un trazo transverso casi reducido y puenteado no consolida, aunque el implante sea el mismo y el movimiento parecido."},
    {"tipo": "recuadro", "variante": "error", "titulo": "La trampa del trazo simple puenteado",
     "texto": "Es el error de montaje más frecuente y el más caro. Se reduce casi anatómicamente un trazo transverso u oblicuo corto, se coloca una placa larga y se llenan los agujeros próximos al foco. El resultado es una brecha mínima con una longitud de trabajo mínima: la deformación en esa única interfase es altísima, el foco reabsorbe, el callo no aparece y la placa acaba rompiéndose por fatiga en un agujero vacío. Frente a este escenario solo hay dos respuestas coherentes: comprimir de verdad, o alargar mucho la longitud de trabajo para repartir el movimiento."},
    {"tipo": "recuadro", "variante": "idea", "titulo": "El callo asimétrico de la placa bloqueada",
     "texto": "El montaje bloqueado convencional no cierra la brecha de forma uniforme: la cortical lejana se mueve y la que está bajo la placa apenas. El callo sigue esa asimetría y aparece escaso e irregular precisamente donde está el implante. Las tres respuestas descritas son alargar la longitud de trabajo, separar la placa del hueso unos milímetros, y usar tornillos de bloqueo dinámico o far cortical locking, que solo agarran la cortical lejana y flexan dentro del canal para devolver movimiento a la próxima."},
    {"tipo": "recuadro", "variante": "regla", "titulo": "Rigidez y resistencia tiran en sentidos contrarios",
     "texto": "Alargar la longitud de trabajo flexibiliza el montaje, que es lo que se busca, pero al mismo tiempo baja la carga que la placa soporta antes de deformarse de forma permanente. Si además no hay contacto cortical que comparta carga, ese montaje flexible falla antes en carga cíclica. La dosificación de la estabilidad relativa siempre es un equilibrio entre las dos cosas, y se compensa con una placa más larga, con el régimen de apoyo, o restaurando algo de contacto."},
]
titulos = {b.get("titulo") for b in P["esencial"]}
P["esencial"] += [b for b in NUEVOS_BLOQUES if b["titulo"] not in titulos]

# ------------------------------------------------------------------ evidencia y refs
NUEVA_EV = [
    {"nivel": "5", "afirmacion": "La longitud de trabajo es el factor que más determina la rigidez axial y torsional de una placa bloqueada; omitir el tornillo inmediato al foco a cada lado deja el montaje casi el doble de flexible. Más de tres tornillos por fragmento no aumenta la rigidez axial, y más de cuatro no aumenta la torsional.", "refs": ["ref-stoffel-2003"]},
    {"nivel": "5", "afirmacion": "Como guía empírica, la relación de cobertura debe superar 2-3 en fracturas conminutas y 8-10 en trazos simples, y la densidad de tornillos mantenerse por debajo de 0,5 en conminutas y de 0,3-0,4 en trazos simples.", "refs": ["ref-gautier-2003"]},
    {"nivel": "3", "afirmacion": "El enclavijado bloqueado convencional produce cierre asimétrico de la brecha y, con él, un callo asimétrico e inconsistente que disminuye desde la cortical lejana hacia la próxima.", "refs": ["ref-lujan-2010"]},
    {"nivel": "5", "afirmacion": "Los tornillos de far cortical locking inducen movimiento interfragmentario simétrico por flexión en voladizo del vástago, y en modelo animal se asociaron a mayor volumen de callo y mayor contenido mineral que la placa bloqueada convencional.", "refs": ["ref-bottlang-2011"]},
]
P.setdefault("evidencia", [])
afirmaciones = {e["afirmacion"] for e in P["evidencia"]}
P["evidencia"] += [e for e in NUEVA_EV if e["afirmacion"] not in afirmaciones]

for r in ("ref-stoffel-2003", "ref-gautier-2003", "ref-lujan-2010", "ref-bottlang-2011"):
    if r not in P["refs"]:
        P["refs"].append(r)

F.write_text(json.dumps(P, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Paso 3 actualizado: {len(P['decisiones'])} decisiones, "
      f"{sum(len(d['opciones']) for d in P['decisiones'])} opciones, "
      f"{len(P['alertas'])} alertas, {len(P['derivados'])} derivados.")
