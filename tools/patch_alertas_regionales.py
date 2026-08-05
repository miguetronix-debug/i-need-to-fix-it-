#!/usr/bin/env python3
"""
patch_alertas_regionales.py — Conecta las clasificaciones regionales del Paso 2
con el razonamiento de los pasos siguientes.

Sin esto, las clasificaciones serían una tabla de consulta. Con esto, elegir
Pauwels III cambia lo que el app dice en el Paso 5, y elegir Vancouver B2
cambia lo que dice en el Paso 6.

Es idempotente: las alertas llevan el prefijo «rg-».

Uso:  python3 tools/patch_alertas_regionales.py
"""

import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PASOS = RAIZ / "content" / "pasos"

ALERTAS = {
    "01-evaluacion.json": [
        {"id": "rg-astragalo-urgente", "severidad": "critica",
         "titulo": "Luxación del astrágalo: la reducción no espera",
         "texto": "Un Hawkins III o IV mantiene el cuerpo del astrágalo extruido, tensando la piel desde dentro y con el aporte vascular interrumpido. La reducción urgente es lo único que puede salvar esa piel y algo de vascularización, aunque la osteosíntesis definitiva se difiera.",
         "mostrarSi": {"ctx": ["urgencia-reduccion"]}},
        {"id": "rg-pelvis-sangrado", "severidad": "critica",
         "titulo": "Este patrón de pelvis es el que sangra",
         "texto": "La apertura en libro y el cizallamiento vertical aumentan el volumen pélvico y rompen el plexo venoso presacro. Faja pélvica o fijador externo de entrada, protocolo de transfusión masiva y decisión precoz sobre empaquetamiento o angioembolización. La osteosíntesis definitiva viene después.",
         "mostrarSi": {"ctx": ["pelvis-hemorragia"]}},
    ],
    "03-estabilidad.json": [
        {"id": "rg-sin-contacto", "severidad": "alta",
         "titulo": "Sin columna cortical que comparta carga",
         "texto": "Un Winquist III o IV significa que no queda contacto cortical: el implante soporta toda la carga y la longitud de trabajo es toda la distancia entre los pernos. Bloqueo estático obligado, y el régimen de apoyo hay que definirlo, no suponerlo.",
         "mostrarSi": {"ctx": ["sin-contacto-cortical"]}},
    ],
    "05-principios.json": [
        {"id": "rg-pauwels", "severidad": "alta",
         "titulo": "Trazo vertical del cuello: eso es cizallamiento, no compresión",
         "texto": "Con un Pauwels III la carga no comprime el foco: lo cizalla. Tres tornillos paralelos trabajan entonces a cizallamiento y ceden en varo. Lo que corresponde es ángulo fijo —tornillo deslizante con placa, o clavo cefalomedular—, o añadir un tornillo antirrotatorio con una placa de sostén que haga de contrafuerte.",
         "mostrarSi": {"ctx": ["pauwels-vertical"]}},
        {"id": "rg-sa-medial", "severidad": "alta",
         "titulo": "Maléolo medial vertical: tornillos a fricción no lo sujetan",
         "texto": "En la supinación-aducción el trazo medial es vertical, así que los tornillos horizontales trabajan a cizallamiento. Ese fragmento pide una placa de contrafuerte antideslizante.",
         "mostrarSi": {"ctx": ["lh-aduccion"]}},
    ],
    "06-implante.json": [
        {"id": "rg-vancouver-b2", "severidad": "critica",
         "titulo": "Vástago suelto: la operación es revisarlo, no fijar la fractura",
         "texto": "En un Vancouver B2 o B3 el problema no es la fractura, es que la prótesis ha perdido su fijación. Colocar una placa sobre un vástago suelto falla siempre, porque el vástago sigue moviéndose dentro del hueso. Hay que revisar con vástago largo que puentee el foco, y en el B3 además reconstruir el hueso.",
         "mostrarSi": {"ctx": ["revisar-vastago"]},
         "noSi": {"ctx": ["vastago-revision"]}},
        {"id": "rg-garden-desplazada", "severidad": "alta",
         "titulo": "Cuello desplazado: valora si la respuesta es una prótesis",
         "texto": "Un Garden III-IV rompe el aporte cefálico y acumula tasas altas de necrosis y no unión. En el paciente mayor o con demandas bajas, la artroplastia evita la reintervención; la fijación se reserva al paciente joven, y entonces es urgente y anatómica.",
         "mostrarSi": {"ctx": ["garden-desplazada"]}},
        {"id": "rg-necrosis-humeral", "severidad": "alta",
         "titulo": "Predictores de isquemia de la cabeza humeral",
         "texto": "Calcar corto por debajo de 8 mm, bisagra medial rota o trazo basicervical: la cabeza probablemente está isquémica. Con varios presentes, en el paciente mayor la artroplastia invertida evita una fijación que va a colapsar.",
         "mostrarSi": {"ctx": ["riesgo-necrosis-humeral"]}},
        {"id": "rg-sanders-iv", "severidad": "media",
         "titulo": "Faceta posterior conminuta: valora la artrodesis primaria",
         "texto": "En un Sanders IV la superficie no es reconstruible y el resultado funcional de la osteosíntesis aislada es pobre. La artrodesis subastragalina primaria, con restauración de altura y anchura, es una alternativa legítima que hay que plantear antes de operar, no después.",
         "mostrarSi": {"ctx": ["valorar-artrodesis"]}},
        {"id": "rg-pelvis-posterior", "severidad": "alta",
         "titulo": "Inestabilidad vertical: la fijación anterior no basta",
         "texto": "Un Tile C significa que el complejo posterior está roto. La sínfisis o el fijador anterior no controlan el desplazamiento craneal: hace falta fijación posterior, con tornillos iliosacros o placa transilíaca.",
         "mostrarSi": {"ctx": ["pelvis-fijacion-posterior"]}},
        {"id": "rg-sindesmosis-comprimida", "severidad": "critica",
         "titulo": "La sindesmosis no se comprime: se posiciona",
         "texto": "Has elegido compresión interfragmentaria con la sindesmosis lesionada. Ese espacio no es un foco de fractura que haya que cerrar: es una articulación con movimiento fisiológico. Comprimirla estrecha la mortaja, bloquea la dorsiflexión y deja el tobillo rígido y doloroso. Lo que corresponde es un tornillo de POSICIÓN, colocado sin comprimir y con el tobillo en neutro.",
         "mostrarSiAlguno": [{"ctxTodos": ["riesgo-sindesmosis", "usa-compresion"]},
                             {"ctx": ["riesgo-sindesmosis"], "tipo-tornillo": ["tor-parcial"]}]},
        {"id": "rg-sindesmosis", "severidad": "alta",
         "titulo": "Peroné alto: comprueba la sindesmosis",
         "texto": "En la pronación-rotación externa el trazo del peroné sube, y cuanto más sube más membrana interósea está rota. Palpa todo el peroné para descartar una Maisonneuve y haz la prueba de estrés intraoperatoria. Si hay que estabilizarla, es un tornillo de posición: comprimir la sindesmosis es el error.",
         "mostrarSi": {"ctx": ["riesgo-sindesmosis"]}},
        {"id": "rg-codo-inestable", "severidad": "alta",
         "titulo": "La cabeza radial aquí es un estabilizador primario",
         "texto": "Con luxación del codo asociada, resecar la cabeza radial sin sustituirla deja el codo inestable. Busca la tríada terrible —coronoides y ligamento colateral lateral— y planifica el orden de reparación desde dentro hacia fuera.",
         "mostrarSi": {"ctx": ["inestabilidad-codo"]}},
        {"id": "rg-winquist-dinamizar", "severidad": "alta",
         "titulo": "No dinamices lo que no tiene contacto cortical",
         "texto": "Con un Winquist III o IV no queda columna que comparta carga: la dinamización solo produce acortamiento. Bloqueo estático en ambos extremos.",
         "mostrarSi": {"ctx": ["sin-contacto-cortical"], "clavo-config": ["cl-dinamico"]}},
    ],
    "07-posicion.json": [
        {"id": "rg-acetabulo-supino-posterior", "severidad": "critica",
         "titulo": "Un patrón posterior no se alcanza en supino",
         "texto": "La pared y la columna posteriores se abordan por Kocher-Langenbeck, y eso exige prono o lateral. En supino no hay forma de llegar, y descubrirlo con el campo montado obliga a desmontar, volver a preparar y volver a pintar. Si el patrón afecta además a la columna anterior, la salida es una posición flotante o dos tiempos.",
         "mostrarSi": {"ctx": ["acet-posterior"], "posicion": ["pos-supino"]}},
        {"id": "rg-acetabulo-posicion", "severidad": "alta",
         "titulo": "El patrón acetabular decide la posición, no al revés",
         "texto": "Los patrones posteriores se abordan en prono o lateral por Kocher-Langenbeck; los anteriores, en supino por ilioinguinal o anterior intrapélvico. Si el patrón afecta a las dos columnas, decide antes si vas a necesitar una posición flotante o dos tiempos.",
         "mostrarSiAlguno": [{"ctx": ["acet-posterior"]}, {"ctx": ["acet-anterior"]}, {"ctx": ["acet-ambas"]}]},
        {"id": "rg-columna-posterior-pos", "severidad": "media",
         "titulo": "Fragmento posteromedial: la posición tiene que permitir llegar por detrás",
         "texto": "Con una columna posteromedial afectada, el supino puro no da acceso. Valora decúbito flotante, prono, o una posición que permita flexionar la rodilla y rotar la cadera para abrir el intervalo posteromedial.",
         "mostrarSi": {"ctx": ["col-posterior"]}},
    ],
    "08-abordaje.json": [
        {"id": "rg-placa-lateral-insuficiente", "severidad": "critica",
         "titulo": "La placa lateral no controla el fragmento medial",
         "texto": "Un Schatzker IV o una columna medial o posteromedial afectada necesitan su propio contrafuerte por su propio abordaje. Sujetarlos con tornillos largos desde una placa lateral es el mecanismo por el que estas fracturas colapsan en varo a las pocas semanas.",
         "mostrarSiAlguno": [{"ctx": ["sch-medial"]}, {"ctx": ["col-medial"]}, {"ctx": ["col-posterior"]}]},
        {"id": "rg-acetabulo-abordaje", "severidad": "alta",
         "titulo": "En el acetábulo el abordaje es la operación",
         "texto": "El patrón de Letournel no describe: prescribe. Elegir la vía equivocada no se corrige ampliando la incisión, y el abordaje combinado o extensible tiene un coste de partes blandas que hay que aceptar antes de empezar.",
         "mostrarSiAlguno": [{"ctx": ["acet-posterior"]}, {"ctx": ["acet-anterior"]}, {"ctx": ["acet-ambas"]}]},
    ],
    "09-tecnicas.json": [
        {"id": "rg-lauge-maniobra", "severidad": "info",
         "titulo": "El mecanismo se deshace al revés",
         "texto": "Lauge-Hansen sirve justo para esto: la maniobra de reducción es la inversa de la que produjo la lesión. En la rotación externa se reduce rotando internamente; en la aducción, abduciendo. Aplicarlo ahorra intentos y ahorra manipulación sobre el foco.",
         "mostrarSiAlguno": [{"ctx": ["lh-rotacion"]}, {"ctx": ["lh-aduccion"]}, {"ctx": ["lh-abduccion"]}]},
        {"id": "rg-hundimiento-meseta", "severidad": "alta",
         "titulo": "Hundimiento de meseta: la ligamentotaxis no lo levanta",
         "texto": "En un Schatzker II o III hay un fragmento deprimido sin inserción ligamentosa que lo arrastre. Hay que elevarlo por ventana metafisaria y rellenar el defecto, o vuelve a hundirse en cuanto se carga.",
         "mostrarSi": {"ctx": ["sch-hundido"]},
         "noSi": {"hundido": ["hu-si"]}},
    ],
}


def main():
    total = 0
    for archivo, nuevas in ALERTAS.items():
        f = PASOS / archivo
        P = json.loads(f.read_text(encoding="utf-8"))
        P["alertas"] = [a for a in P["alertas"] if not a["id"].startswith("rg-")]
        P["alertas"] += nuevas
        f.write_text(json.dumps(P, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        total += len(nuevas)
        print(f"   {archivo:22s} +{len(nuevas)} alertas regionales")
    print(f"Total: {total} alertas conectadas a las clasificaciones regionales")


if __name__ == "__main__":
    main()
