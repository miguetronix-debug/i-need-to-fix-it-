#!/usr/bin/env python3
"""
build_prototipo.py — Genera prototipo.html, un archivo HTML autónomo que
implementa el asistente de "I Need To Fix It" leyendo el contenido de
content/pasos/*.json y content/referencias.json.

El contenido se incrusta en el HTML (no se hace fetch) para que el archivo
funcione al abrirlo directamente desde el disco, sin servidor.

Uso:  python3 tools/build_prototipo.py
"""

import datetime
import hashlib
import json
from pathlib import Path

FECHA = datetime.date.today()
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

RAIZ = Path(__file__).resolve().parent.parent
PASOS = RAIZ / "content" / "pasos"
SALIDA = RAIZ / "prototipo.html"

TITULOS_10 = [
    "Evaluación", "Clasificación", "Estabilidad", "Reducción", "Principios",
    "Implante", "Posición", "Abordaje", "Técnicas", "Complicaciones",
]


def cargar():
    pasos = {}
    for f in sorted(PASOS.glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        pasos[d["numero"]] = d
    refs_path = RAIZ / "content" / "referencias.json"
    refs = json.loads(refs_path.read_text(encoding="utf-8")) if refs_path.exists() else {"referencias": {}}
    cod_path = RAIZ / "content" / "aoota_codigos.json"
    codigos = json.loads(cod_path.read_text(encoding="utf-8"))["codigos"] if cod_path.exists() else {}
    # el español es lo que se muestra; el inglés queda de respaldo y como fuente
    codigos = {k: {"texto": v.get("texto_es") or v.get("texto", ""),
                   "en": v.get("texto", "") if v.get("texto_es") else "",
                   "pagina": v.get("pagina"), "figura": v.get("figura")}
               for k, v in codigos.items()}
    casos_path = RAIZ / "content" / "casos.json"
    casos = json.loads(casos_path.read_text(encoding="utf-8"))["casos"] if casos_path.exists() else []
    # Cadenas de la interfaz. Separadas del código como el resto del contenido,
    # así añadir un idioma es editar un JSON y no tocar el generador.
    int_path = RAIZ / "content" / "interfaz.json"
    idiomas = json.loads(int_path.read_text(encoding="utf-8"))["idiomas"] if int_path.exists() else {}
    # Traducciones del CONTENIDO (preguntas y etiquetas), por idioma. Lo que no
    # esté aquí se muestra en español: es preferible a dejar el hueco vacío.
    trad = {}
    # Dos fuentes, porque son dos maneras de trabajar: el Paso 2 lo genera un
    # script y vive en un archivo suelto; los pasos redactados se traducen a
    # mano, uno por archivo, para poder revisarlos de uno en uno.
    for f_tr in sorted((RAIZ / "content").glob("traducciones_*.json")):
        lang = f_tr.stem.split("_")[-1]
        trad.setdefault(lang, {}).update(
            json.loads(f_tr.read_text(encoding="utf-8")).get("pasos", {}))
    for f_tr in sorted((RAIZ / "content" / "traducciones").glob("*-*.json")):
        num, lang = f_tr.stem.split("-", 1)
        cuerpo = json.loads(f_tr.read_text(encoding="utf-8"))
        cuerpo.pop("_nota", None)
        trad.setdefault(lang, {})[str(int(num))] = cuerpo
    return pasos, refs, codigos, casos, idiomas, trad


CSS = """
*{box-sizing:border-box;margin:0;padding:0}
:root{
  /* --ink3 a #6f6e68 da 5,0:1 sobre --bg; el anterior #8b8a84 daba 3,3:1 y no
     alcanzaba el AA de WCAG para texto pequeño. */
  --bg:#faf9f7; --card:#fff; --ink:#1c1c1a; --ink2:#5f5e5a; --ink3:#6f6e68;
  --line:#e5e3dd; --line2:#cfcdc5;
  --acc:#185fa5; --acc-bg:#e6f1fb; --acc-ink:#0c447c;
  --warn:#854f0b; --warn-bg:#faeeda; --warn-line:#efa027;
  --dang:#a32d2d; --dang-bg:#fcebeb; --dang-line:#e24b4a;
  --ok:#3b6d11; --ok-bg:#eaf3de;
  --r:10px;
}
@media(prefers-color-scheme:dark){
  :root{--bg:#181816;--card:#232320;--ink:#f0efec;--ink2:#b4b2a9;--ink3:#9d9c94;
        --line:#3a3a36;--line2:#4d4d47;--acc:#85b7eb;--acc-bg:#12283d;--acc-ink:#b5d4f4;
        --warn:#fac775;--warn-bg:#3a2c12;--dang:#f09595;--dang-bg:#3d1a1a;--ok:#c0dd97;--ok-bg:#20300f;}
}
body{background:var(--bg);color:var(--ink);font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
     -webkit-font-smoothing:antialiased;padding-bottom:118px}
.wrap{max-width:820px;margin:0 auto;padding:0 16px}

header{border-bottom:1px solid var(--line);background:var(--card);position:sticky;top:0;z-index:20}
.hrow{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:12px 0}
.brand{font-size:17px;font-weight:600;letter-spacing:-.2px}
.brand small{display:block;font-size:11px;font-weight:400;color:var(--ink3);letter-spacing:0}
.modos{display:flex;gap:0;border:1px solid var(--line2);border-radius:var(--r);overflow:hidden;flex-shrink:0}
.modos button{background:none;border:0;padding:7px 13px;font:inherit;font-size:13px;color:var(--ink2);cursor:pointer}
.modos button.on{background:var(--acc);color:#fff}

/* Selector de idioma: dos letras, deliberadamente discreto. No compite con
   los modos, que son la decisión frecuente; el idioma se elige una vez. */
.hder{display:flex;gap:8px;align-items:center;flex-shrink:0}
.idiomas{display:flex;border:1px solid var(--line2);border-radius:var(--r);overflow:hidden;flex-shrink:0}
.idiomas button{background:none;border:0;padding:7px 9px;font:inherit;font-size:11.5px;
                font-weight:600;letter-spacing:.4px;color:var(--ink3);cursor:pointer}
.idiomas button.on{background:var(--ink2);color:#fff}

/* Banda que advierte, en inglés, que el razonamiento clínico sigue en español.
   Sin ella el app parecería a medio traducir, que es peor que decirlo. */
.banner{background:#fff8e6;border:1px solid #e8d9a8;border-left:3px solid #d9a441;
        border-radius:var(--r);padding:10px 13px;margin:12px 0 0;font-size:12.5px;
        line-height:1.6;color:#6b5518}
@media print{.idiomas,.banner{display:none}}

.pasos{display:flex;gap:4px;padding:10px 0 12px;overflow-x:auto}
.pchip{flex:0 0 auto;font-size:11px;padding:5px 9px;border-radius:20px;border:1px solid var(--line);
       color:var(--ink3);white-space:nowrap;background:var(--card)}
.pchip.on{background:var(--acc);border-color:var(--acc);color:#fff;font-weight:500}
.pchip.next{opacity:.5}

h1{font-size:21px;font-weight:600;margin:22px 0 4px;letter-spacing:-.3px}
.sub{color:var(--ink2);font-size:14px;margin-bottom:2px}
.qkey{font-size:17px;font-weight:500;margin:14px 0 0;padding:13px 15px;background:var(--acc-bg);
      color:var(--acc-ink);border-radius:var(--r)}

section{margin:26px 0}
h2{font-size:13px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;color:var(--ink3)}
.qrow{display:flex;align-items:baseline;justify-content:space-between;gap:12px;margin-bottom:10px}
.vermas{background:none;border:0;padding:0;font:inherit;font-size:12.5px;color:var(--acc);cursor:pointer;flex-shrink:0}
.vermas:hover{text-decoration:underline}
.ayuda{font-size:13px;color:var(--ink2);margin:-4px 0 11px;line-height:1.55}

.opts{display:grid;grid-template-columns:repeat(auto-fit,minmax(212px,1fr));gap:9px}
.opt{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:12px 14px;
     cursor:pointer;text-align:left;font:inherit;color:var(--ink);transition:border-color .12s,background .12s}
.opt:hover{border-color:var(--line2)}
.opt.sel{border-color:var(--acc);background:var(--acc-bg);border-width:2px;padding:11px 13px}
.opt b{display:block;font-size:15px;font-weight:600;margin-bottom:5px}
.opt.sel b{color:var(--acc-ink)}
.opt ul{list-style:none;font-size:12.5px;line-height:1.6;color:var(--ink2)}
.opt li{padding-left:11px;position:relative}
.opt li:before{content:"·";position:absolute;left:2px}
.opt.sel ul{color:var(--acc-ink);opacity:.92}

.alerta{border-radius:var(--r);padding:12px 14px;margin:9px 0;border-left:4px solid}
.alerta b{display:block;font-size:14px;margin-bottom:4px}
.alerta p{font-size:13px;line-height:1.6}
.a-critica{background:var(--dang-bg);border-color:var(--dang-line);color:var(--dang)}
.a-alta{background:var(--warn-bg);border-color:var(--warn-line);color:var(--warn)}
.a-media,.a-info{background:var(--card);border-color:var(--line2);color:var(--ink2)}
.a-advertencia{background:var(--warn-bg);border-color:var(--warn-line);color:var(--warn)}
.bloq{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.05em;
      display:inline-block;margin-top:7px;padding:3px 8px;border-radius:4px;background:rgba(0,0,0,.08)}

details{background:var(--card);border:1px solid var(--line);border-radius:var(--r);margin:8px 0;overflow:hidden}
summary{padding:12px 15px;cursor:pointer;font-size:14px;font-weight:500;list-style:none;display:flex;
        justify-content:space-between;align-items:center;gap:10px}
summary::-webkit-details-marker{display:none}
summary:after{content:"+";color:var(--ink3);font-size:17px;line-height:1}
details[open] summary:after{content:"−"}
.dbody{padding:0 15px 15px;font-size:14px;line-height:1.65}

table{width:100%;border-collapse:collapse;font-size:12.5px;margin:4px 0 2px}
th{text-align:left;font-weight:600;padding:7px 8px;border-bottom:1.5px solid var(--line2);color:var(--ink2);
   font-size:11.5px;text-transform:uppercase;letter-spacing:.03em}
td{padding:7px 8px;border-bottom:1px solid var(--line);vertical-align:top;line-height:1.5}
tr:last-child td{border-bottom:0}
.tscroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
.tscroll table{min-width:520px}
.tcap{font-size:12px;font-weight:600;color:var(--ink2);margin:14px 0 2px}

.rec{border-radius:var(--r);padding:12px 14px;margin:11px 0;font-size:13.5px;line-height:1.65}
.rec b{display:block;margin-bottom:4px;font-size:13.5px}
.rec-error{background:var(--dang-bg);color:var(--dang)}
.rec-regla{background:var(--acc-bg);color:var(--acc-ink)}
.rec-idea{background:var(--card);border:1px solid var(--line);color:var(--ink2)}
.lst{margin:11px 0;font-size:13.5px;line-height:1.7}
.lst b{display:block;margin-bottom:5px}
.lst ol{margin-left:18px;color:var(--ink2)}

.plan{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px;margin:26px 0}
.plan h3{font-size:15px;font-weight:600;margin-bottom:11px}
.prow{display:flex;justify-content:space-between;gap:12px;padding:8px 0;border-bottom:1px solid var(--line);font-size:13.5px}
.prow:last-of-type{border-bottom:0}
.prow span:first-child{color:var(--ink2)}
.prow span:last-child{font-weight:500;text-align:right}
.vacio{color:var(--ink3);font-size:13.5px;font-style:italic}
.deriv{margin-top:13px;padding:12px 14px;background:var(--acc-bg);border-radius:var(--r);color:var(--acc-ink)}
.deriv b{display:block;font-size:12px;text-transform:uppercase;letter-spacing:.05em;margin-bottom:5px}
.deriv b i{font-weight:400;text-transform:none;letter-spacing:0;opacity:.75}
.deriv p{font-size:13.5px;line-height:1.6}
.deriv ul{margin:7px 0 0 17px;font-size:13px;line-height:1.6}
.deriv .nota{font-size:12px;opacity:.8;margin-top:6px}
.lam{margin:11px 0 4px}
.lam img{width:100%;border-radius:8px;border:1px solid var(--line);background:#fff;display:block}
.lam.rec img{max-width:300px;margin:0 auto}
.gal{margin:12px 0 4px}
.galt{font-size:12.5px;margin-bottom:9px;opacity:.85}
.galg{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:9px}
.galo{background:#fff;border:1px solid var(--line);border-radius:8px;padding:8px;cursor:pointer;
      font:inherit;text-align:left;color:var(--ink);display:block}
.galo:hover{border-color:var(--acc)}
.galo img{width:100%;display:block;border-radius:5px;background:#fff}
.galo b{display:block;font-size:13px;font-weight:600;margin-top:6px;color:var(--acc-ink)}
.galo span{display:block;font-size:11.5px;line-height:1.45;color:var(--ink2);margin-top:2px}
.lam figcaption{font-size:11.5px;opacity:.75;margin-top:5px;line-height:1.5}
.deriv.big .cod{font-size:30px;font-weight:600;letter-spacing:1px;line-height:1.25;font-variant-numeric:tabular-nums}
.pchip{cursor:pointer}
.pchip.next{cursor:default}
.opts.chips{display:flex;flex-wrap:wrap;gap:7px}
.opt.chip{padding:8px 12px;border-radius:20px;flex:0 0 auto}
.opt.chip b{margin:0;font-size:13px;font-weight:400}
.opt.chip.sel{padding:7px 11px}
.opt.chip.sel b{font-weight:500}

.q{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:14px 16px;margin:9px 0}
.q p{font-size:14px;font-weight:500;margin-bottom:9px}
.q button{display:block;width:100%;text-align:left;background:none;border:1px solid var(--line);
          border-radius:7px;padding:9px 11px;margin:5px 0;font:inherit;font-size:13.5px;color:var(--ink);cursor:pointer}
.q button:hover{border-color:var(--line2)}
.q button.bien{background:var(--ok-bg);border-color:var(--ok);color:var(--ok);font-weight:500}
.q button.mal{background:var(--dang-bg);border-color:var(--dang-line);color:var(--dang)}
.expl{font-size:13px;line-height:1.6;color:var(--ink2);margin-top:9px;padding-top:9px;border-top:1px solid var(--line)}

.ev{font-size:13.5px;line-height:1.6;padding:9px 0;border-bottom:1px solid var(--line)}
.ev:last-child{border-bottom:0}
.niv{display:inline-block;font-size:10.5px;font-weight:600;padding:2px 7px;border-radius:4px;
     background:var(--acc-bg);color:var(--acc-ink);margin-right:7px;vertical-align:1px}
.ref{font-size:12px;color:var(--ink3);margin-top:3px}
.ref a{color:var(--acc)}

.barra{position:fixed;bottom:0;left:0;right:0;background:var(--card);border-top:1px solid var(--line);
       padding:10px 16px;display:flex;justify-content:space-between;align-items:center;gap:12px;z-index:30}
.barra .in{max-width:820px;margin:0 auto;width:100%;display:flex;justify-content:space-between;align-items:center;gap:12px}
.barra button{background:none;border:1px solid var(--line2);border-radius:var(--r);padding:9px 15px;
              font:inherit;font-size:14px;color:var(--ink);cursor:pointer}
.barra button.pri{background:var(--acc);border-color:var(--acc);color:#fff;font-weight:500}
.barra button:disabled{opacity:.4;cursor:default}

.disc{font-size:11.5px;line-height:1.6;color:var(--ink3);border-top:1px solid var(--line);
      padding:16px 0 8px;margin-top:32px}
.oculto{display:none}

/* Principio del paso: lo doctrinal, separado de los avisos del caso */
.princ{margin:18px 0 4px;background:var(--acc-bg);border-color:transparent}
.princ summary{font-size:13px;font-weight:500;color:var(--acc-ink)}
.princ summary:after{color:var(--acc-ink)}
.pidea{padding:9px 0;border-top:1px solid rgba(0,0,0,.07)}
.pidea:first-child{border-top:0;padding-top:2px}
.pidea b{display:block;font-size:13.5px;margin-bottom:3px;color:var(--acc-ink)}
.pidea p{font-size:13px;line-height:1.6;color:var(--acc-ink);opacity:.9}
.porque{background:none;border:0;padding:0;margin-top:7px;font:inherit;font-size:12px;
        font-weight:500;color:inherit;opacity:.75;cursor:pointer;text-decoration:underline}
.porque:hover{opacity:1}

/* Chips de paso: marcar los que ya tienen decisiones */
.pchip.hecho{border-color:var(--acc);color:var(--acc)}
.pchip.hecho.on{color:#fff}
.pchip.hecho:before{content:"✓ ";font-size:10px}

/* Plan consolidado */
.resumen h1{margin-top:22px}
.racc{display:flex;flex-wrap:wrap;gap:8px;margin:16px 0 4px}
.racc button{background:none;border:1px solid var(--line2);border-radius:var(--r);padding:9px 15px;
             font:inherit;font-size:14px;color:var(--ink);cursor:pointer}
.racc button.pri{background:var(--acc);border-color:var(--acc);color:#fff;font-weight:500}
.rbloque{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 18px;margin:14px 0}
.rbloque h3{font-size:15px;font-weight:600;margin-bottom:9px;display:flex;align-items:baseline;gap:9px}
.rbloque h3 span{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.05em;
                 color:var(--acc);background:var(--acc-bg);padding:3px 8px;border-radius:20px}
.rder{margin-top:11px;padding-top:10px;border-top:1px solid var(--line)}
.rder b{display:block;font-size:12.5px;text-transform:uppercase;letter-spacing:.04em;color:var(--ink3);margin-bottom:4px}
.rder p{font-size:13.5px;line-height:1.6}
.rder ul{margin:5px 0 0 17px;font-size:13px;line-height:1.6;color:var(--ink2)}
.vacio{font-size:13.5px;color:var(--ink3);font-style:italic}
.retomado{font-size:11px;background:var(--ok-bg);color:var(--ok);padding:3px 8px;border-radius:20px;margin-left:8px}

/* Marcador de la autoevaluación */
.qmini{font-size:12px;color:var(--ink3)}
.qmini.ok{color:var(--ok);font-weight:600}
.qmini.ko{color:var(--dang);font-weight:600}

/* Biblioteca de casos */
.pchip.casos{background:var(--warn-bg);border-color:var(--warn-line);color:var(--warn);font-weight:500;
             margin-right:9px;position:relative}
.pchip.casos:hover{background:var(--warn-line);color:#fff}
.pchip.casos:after{content:"";position:absolute;right:-5px;top:3px;bottom:3px;width:1px;background:var(--line2)}
.ccard{display:block;width:100%;text-align:left;background:var(--card);border:1px solid var(--line);
       border-radius:12px;padding:14px 18px;margin:11px 0;font:inherit;color:var(--ink);cursor:pointer}
.ccard:hover{border-color:var(--acc)}
.ccard b{display:block;font-size:15.5px;font-weight:600;margin:7px 0 4px}
.ccard p{font-size:13.5px;line-height:1.6;color:var(--ink2)}
.cmeta{display:flex;flex-wrap:wrap;gap:7px;align-items:center}
.creg,.ccrit,.cmin{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.04em;
                   padding:3px 8px;border-radius:20px}
.creg{background:var(--acc-bg);color:var(--acc-ink)}
.ccrit{background:var(--dang-bg);color:var(--dang)}
.cmin{background:var(--bg);color:var(--ink3);border:1px solid var(--line)}
.caso .rbloque h3 span{background:var(--bg);color:var(--ink2);border:1px solid var(--line)}
.ctxt{font-size:14px;line-height:1.7}

/* Tira de tornillos: el Paso 3 hecho manipulable */
.tira{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:14px 16px;margin:14px 0}
.tctrl{display:flex;flex-wrap:wrap;gap:14px;margin:4px 0 14px}
.tctrl label{font-size:12.5px;color:var(--ink2);display:flex;align-items:center;gap:6px}
.tctrl select{font:inherit;font-size:13px;padding:5px 8px;border-radius:7px;border:1px solid var(--line2);
              background:var(--bg);color:var(--ink)}
.tplaca{display:flex;gap:5px;justify-content:center;padding:14px 10px;background:var(--bg);
        border-radius:8px;border:1px solid var(--line);flex-wrap:wrap}
.thole{width:26px;height:26px;border-radius:50%;border:2px solid var(--line2);background:var(--card);
       cursor:pointer;padding:0;flex:0 0 auto;transition:background .12s,border-color .12s}
.thole:hover{border-color:var(--acc)}
.thole.on{background:var(--acc);border-color:var(--acc);box-shadow:inset 0 0 0 3px var(--card)}
.thole.foco{border-style:dashed;border-color:var(--dang-line);background:var(--dang-bg);cursor:not-allowed}
.tmets{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:8px;margin-top:13px}
.tmet{border-radius:8px;padding:9px 11px;border-left:3px solid}
.tmet b{display:block;font-size:13px;font-weight:600;margin-bottom:2px}
.tmet span{font-size:11.5px;opacity:.8}
.tmet.bien{background:var(--ok-bg);color:var(--ok);border-color:var(--ok)}
.tmet.mal{background:var(--warn-bg);color:var(--warn);border-color:var(--warn-line)}
.tnota{font-size:12.5px;line-height:1.6;color:var(--ink2);margin-top:11px}

/* Enlace externo */
.ext{display:block;text-decoration:none;background:var(--card);border:1px solid var(--line);
     border-left:3px solid var(--acc);border-radius:var(--r);padding:12px 15px;margin:12px 0;color:var(--ink)}
.ext:hover{border-color:var(--acc);border-left-color:var(--acc)}
.ext b{display:block;font-size:14px;color:var(--acc-ink);margin-bottom:3px}
.ext span{display:block;font-size:13px;line-height:1.6;color:var(--ink2)}
.ext i{display:block;font-style:normal;font-size:11.5px;color:var(--ink3);margin-top:5px}

/* Buscador del Paso 2 */
.busca{position:relative;margin:0 0 14px}
.busca input{width:100%;font:inherit;font-size:15px;padding:11px 14px;border-radius:var(--r);
             border:1px solid var(--line2);background:var(--card);color:var(--ink)}
.busca input:focus{outline:0;border-color:var(--acc);box-shadow:0 0 0 3px var(--acc-bg)}
.bres{position:absolute;left:0;right:0;top:100%;margin-top:5px;background:var(--card);z-index:15;
      border:1px solid var(--line2);border-radius:var(--r);max-height:290px;overflow-y:auto;
      box-shadow:0 8px 24px rgba(0,0,0,.12)}
.bres button{display:block;width:100%;text-align:left;background:none;border:0;border-bottom:1px solid var(--line);
             padding:10px 14px;font:inherit;font-size:13.5px;color:var(--ink);cursor:pointer}
.bres button:last-child{border-bottom:0}
.bres button:hover,.bres button.foco{background:var(--acc-bg)}
.bres b{color:var(--acc-ink);font-variant-numeric:tabular-nums;margin-right:8px}
.bres span{color:var(--ink2);font-size:12.5px}
.bnada{padding:11px 14px;font-size:13px;color:var(--ink3)}

@media print{
  header,.barra,.pasos,.modos,.racc,.porque,.busca{display:none}
  body{padding:0}
  details{page-break-inside:avoid}details>summary{display:none}.dbody{padding:0}
  .rbloque{page-break-inside:avoid;border:0;border-top:1px solid #ccc;border-radius:0;padding:10px 0}
  .princ{display:none}
}
"""

JS = """
const S={modo:'consulta',paso:1,dec:{},resp:{},porPaso:{},verCrit:{},vista:'paso',idioma:'es'};
let P=DATA.pasos[1];
const REFS=DATA.refs.referencias||{};
const DISPONIBLES=Object.keys(DATA.pasos).map(Number).sort((a,b)=>a-b);
const CLAVE='infi-caso-v1', CLAVE_Q='infi-quiz-v1', CLAVE_L='infi-idioma-v1';

/* -------------------------------------------------------------------- idioma
   TR('clave', {hueco:valor}) devuelve la cadena en el idioma activo. Si una
   clave falta en el idioma elegido cae al español en vez de escribir «undefined»
   en la pantalla: es preferible una palabra en el idioma equivocado a un hueco.
   El contenido clínico de los diez pasos NO pasa por aquí todavía: sigue en
   español, y en inglés se avisa de ello con una banda arriba. */
const IDIOMAS=DATA.idiomas||{};
const VERSION=DATA.version||'';

/* -------------------------------------------------- traducción del contenido
   El archivo de traducción es un CALCO PARCIAL del paso: la misma forma, solo
   con los campos ya traducidos. `fusiona` lo superpone sobre el español, así
   que traducir un campo nuevo no exige tocar el motor.

   Las listas se emparejan por `id` cuando lo tienen —el orden puede cambiar sin
   desalinear nada— y por posición cuando no, que es el caso de los bloques de
   texto y de las preguntas del examen. */
function fusiona(base, over){
  if(over===undefined||over===null) return base;
  if(Array.isArray(base)){
    if(!Array.isArray(over)) return base;
    const conId = base.length && base[0] && base[0].id!==undefined;
    if(conId){
      const porId={}; for(const o of over) if(o&&o.id!==undefined) porId[o.id]=o;
      return base.map(b=>fusiona(b, porId[b.id]));
    }
    return base.map((b,i)=>fusiona(b, over[i]));
  }
  if(base&&typeof base==='object'){
    if(typeof over!=='object'||Array.isArray(over)) return base;
    const out={}; for(const k in base) out[k]=base[k];
    for(const k in over) out[k]=fusiona(base[k], over[k]);
    return out;
  }
  return over;   // cadena, número o booleano: manda la traducción
}

/* Se calcula una vez por paso e idioma: fusionar en cada render sería tirar
   trabajo a la basura sesenta veces por pantalla. */
var _pasoCache={};
function pasoDe(n){
  if(S.idioma==='es') return DATA.pasos[n];
  const clave=S.idioma+':'+n;
  if(_pasoCache[clave]) return _pasoCache[clave];
  const tr=DATA.trad&&DATA.trad[S.idioma]&&DATA.trad[S.idioma][String(n)];
  const r = tr? fusiona(DATA.pasos[n], tr) : DATA.pasos[n];
  _pasoCache[clave]=r;
  return r;
}
function TR(k, huecos){
  const d=IDIOMAS[S.idioma]||{}, base=IDIOMAS.es||{};
  let s = (k in d && d[k]!=='') ? d[k] : (base[k]!==undefined ? base[k] : k);
  if(huecos) for(const h in huecos) s=s.split('{'+h+'}').join(huecos[h]);
  return s;
}
/* La banda no puede mentir: dice exactamente qué pasos están traducidos, y
   desaparece sola cuando ya no queda ninguno en español. Un paso cuenta como
   traducido si su calco trae título, que es lo que solo se pone al traducirlo
   entero; el Paso 2 no lo lleva porque su traducción es de vocabulario. */
function pasosTraducidos(){
  const tr=DATA.trad&&DATA.trad[S.idioma]; if(!tr) return [];
  return DISPONIBLES.filter(n=>tr[String(n)]&&tr[String(n)].titulo);
}
function textoBanner(){
  if(S.idioma==='es') return '';
  const hechos=pasosTraducidos();
  if(!hechos.length) return TR('banner_ninguno');
  if(hechos.length===DISPONIBLES.length) return TR('banner_todos');
  if(hechos.length===1)
    return TR('banner_algunos_1',{lista:TR('paso')+' '+hechos[0]});
  const lista = TR('banner_pasos')+' '+hechos.slice(0,-1).join(', ')+' & '+hechos[hechos.length-1];
  return TR('banner_algunos_n',{lista:lista});
}
function idiomasDisponibles(){ return Object.keys(IDIOMAS); }
function idioma(l){
  if(!IDIOMAS[l]) return;
  S.idioma=l;
  try{ localStorage.setItem(CLAVE_L,l); }catch(e){}
  aplicarIdioma();
  INDICE=null;   // el buscador del compendio se reconstruye en el otro idioma
  P=pasoDe(S.paso);
  cargar();
  window.scrollTo(0,0);
}
/* Lo que no se repinta en cada render —cabecera, aviso legal, atributo lang—
   se refresca aquí una vez por cambio de idioma. */
function aplicarIdioma(){
  const d=IDIOMAS[S.idioma]||{};
  document.documentElement.lang = d._html_lang || S.idioma;
  document.title = TR('titulo_doc');
  const md=document.querySelector('meta[name="description"]');
  if(md) md.setAttribute('content', TR('descripcion_doc'));
  const sub=document.querySelector('.brand small'); if(sub) sub.textContent=TR('marca_sub');
  const bc=document.querySelector('.modos button[data-m="consulta"]'); if(bc) bc.textContent=TR('modo_consulta');
  const be=document.querySelector('.modos button[data-m="estudio"]');  if(be) be.textContent=TR('modo_estudio');
  const dh=document.getElementById('desh'); if(dh) dh.textContent=TR('desarrollo_h2');
  const ds=document.getElementById('dessum'); if(ds) ds.textContent=TR('desarrollo_abrir');
  const qh=document.getElementById('quizh'); if(qh) qh.textContent=TR('autoevaluacion_h2');
  const av=document.getElementById('aviso');
  if(av) av.innerHTML='<b>'+esc(TR('aviso_b'))+'</b> '+esc(TR('aviso',{version:VERSION}));
  const ban=document.getElementById('banner');
  if(ban){ ban.textContent=textoBanner(); ban.classList.toggle('oculto', !ban.textContent); }
  const chips=(IDIOMAS[S.idioma]||{}).pasos_chips||(IDIOMAS.es||{}).pasos_chips||[];
  for(const c of document.querySelectorAll('.pchip[data-n]')){
    const n=+c.getAttribute('data-n');
    if(chips[n-1]) c.textContent=n+'. '+chips[n-1];
  }
  const cc=document.getElementById('chipcasos'); if(cc) cc.textContent=TR('casos_h1');
  const bb=document.getElementById('brei'); if(bb) bb.textContent=TR('b_reiniciar');
  const ba=document.getElementById('ant'); if(ba) ba.textContent=TR('b_atras');
  for(const b of document.querySelectorAll('.idiomas button'))
    b.classList.toggle('on', b.getAttribute('data-l')===S.idioma);
}

/* ---------------------------------------------------------------- persistencia
   El caso vive en localStorage y, además, se puede llevar en la URL. Si al
   abrir hay hash manda el hash (alguien te compartió un caso); si no, se
   recupera lo último que estabas haciendo. */
function guardar(){
  try{ localStorage.setItem(CLAVE, JSON.stringify({porPaso:S.porPaso,paso:S.paso,modo:S.modo})); }catch(e){}
  escribirHash();
}
function restaurar(){
  const delHash=leerHash();
  if(delHash){ S.porPaso=delHash.porPaso||{}; S.paso=delHash.paso||1; return true; }
  try{
    const raw=localStorage.getItem(CLAVE); if(!raw) return false;
    const g=JSON.parse(raw);
    S.porPaso=g.porPaso||{}; S.paso=DATA.pasos[g.paso]?g.paso:1; S.modo=g.modo||'consulta';
    return Object.keys(S.porPaso).some(k=>Object.keys(S.porPaso[k]||{}).length);
  }catch(e){ return false; }
}
function hayCaso(){ return Object.keys(S.porPaso).some(k=>Object.keys(S.porPaso[k]||{}).length); }

/* El hash guarda solo lo elegido, en un formato corto y legible:
   #p=3&2=hueso:h-4,segmento:s-42&3=zonas:z-unica,palancas:p-longitud|p-span   */
function escribirHash(){
  const trozos=[];
  for(const n of DISPONIBLES){
    const d=S.porPaso[n]; if(!d) continue;
    // el asterisco marca multiselección, para no perder el tipo al volver
    const pares=Object.keys(d).filter(k=>d[k]&&(!Array.isArray(d[k])||d[k].length))
      .map(k=>k+':'+(Array.isArray(d[k])?'*'+d[k].join('|'):d[k]));
    if(pares.length) trozos.push(n+'='+pares.join(','));
  }
  const h = trozos.length? '#p='+S.paso+'&'+trozos.join('&') : '';
  if(location.hash===h) return;
  // en file:// algunos navegadores rechazan replaceState
  try{ history.replaceState(null,'',location.pathname+location.search+h); }
  catch(e){ try{ location.hash=h; }catch(e2){} }
}
function leerHash(){
  const h=location.hash.replace(/^#/,''); if(!h) return null;
  const out={porPaso:{},paso:1};
  for(const parte of h.split('&')){
    const i=parte.indexOf('='); if(i<0) continue;
    const clave=parte.slice(0,i), valor=parte.slice(i+1);
    if(clave==='p'){ out.paso=+valor||1; continue; }
    const n=+clave; if(!DATA.pasos[n]) continue;
    const dec={};
    for(const par of valor.split(',')){
      const j=par.indexOf(':'); if(j<0) continue;
      const k=par.slice(0,j), v=par.slice(j+1);
      dec[k]= v.charAt(0)==='*' ? v.slice(1).split('|') : v;
    }
    out.porPaso[n]=dec;
  }
  return Object.keys(out.porPaso).length? out : null;
}

function urlRef(r){
  if(r.url) return r.url;
  if(r.pmid) return 'https://pubmed.ncbi.nlm.nih.gov/'+r.pmid+'/';
  if(r.pmc) return 'https://www.ncbi.nlm.nih.gov/pmc/articles/'+r.pmc+'/';
  if(r.doi) return 'https://doi.org/'+r.doi;
  return null;
}
function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}

function visible(d){
  if(d.mostrarSi&&!cumple(d.mostrarSi)) return false;
  if(d.mostrarSiAlguno&&!d.mostrarSiAlguno.some(cumple)) return false;
  return d.opciones.some(o=>!o.soloSi||cumple(o.soloSi));
}
function sugerida(){
  const e=S.dec['estado-fisiologico']; if(!e) return null;
  const o=P.decisiones.find(d=>d.id==='estado-fisiologico').opciones.find(x=>x.id===e);
  return o&&o.consecuencias?o.consecuencias.estrategia:null;
}

function alertas(){
  const out=[];
  for(const a of P.alertas){
    let ok=false;
    if(a.mostrarSiempre) ok=true;
    else if(a.mostrarSi) ok=cumple(a.mostrarSi);
    else if(a.mostrarSiAlguno) ok=a.mostrarSiAlguno.some(cumple);
    if(ok&&a.noSi&&cumple(a.noSi)) ok=false;
    if(ok&&a.noSiAlguno&&a.noSiAlguno.some(cumple)) ok=false;
    if(ok&&a.noSiTodo&&cumpleTodo(a.noSiTodo)) ok=false;
    // «siempre» marca lo doctrinal, que se muestra aparte de los avisos del caso
    if(ok) out.push(Object.assign({},a,{siempre:!!a.mostrarSiempre}));
  }
  for(const r of P.reglasCoherencia){
    let ok=true;
    if(r.si.estrategiaDistintaDeSugerida){
      const s=sugerida(); ok = !!(s && S.dec['estrategia'] && S.dec['estrategia']!==s);
    } else {
      ok=cumple(r.si);
    }
    if(ok&&r.noSi&&cumple(r.noSi)) ok=false;
    if(ok&&r.noSiAlguno&&r.noSiAlguno.some(cumple)) ok=false;
    if(ok&&r.noSiTodo&&cumpleTodo(r.noSiTodo)) ok=false;
    if(ok) out.push({id:r.id,severidad:r.severidad,titulo:r.titulo||TR('coherencia'),texto:r.mensaje,bloqueante:r.bloqueante,regla:true});
  }
  const hayCritica=out.some(a=>a.regla&&a.severidad==='critica');
  const filtrado=out.filter(a=>!(a.regla&&a.severidad==='info'&&hayCritica));
  const orden={critica:0,advertencia:1,alta:2,media:3,info:4};
  return filtrado.sort((a,b)=>(orden[a.severidad]??9)-(orden[b.severidad]??9));
}

// Hechos derivados de pasos anteriores, para que un paso pueda razonar sobre
// lo que se decidió antes. Se consultan con la clave especial "ctx".
const DIAFISARIOS=['12','2R2','2U2','32','42','4F2','15.2'];
function contexto(){
  const d2=S.porPaso[2]||{}; const t=[];
  const opt=(dec,id)=>{ const p=pasoDe(2); if(!p) return null;
    const dd=p.decisiones.find(x=>x.id===dec); if(!dd) return null;
    return dd.opciones.find(x=>x.id===id)||null; };
  const seg=d2['segmento']?(opt('segmento',d2['segmento'])||{}).codigo:null;
  const tip=d2['tipo']?(opt('tipo',d2['tipo'])||{}).codigo:null;
  if(seg){
    const base=seg.split('.')[0];
    const clase = seg==='44'?'maleolar' : (base==='61'||base==='62')?'pelvis'
                : DIAFISARIOS.indexOf(seg)>=0?'diaf' : 'artic';
    t.push(clase); t.push('seg-'+seg);
    if(tip){ t.push('tipo'+tip); t.push(clase+'-'+tip); }
  }
  // hechos del paso 3 (estabilidad)
  const d3=S.porPaso[3]||{};
  if(d3['zonas']==='z-unica') t.push('zonas-una');
  if(d3['zonas']==='z-dos') t.push('zonas-dos');
  if(d3['estabilidad']==='e-absoluta') t.push('est-absoluta');
  if(d3['estabilidad']==='e-relativa') t.push('est-relativa');
  if(d3['estab-articular']==='ea-absoluta') t.push('art-absoluta');
  if(d3['estab-articular']==='ea-relativa') t.push('art-relativa');
  if(d3['estab-metafisis']==='em-absoluta') t.push('meta-absoluta');
  if(d3['estab-metafisis']==='em-relativa') t.push('meta-relativa');
  // región anatómica, para posición (paso 7) y abordaje (paso 8)
  if(seg){ const r=REGION[seg]||REGION[seg.split('.')[0]]; if(r) t.push('reg-'+r); }
  // marcado en cualquier decisión de un paso, respetando la multiselección
  const hay=(n,ids)=>{ const d=S.porPaso[n]||{};
    for(const k in d){ const v=d[k];
      if(Array.isArray(v)){ if(v.some(x=>ids.indexOf(x)>=0)) return true; }
      else if(ids.indexOf(v)>=0) return true; }
    return false; };
  // hechos del paso 4 (reducción)
  if(hay(4,['t-anatomica','ta-anatomica','tm-anatomica'])) t.push('red-anatomica');
  if(hay(4,['t-funcional','ta-funcional','tm-funcional'])) t.push('red-funcional');
  if(hay(4,['v-directa','va-directa','vm-directa'])) t.push('via-directa');
  if(hay(4,['v-percutanea','va-percutanea','vm-percutanea'])) t.push('via-percutanea');
  if(hay(4,['v-indirecta','va-indirecta','vm-indirecta'])) t.push('via-indirecta');
  // hechos del paso 5 (principios)
  if(hay(5,['pr-compresion','pa-compresion','pm-compresion'])) t.push('usa-compresion');
  if(hay(5,['pr-banda','pa-banda'])) t.push('usa-banda');
  if(hay(5,['pr-sosten','pa-sosten','pm-sosten'])) t.push('usa-sosten');
  if(hay(5,['pr-ferulaje','pm-ferulaje'])) t.push('usa-ferulaje');
  if(hay(5,['n-si'])) t.push('usa-neutralizacion');
  if(hay(5,['mf-clavo'])) t.push('fer-clavo');
  if(hay(5,['mf-placa-puente'])) t.push('fer-puente');
  if(hay(5,['mf-tutor'])) t.push('fer-tutor');
  if(hay(5,['mc-tornillo-tecnica','mc-tornillo-diseno','mc-tornillo-por-placa'])) t.push('comp-tornillo');
  if(hay(5,['mc-placa-dcp'])) t.push('comp-placa');
  // Cualquier opción puede declarar «emite»: así una clasificación regional
  // alimenta el razonamiento de los pasos siguientes sin tocar el motor.
  for(const n of Object.keys(S.porPaso)){
    const p=pasoDe(n); if(!p) continue;
    const d=S.porPaso[n]||{};
    for(const dd of p.decisiones){
      const v=d[dd.id]; if(!v) continue;
      for(const id of (Array.isArray(v)?v:[v])){
        const o=dd.opciones.find(x=>x.id===id);
        if(o&&o.emite) for(const f of o.emite) if(t.indexOf(f)<0) t.push(f);
      }
    }
  }
  // hechos del paso 6 (implante)
  if(hay(6,['i-tornillo'])) t.push('imp-tornillo');
  if(hay(6,['i-placa'])) t.push('imp-placa');
  if(hay(6,['i-clavo'])) t.push('imp-clavo');
  if(hay(6,['i-tutor'])) t.push('imp-tutor');
  if(hay(6,['i-agujas'])) t.push('imp-agujas');
  if(hay(6,['pl-bloqueada','pl-va'])) t.push('placa-bloqueada');
  if(hay(6,['pl-no-bloqueada'])) t.push('placa-no-bloqueada');
  return t;
}
// Mapa segmento AO → región anatómica quirúrgica.
const REGION={'11':'hombro','14':'hombro','15':'hombro','16':'torax',
 '12':'humero','13':'codo','2R1':'codo','2U1':'codo',
 '2R2':'antebrazo','2U2':'antebrazo','2R3':'muneca','2U3':'muneca',
 '71':'mano','72':'mano','73':'mano','74':'mano','75':'mano','76':'mano','77':'mano','78':'mano',
 '31':'cadera','32':'femur','33':'rodilla','34':'rodilla','41':'rodilla','4F1':'rodilla',
 '42':'tibia','4F2':'tibia','43':'tobillo','44':'tobillo','4F3':'tobillo',
 '81':'pie','82':'pie','83':'pie','84':'pie','85':'pie','87':'pie','88':'pie',
 '51':'columna','52':'columna','53':'columna','61':'pelvis','62':'pelvis'};
function marcado(k,v){
  if(k==='ctx'||k==='ctxTodos') return contexto().indexOf(v)>=0;
  const x=S.dec[k]; return Array.isArray(x)? x.includes(v) : x===v;
}
// "ctx" es una lista alternativa: basta con que se cumpla uno de los hechos.
// "ctxTodos" exige que se cumplan todos: es la forma de encadenar dos hechos.
function cumple(si){
  for(const k in si){
    if(k==='ctxTodos'){ if(!si[k].every(v=>marcado(k,v))) return false; continue; }
    if(!si[k].some(v=>marcado(k,v))) return false;
  }
  return true;
}
// Variante exigente: hacen falta TODOS los valores, no basta con uno.
function cumpleTodo(si){ for(const k in si){ if(!si[k].every(v=>marcado(k,v))) return false; } return true; }
// Una opción se ve si cumple «soloSi» y NO cumple «noSi». Hacía falta la
// negación para poder decir «esta vía existe en la rodilla, salvo en la meseta,
// donde la lista es otra»: sin ella habría que enumerar todo lo demás.
function opcionesVisibles(d){
  return d.opciones.filter(o=>
    (!o.soloSi || cumple(o.soloSi)) &&
    (!o.noSi   || !cumple(o.noSi)));
}
function esMulti(d){ return d.tipo==='opcionMultiple'; }

function cod(id){ for(const dd of P.decisiones){ const o=dd.opciones.find(x=>x.id===id); if(o) return o.codigo; } return ''; }

function baseCodigo(c){
  const seg=S.dec[c.segmento]; if(!seg) return null;
  let base=cod(seg);
  if(base.indexOf('_')>=0){
    const idv=c.identificador?S.dec[c.identificador]:null;
    if(idv){ const partes=cod(idv).split('.'); let i=0; base=base.replace(/_/g,()=>partes[i++]||'_'); }
  }
  if(c.tipo&&S.dec[c.tipo]) base+=cod(S.dec[c.tipo]); else return {codigo:base, completo:false};
  if(c.grupo&&S.dec[c.grupo]) base+=cod(S.dec[c.grupo]);
  if(c.subgrupo&&S.dec[c.subgrupo]) base+=cod(S.dec[c.subgrupo]);
  return {codigo:base, completo:true};
}

function codigoAO(d){
  const c=(d&&d.campos)||{segmento:'segmento',tipo:'tipo',grupo:'grupo',calificaciones:'calificaciones',modificadores:'modificadores'};
  const b=baseCodigo(c); if(!b||!b.completo) return null;
  let txt=b.codigo;
  const q=(c.calificaciones?(S.dec[c.calificaciones]||[]):[]).map(cod).filter(Boolean);
  if(q.length) txt+='('+q.join(', ')+')';
  const m=(c.modificadores?(S.dec[c.modificadores]||[]):[]).map(cod).filter(Boolean);
  if(m.length) txt+='['+m.join(', ')+']';
  return txt;
}

// En inglés se sirve el texto ORIGINAL del compendio, que es la fuente:
// no es una traducción nuestra, es el documento de la AO tal cual.
function txtDe(c){ const r=DATA.codigos?DATA.codigos[c]:null; if(!r) return '';
  if(S.idioma!=='es' && r.en) return r.en;
  return r.texto||''; }

function descripcionCompleta(){
  const seg=S.dec['segmento']; if(!seg) return null;
  // cadena de códigos: segmento → tipo → grupo → subgrupo
  const cadena=[]; let acum=cod(seg); cadena.push(acum);
  if(S.dec['tipo']){ acum+=cod(S.dec['tipo']); cadena.push(acum);
    if(S.dec['grupo']){ acum+=cod(S.dec['grupo']); cadena.push(acum);
      if(S.dec['subgrupo']){ acum+=cod(S.dec['subgrupo']); cadena.push(acum); } } }
  // El compendio a veces reescribe el nivel anterior dentro del siguiente
  // («Proximal end segment» + «Tibia, proximal end segment, complete articular»).
  // Encadenar sin más duplicaría la frase, así que antes de concatenar se
  // comprueba si el nivel nuevo ya contiene al anterior.
  const norm=s=>String(s).toLowerCase().replace(/[.,;:]/g,'').replace(/\s+/g,' ').trim();
  let frase='', prev='';
  for(const c of cadena){
    const t=txtDe(c); if(!t) continue;
    if(!frase){ frase=t; prev=t; continue; }
    const p0=prev.split(/[\s,]+/)[0].toLowerCase();
    if(norm(t).indexOf(norm(frase))>=0) frase=t;         // ya lo dice todo: sustituye
    else if(norm(t).indexOf(norm(prev))>=0) frase=t;     // reescribe el nivel anterior
    else if(p0 && t.toLowerCase().indexOf(p0)===0) frase=t;  // repite el tronco: más específico
    else frase=frase.replace(/[.\s]+$/,'')+', '+t.charAt(0).toLowerCase()+t.slice(1);
    prev=t;
  }
  frase=frase.charAt(0).toUpperCase()+frase.slice(1);
  // calificaciones y modificadores, en palabras
  const et=id=>{ for(const dd of P.decisiones){ const o=dd.opciones.find(x=>x.id===id); if(o) return o.etiqueta; } return ''; };
  const q=(S.dec['calificaciones']||[]).map(et).map(x=>x.replace(/^\([a-z]\)\s*/,'')).filter(Boolean);
  if(q.length) frase+=' — '+q.join('; ');
  const m=(S.dec['modificadores']||[]).map(et).map(x=>x.replace(/^\[[^\]]+\]\s*/,'')).filter(Boolean);
  if(m.length) frase+=' · '+m.join('; ');
  // figura: primero el recorte del código más profundo; si no lo hay, la lámina
  let figura=null, pagina=null, recorte=false;
  for(let i=cadena.length-1;i>=0;i--){
    const r=DATA.codigos?DATA.codigos[cadena[i]]:null; if(!r) continue;
    if(!figura&&r.figura){ figura=r.figura; recorte=true; }
    if(!pagina&&r.pagina) pagina=r.pagina;
    if(figura) break;
  }
  if(!figura&&pagina) figura='content/figuras/p'+pagina+'.jpg';
  return {frase:frase, pagina:pagina, imagen:figura, recorte:recorte};
}

// Si aún no se ha bajado al último nivel, ofrecer las figuras de los hijos
// para elegir viendo el dibujo en vez de adivinar.
function galeriaHijos(){
  let decHijo=null;
  if(S.dec['grupo']&&!S.dec['subgrupo']) decHijo='subgrupo';
  else if(S.dec['tipo']&&!S.dec['grupo']) decHijo='grupo';
  else if(S.dec['segmento']&&!S.dec['tipo']) decHijo='tipo';
  if(!decHijo) return null;
  const d=P.decisiones.find(x=>x.id===decHijo); if(!d) return null;
  const hijos=opcionesVisibles(d).map(o=>{
    const reg=o.codigoCompleto&&DATA.codigos?DATA.codigos[o.codigoCompleto]:null;
    return {id:o.id, dec:decHijo, codigo:o.codigoCompleto||'', etiqueta:o.etiqueta,
            texto:(o.criterios&&o.criterios[0])||'', figura:reg?reg.figura:null};
  }).filter(h=>h.figura);
  return hijos.length>1?{decision:decHijo, hijos:hijos}:null;
}

function codigoCanonico(){
  const der=(P.derivados||[]).find(x=>x.tipo==='codigoAO'); if(!der) return null;
  const seg=S.dec['segmento']; if(!seg) return null;
  let base=cod(seg);
  if(S.dec['tipo']) base+=cod(S.dec['tipo']);
  if(S.dec['grupo']) base+=cod(S.dec['grupo']);
  if(S.dec['subgrupo']) base+=cod(S.dec['subgrupo']);
  return base;
}

function derivados(){
  const out=[];
  for(const d of (P.derivados||[])){
    if(d.tipo==='textoCodigo'){
      const desc=descripcionCompleta();
      if(!desc) continue;
      const gal=galeriaHijos();
      out.push({titulo:d.titulo,principal:desc.frase,lineas:[],
                nota:'Texto del compendio AO/OTA 2018 encadenando hueso, segmento, tipo, grupo y subgrupo.',
                imagen:gal?null:desc.imagen, pagina:desc.pagina, recorte:desc.recorte, galeria:gal});
    } else if(d.tipo==='codigoAO'){
      const c=codigoAO(d); if(!c) continue;
      out.push({titulo:d.titulo,principal:c,lineas:[],nota:d.nota,destacado:true});
    } else if(d.tipo==='plantilla'){
      const req=d.requiere||[];
      if(req.some(k=>!S.dec[k])) continue;
      let txt=d.plantilla||d.texto||'';
      for(const k of req){
        const dec=P.decisiones.find(x=>x.id===k); if(!dec) continue;
        const op=dec.opciones.find(o=>o.id===S.dec[k]); if(!op) continue;
        txt=txt.replace('{'+k+'}', op.codigo!==undefined?op.codigo:op.etiqueta);
      }
      if(!txt) continue;
      out.push({titulo:d.titulo,principal:txt,lineas:[],nota:d.nota,destacado:!!d.requiere});
    } else {
      let rs=(d.reglas||[]).filter(r=>cumple(r.si));
      if(!rs.length) continue;
      rs.sort((a,b)=>(a.prioridad??0)-(b.prioridad??0));
      if(d.modo==='primera') rs=[rs[0]];
      out.push({titulo:d.titulo,principal:rs[0].texto,lineas:rs.slice(1).map(r=>r.texto),nota:d.nota});
    }
  }
  return out;
}

function bloque(b){
  if(b.tipo==='parrafo') return '<p style="margin:9px 0;font-size:14px;line-height:1.7">'+esc(b.texto)+'</p>';
  if(b.tipo==='recuadro') return '<div class="rec rec-'+(b.variante||'idea')+'"><b>'+esc(b.titulo)+'</b>'+esc(b.texto)+'</div>';
  if(b.tipo==='lista') return '<div class="lst"><b>'+esc(b.titulo)+'</b><ol>'+b.items.map(i=>'<li>'+esc(i)+'</li>').join('')+'</ol></div>';
  if(b.tipo==='tabla'){
    return '<div class="tcap">'+esc(b.titulo)+'</div><div class="tscroll"><table><thead><tr>'+
      b.encabezados.map(h=>'<th>'+esc(h)+'</th>').join('')+'</tr></thead><tbody>'+
      b.filas.map(f=>'<tr>'+f.map(c=>'<td>'+esc(c)+'</td>').join('')+'</tr>').join('')+'</tbody></table></div>';
  }
  if(b.tipo==='enlace') return '<a class="ext" href="'+esc(b.url)+'" target="_blank" rel="noopener">'+
    '<b>'+esc(b.titulo)+'</b><span>'+esc(b.texto)+'</span><i>'+esc(b.fuente||'')+' ↗</i></a>';
  if(b.tipo==='tiraTornillos') return '<div id="tira"></div>';
  return '';
}

/* ------------------------------------------------------ tira de tornillos
   Las tres cifras que enseña el Paso 3 son aritmética, no simulación:
     relación de cobertura = largo de placa / largo de fractura
     densidad de tornillos = tornillos puestos / agujeros
     longitud de trabajo  = separación entre los tornillos más internos
   Encender y apagar agujeros las mueve en vivo, que es la única forma de que
   dejen de ser tres números leídos y pasen a ser algo que se manipula. */
// Arranca en un montaje correcto: es más instructivo romperlo que arreglarlo.
const T={n:12, largoFx:4, puestos:[0,1,2,9,10,11]};
function tiraTogglear(i){
  const j=T.puestos.indexOf(i);
  if(j>=0) T.puestos.splice(j,1); else T.puestos.push(i);
  tiraPintar();
}
function tiraSet(k,v){
  T[k]=+v;
  const c=tiraCalculo();
  T.puestos=T.puestos.filter(i=>i<T.n&&!c.dentro(i));   // nada dentro del foco
  tiraPintar();
}
function tiraCalculo(){
  // el foco ocupa «largoFx» agujeros centrados en la placa; los que caen
  // dentro no admiten tornillo
  const desde=(T.n-T.largoFx)/2, hasta=desde+T.largoFx;
  const dentro=i=>i>=desde&&i<hasta;
  const izq=T.puestos.filter(i=>i<desde).sort((a,b)=>a-b);
  const der=T.puestos.filter(i=>i>=hasta).sort((a,b)=>a-b);
  const trabajo = (izq.length&&der.length) ? (der[0]-izq[izq.length-1]) : null;
  return {
    dentro:dentro,
    tornillos:T.puestos.length,
    densidad: T.puestos.length/T.n,
    cobertura: (T.n-1)/Math.max(T.largoFx,0.5),
    trabajo:trabajo,
    izq:izq.length, der:der.length,
    // «simple» cuando el foco cabe en un hueco: es el criterio estricto de Gautier
    simple: T.largoFx<=1
  };
}
function tiraPintar(){
  const el=document.getElementById('tira'); if(!el) return;
  const c=tiraCalculo();
  const objDen = c.simple? 0.4 : 0.5, objCob = c.simple? 8 : 2.5;
  const ok=(v,lim,mayor)=>mayor? v>=lim : v<=lim;
  const marca=(v,lim,mayor,txt)=>'<div class="tmet'+(ok(v,lim,mayor)?' bien':' mal')+'"><b>'+txt+'</b>'+
    '<span>'+(mayor?'objetivo ≥ ':'objetivo ≤ ')+String(lim).replace('.',',')+'</span></div>';
  let h='<div class="tira"><div class="tcap">Prueba con la placa: enciende y apaga agujeros</div>'+
    '<div class="tctrl">'+
      '<label>Agujeros <select onchange="tiraSet(\\'n\\',this.value)">'+
        [6,8,10,12,14,16].map(n=>'<option value="'+n+'"'+(n===T.n?' selected':'')+'>'+n+'</option>').join('')+
      '</select></label>'+
      '<label>Largo del foco <select onchange="tiraSet(\\'largoFx\\',this.value)">'+
        [[1,'trazo simple'],[2,'cuña'],[4,'conminuta corta'],[6,'conminuta larga']]
          .map(o=>'<option value="'+o[0]+'"'+(o[0]===T.largoFx?' selected':'')+'>'+o[1]+'</option>').join('')+
      '</select></label>'+
    '</div><div class="tplaca">';
  for(let i=0;i<T.n;i++){
    const puesto=T.puestos.indexOf(i)>=0, foco=c.dentro(i);
    h+='<button class="thole'+(puesto?' on':'')+(foco?' foco':'')+'" '+
       (foco?'disabled title="Sobre el foco: aquí no va tornillo"':'onclick="tiraTogglear('+i+')"')+'></button>';
  }
  h+='</div><div class="tmets">'+
    marca(c.densidad, objDen, false, TR('tira_densidad',{v:c.densidad.toFixed(2).replace('.',S.idioma==='es'?',':'.')}))+
    marca(c.cobertura, objCob, true, TR('tira_cobertura',{v:c.cobertura.toFixed(1).replace('.',S.idioma==='es'?',':'.')}))+
    marca(Math.min(c.izq,c.der), 3, true, TR('tira_por_fragmento',{a:c.izq,b:c.der}))+
    (c.trabajo!==null? marca(c.trabajo, 3, true, TR('tira_trabajo',{n:c.trabajo}))
                     : '<div class="tmet mal"><b>'+esc(TR('tira_trabajo_sin'))+'</b><span>'+esc(TR('tira_trabajo_faltan'))+'</span></div>')+
  '</div><p class="tnota">'+
    (c.simple
      ? 'Trazo simple: Gautier y Sommer piden cobertura por encima de 8-10 y densidad por debajo de 0,3-0,4. Si no llegas, el camino correcto es comprimir, no puentear.'
      : 'Foco multifragmentario: cobertura por encima de 2-3 y densidad por debajo de 0,5. Vaciar los agujeros vecinos al foco es lo que más flexibiliza el montaje.')+
  '</p></div>';
  el.innerHTML=h;
}

function render(){
  document.querySelectorAll('.modos button').forEach(b=>b.classList.toggle('on',b.dataset.m===S.modo));

  const aparte = S.vista!=='paso';
  document.getElementById('vistapaso').classList.toggle('oculto',aparte);
  const vr=document.getElementById('vistaresumen');
  vr.classList.toggle('oculto',!aparte);
  if(aparte){
    vr.innerHTML = S.vista==='resumen'? pintarResumen()
                 : S.vista==='casos'? pintarCasos() : pintarCaso();
    pintarBarra(); return;
  }

  let h='';
  for(const d of P.decisiones){
    if(!visible(d)) continue;
    const sug = d.id==='estrategia' ? sugerida() : null;
    const vis=opcionesVisibles(d), multi=esMulti(d);
    const abierto=!!S.verCrit[d.id];
    // Los grupos largos se pintan como fichas compactas, pero «Ver más» los
    // despliega a tarjeta para que sus criterios sean alcanzables: si no, el
    // contenido más valioso (las cifras, la estructura en riesgo) no se ve.
    const chip=(multi||vis.length>12)&&!abierto;
    const hayCrit=vis.some(o=>(o.criterios||[]).length);
    h+='<section><div class="qrow"><h2>'+esc(d.pregunta)+'</h2>'+
       (hayCrit?'<button class="vermas" onclick="verCrit(\\''+d.id+'\\')">'+(abierto?TR('ocultar'):TR('ver_mas'))+'</button>':'')+
       '</div>';
    if(d.ayuda && (abierto||S.modo==='estudio')) h+='<p class="ayuda">'+esc(d.ayuda)+'</p>';
    h+='<div class="opts'+(chip?' chips':'')+'">';
    for(const o of vis){
      const sel=marcado(d.id,o.id);
      h+='<button class="opt'+(sel?' sel':'')+(chip?' chip':'')+'" onclick="pick(\\''+d.id+'\\',\\''+o.id+'\\')"><b>'+esc(o.etiqueta)+
         (sug===o.id&&!sel?' <span style="font-weight:400;font-size:11.5px;color:var(--acc)">'+esc(TR('sugerida'))+'</span>':'')+'</b>'+
         (abierto?'<ul>'+(o.criterios||[]).map(c=>'<li>'+esc(c)+'</li>').join('')+'</ul>':'')+'</button>';
    }
    h+='</div>';
    if(d.nota) h+='<p class="ayuda" style="margin-top:9px">'+esc(d.nota)+'</p>';
    h+='</section>';
  }
  // El buscador solo tiene sentido donde hay 4 592 opciones: la clasificación
  const buscador = P.numero===2
    ? '<div class="busca"><input id="binput" type="search" autocomplete="off" '+
      'placeholder="'+esc(TR('busca_ph'))+'" '+
      'oninput="buscar(this.value)" onblur="setTimeout(cerrarBusca,180)"><div class="bres" id="bres"></div></div>'
    : '';
  document.getElementById('decs').innerHTML=buscador+h;

  // Los recordatorios doctrinales (mostrarSiempre) no son avisos sobre ESTE
  // caso: se sacan del bloque de alertas para que las alertas signifiquen algo.
  const todas=alertas();
  const doctrina=todas.filter(a=>a.siempre), al=todas.filter(a=>!a.siempre);
  document.getElementById('principio').innerHTML = doctrina.length
    ? '<details class="princ"'+(S.modo==='estudio'?' open':'')+'><summary>'+esc(TR('principio_del_paso',{n:P.numero}))+
      ' · '+esc(doctrina.length===1?TR('idea_1'):TR('idea_n',{n:doctrina.length}))+
      '</summary><div class="dbody">'+doctrina.map(a=>'<div class="pidea"><b>'+esc(a.titulo)+'</b><p>'+esc(a.texto)+'</p></div>').join('')+
      '</div></details>'
    : '';
  document.getElementById('alerts').innerHTML = al.length
    ? '<h2>'+esc(TR('avisos_h2'))+'</h2>'+al.map(a=>'<div class="alerta a-'+a.severidad+'"><b>'+esc(a.titulo)+'</b><p>'+esc(a.texto)+'</p>'+
        (a.bloqueante?'<span class="bloq">'+esc(TR('bloqueante'))+'</span>':'')+
        '<button class="porque" onclick="porQue()">'+esc(TR('por_que'))+'</button></div>').join('')
    : '';

  const filas=[];
  for(const d of P.decisiones){
    if(!visible(d)) continue;
    const v=S.dec[d.id]; if(!v) continue;
    const et=Array.isArray(v)
      ? v.map(id=>{const o=d.opciones.find(x=>x.id===id); return o?o.etiqueta:'';}).filter(Boolean).join(' · ')
      : (function(){const o=d.opciones.find(x=>x.id===v); return o?o.etiqueta:'';})();
    if(et) filas.push('<div class="prow"><span>'+esc(d.pregunta)+'</span><span>'+esc(et)+'</span></div>');
  }
  const bloqueantes=al.filter(a=>a.bloqueante);
  const der=derivados().map(d=>'<div class="deriv'+(d.destacado?' big':'')+'"><b>'+esc(d.titulo)+' <i>· derivado</i></b>'+
      (d.destacado?'<p class="cod">'+esc(d.principal)+'</p>':'<p>'+esc(d.principal)+'</p>')+
      (d.lineas.length?'<ul>'+d.lineas.map(x=>'<li>'+esc(x)+'</li>').join('')+'</ul>':'')+
      (d.galeria?'<div class="gal"><p class="galt">'+esc(TR('elige_dibujo'))+
        (d.galeria.decision==='subgrupo'?'subgrupos':d.galeria.decision==='grupo'?'grupos':'tipos')+' posibles:</p><div class="galg">'+
        d.galeria.hijos.map(h=>'<button class="galo" onclick="pick(\\''+h.dec+'\\',\\''+h.id+'\\')">'+
          '<img src="'+esc(h.figura)+'" alt="'+esc(h.codigo)+'" loading="lazy">'+
          '<b>'+esc(h.codigo)+'</b><span>'+esc(h.texto)+'</span></button>').join('')+'</div></div>':'')+
      (d.imagen?'<figure class="lam'+(d.recorte?' rec':'')+'"><img src="'+esc(d.imagen)+'" alt="Figura del compendio" loading="lazy"><figcaption>'+
        esc(d.recorte?TR('fig_recorte'):TR('fig_lamina'))+
        (d.pagina?esc(TR('fig_pagina',{n:d.pagina})):'')+esc(TR('fig_educativa'))+'</figcaption></figure>':'')+
      (d.nota?'<p class="nota">'+esc(d.nota)+'</p>':'')+'</div>').join('');
  document.getElementById('plan').innerHTML='<h3>'+esc(TR('plan_del_paso',{n:P.numero}))+'</h3>'+
    (filas.length?filas.join(''):'<p class="vacio">Aún no has tomado ninguna decisión.</p>')+der+
    (bloqueantes.length?'<div class="alerta a-critica" style="margin-top:13px"><b>'+esc(TR('antes_que_nada'))+'</b><p>'+
      bloqueantes.map(b=>esc(b.texto)).join(' ')+'</p></div>':'')+
    (filas.length? '<p style="font-size:12.5px;color:var(--ink3);margin-top:13px;line-height:1.6">'+esc(P.sintesis)+'</p>':'');

  document.getElementById('estudio').classList.toggle('oculto',S.modo!=='estudio');
  document.getElementById('estudio2').classList.toggle('oculto',S.modo!=='estudio');
  pintarBarra();
}

/* ------------------------------------------------------- buscador del Paso 2
   Un campo único que acepta el código («42B2») o el nombre («meseta», «pilón»).
   Es lo que convierte al cirujano formado en usuario: él no quiere navegar
   hueso → segmento → tipo → grupo; quiere escribir y llegar. */
let INDICE=null;
const SINONIMOS={'meseta':'41','platillo':'41','pilon':'43','pilón':'43','tobillo':'44',
  'maleolar':'44','cadera':'31','pertrocanterea':'31','pertrocantérea':'31','cuello femoral':'31',
  'rodilla':'33','muñeca':'2R3','muneca':'2R3','colles':'2R3','codo':'13','olecranon':'2U1',
  'olécranon':'2U1','cabeza radial':'2R1','hombro':'11','clavicula':'15','clavícula':'15',
  'escapula':'14','escápula':'14','acetabulo':'62','acetábulo':'62','pelvis':'61',
  'calcaneo':'82','calcáneo':'82','astragalo':'81','astrágalo':'81','rotula':'34','rótula':'34',
  'escafoides':'72'};
function sinTildes(s){ return String(s).toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,''); }
function construirIndice(){
  if(INDICE) return INDICE;
  INDICE=[];
  const p2=pasoDe(2); if(!p2) return INDICE;
  const decs={}; for(const d of p2.decisiones) decs[d.id]=d;
  const seg={}; for(const o of (decs.segmento||{opciones:[]}).opciones) seg[o.codigo]=o;
  for(const cod in (DATA.codigos||{})){
    const r=DATA.codigos[cod]; if(!r||!r.texto) continue;
    const base=cod.replace(/[A-Z].*$/,'').replace(/\\.$/,'');
    const s=seg[base]||seg[cod.slice(0,2)]||null;
    const region=s? s.etiqueta.replace(/^[^·]*·\\s*/,'') : '';
    INDICE.push({cod:cod, txt:r.texto, region:region,
                 busca:sinTildes(cod+' '+region+' '+r.texto)});
  }
  INDICE.sort((a,b)=>a.cod.length-b.cod.length||a.cod.localeCompare(b.cod));
  return INDICE;
}
function buscar(q){
  const caja=document.getElementById('bres'); if(!caja) return;
  const t=sinTildes(q).trim();
  if(t.length<2){ caja.innerHTML=''; caja.style.display='none'; return; }
  let clave=t;
  for(const k in SINONIMOS) if(t.indexOf(sinTildes(k))>=0){ clave=sinTildes(SINONIMOS[k]); break; }
  const idx=construirIndice();
  const exacto=[], empieza=[], contiene=[];
  for(const e of idx){
    const c=sinTildes(e.cod);
    if(c===clave||c===t) exacto.push(e);
    else if(c.indexOf(clave)===0||c.indexOf(t)===0) empieza.push(e);
    else if(e.busca.indexOf(t)>=0) contiene.push(e);
    if(exacto.length+empieza.length+contiene.length>400) break;
  }
  const res=exacto.concat(empieza,contiene).slice(0,25);
  caja.style.display='block';
  caja.innerHTML = res.length
    ? res.map(e=>{
        // en el segmento pelado, región y texto dicen lo mismo: sobra repetirlo
        const suelto=!/[A-Z]/.test(e.cod);
        const desc=suelto&&e.region? e.region : (e.region? e.region+' · '+e.txt : e.txt);
        return '<button onclick="irACodigo(\\''+e.cod+'\\')"><b>'+esc(e.cod)+'</b><span>'+esc(desc)+'</span></button>';
      }).join('')
    : '<p class="bnada">'+esc(TR('busca_nada',{q:q}))+'</p>';
}
function cerrarBusca(){ const c=document.getElementById('bres'); if(c){ c.innerHTML=''; c.style.display='none'; } }
/* Rellena las decisiones del Paso 2 hacia atrás desde un código completo. */
function irACodigo(cod){
  const p2=pasoDe(2); if(!p2) return;
  const decs={}; for(const d of p2.decisiones) decs[d.id]=d;
  const elige=(id,pred)=>{ const d=decs[id]; if(!d) return null;
    const o=d.opciones.find(pred); if(o){ S.porPaso[2]=S.porPaso[2]||{}; S.porPaso[2][id]=o.id; } return o; };
  const base=cod.replace(/([A-Z]).*$/,'');            // 42B2.1 → 42
  const m=cod.match(/([A-Z])([0-9])?(?:\\.([0-9]))?/); // tipo, grupo, subgrupo
  const segCod=base.replace(/\\.$/,'');
  S.porPaso[2]={};
  const s=elige('segmento',o=>o.codigo===segCod);
  if(s&&s.soloSi&&s.soloSi.hueso) S.porPaso[2].hueso=s.soloSi.hueso[0];
  if(m){
    elige('tipo',o=>o.codigo===m[1]&&(!o.soloSi||!o.soloSi.segmento||o.soloSi.segmento.indexOf(s&&s.id)>=0));
    if(m[2]) elige('grupo',o=>o.codigo===m[2]&&(!o.soloSi||!o.soloSi.tipo||o.soloSi.tipo.indexOf(S.porPaso[2].tipo)>=0));
    if(m[3]) elige('subgrupo',o=>o.codigo==='.'+m[3]&&(!o.soloSi||!o.soloSi.grupo||o.soloSi.grupo.indexOf(S.porPaso[2].grupo)>=0));
  }
  const caja=document.getElementById('bres'); if(caja){ caja.innerHTML=''; caja.style.display='none'; }
  const inp=document.getElementById('binput'); if(inp) inp.value='';
  guardar(); irPaso(2);
}

// Abre el desarrollo del paso, que es donde está el argumento largo de la alerta.
function porQue(){
  const d=document.getElementById('detdes'); if(!d) return;
  d.open=true; d.scrollIntoView({behavior:'smooth',block:'start'});
}

function pintarBarra(){
  const enResumen=S.vista!=='paso';
  const obl=P.decisiones.filter(d=>visible(d)&&!esMulti(d));
  const n=obl.length, hechas=obl.filter(d=>S.dec[d.id]).length;
  const conDecision=DISPONIBLES.filter(k=>Object.keys(S.porPaso[k]||{}).length).length;
  const caso = S.vista==='caso'? CASOS.find(x=>x.id===S.caso) : null;
  document.getElementById('prog').textContent =
      S.vista==='casos' ? (CASOS.length===1?TR('prog_biblioteca_1'):TR('prog_biblioteca_n',{n:CASOS.length}))
    : caso              ? TR('prog_caso',{region:caso.region})
    : S.vista==='resumen'? TR('prog_resumen',{a:conDecision,b:DISPONIBLES.length})
    : TR('prog_paso',{a:S.paso,b:DISPONIBLES.length,c:hechas,d:n});
  const bp=document.getElementById('bplan');
  bp.textContent = enResumen? TR('b_volver_paso') : TR('b_plan');
  bp.onclick = enResumen? verPaso : verResumen;
  const sig=document.getElementById('sig'), hay=!!DATA.pasos[S.paso+1];
  sig.textContent = hay? TR('b_paso_n',{n:S.paso+1}) : TR('b_ver_plan');
  sig.disabled = enResumen || (hay && hechas<n);
  sig.onclick = ()=> hay? irPaso(S.paso+1) : verResumen();
  const ant=document.getElementById('ant');
  ant.disabled = enResumen || !DATA.pasos[S.paso-1];
  ant.onclick = ()=>irPaso(S.paso-1);
  document.querySelectorAll('.pchip').forEach(c=>{
    const k=+c.dataset.n;
    c.classList.toggle('on',!enResumen&&k===S.paso);
    c.classList.toggle('hecho',Object.keys(S.porPaso[k]||{}).length>0);
  });
}

function pick(d,o){
  // Un caso guardado o un enlace antiguo pueden apuntar a una decisión que ya
  // no existe: se ignora en vez de romper la pantalla.
  const dec=P.decisiones.find(x=>x.id===d);
  if(!dec) return;
  if(esMulti(dec)){
    const a=S.dec[d]||[];
    S.dec[d]= a.includes(o)? a.filter(x=>x!==o) : a.concat([o]);
    if(!S.dec[d].length) delete S.dec[d];
  } else {
    S.dec[d]=(S.dec[d]===o)?undefined:o;
  }
  for(let i=0;i<3;i++){
    for(const dd of P.decisiones){
      const v=S.dec[dd.id]; if(!v) continue;
      if(!visible(dd)){ delete S.dec[dd.id]; continue; }
      if(Array.isArray(v)){
        const keep=v.filter(id=>{const op=dd.opciones.find(x=>x.id===id); return op&&(!op.soloSi||cumple(op.soloSi));});
        if(keep.length) S.dec[dd.id]=keep; else delete S.dec[dd.id];
      } else {
        const op=dd.opciones.find(x=>x.id===v);
        if(op&&op.soloSi&&!cumple(op.soloSi)) delete S.dec[dd.id];
      }
    }
  }
  guardar();
  render();
}
function verCrit(id){ S.verCrit[id]=!S.verCrit[id]; render(); }
function modo(m){ S.modo=m; guardar(); render(); window.scrollTo(0,0); }
function reiniciar(){
  const todo = hayCaso() && confirm(TR('confirm_borrar',{n:S.paso}));
  if(todo){ S.porPaso={}; S.paso=DISPONIBLES[0]; }
  S.porPaso[S.paso]={}; S.dec=S.porPaso[S.paso]; S.resp={};
  guardar(); irPaso(S.paso); window.scrollTo(0,0);
}

/* ------------------------------------------------------- plan consolidado
   Es el producto: las decisiones de los nueve pasos en un solo documento
   que se copia, se imprime y se pega en la historia. */
function planCompleto(){
  const out=[];
  for(const n of DISPONIBLES){
    const p=pasoDe(n), d=S.porPaso[n]||{};
    const filas=[];
    for(const dd of p.decisiones){
      const v=d[dd.id]; if(!v||(Array.isArray(v)&&!v.length)) continue;
      const et=Array.isArray(v)
        ? v.map(id=>{const o=dd.opciones.find(x=>x.id===id); return o?o.etiqueta:'';}).filter(Boolean).join(' · ')
        : (function(){const o=dd.opciones.find(x=>x.id===v); return o?o.etiqueta:'';})();
      if(et) filas.push({q:dd.pregunta,r:et});
    }
    // derivados y alertas se calculan en el contexto de ese paso
    const guardaP=P, guardaDec=S.dec, guardaPaso=S.paso;
    P=p; S.dec=d; S.paso=n;
    const der=derivados().map(x=>({t:x.titulo,p:x.principal,l:x.lineas||[]}));
    const crit=alertas().filter(a=>a.severidad==='critica'||a.severidad==='advertencia'||a.bloqueante);
    P=guardaP; S.dec=guardaDec; S.paso=guardaPaso;
    // Un paso al que no has entrado no debe aportar derivados ni, sobre todo,
    // alertas rojas: en un documento que se imprime eso es ruido alarmante.
    const tocado=filas.length>0;
    out.push({n:n,titulo:p.titulo,filas:filas,der:tocado?der:[],crit:tocado?crit:[],
              sintesis:p.sintesis,completo:tocado});
  }
  return out;
}
function planTexto(){
  const L=[TR('txt_plan_titulo'),
           TR('txt_generado',{fecha:new Date().toLocaleDateString(S.idioma,{day:'numeric',month:'long',year:'numeric'})}),''];
  for(const b of planCompleto()){
    if(!b.completo&&!b.der.length) continue;
    L.push(TR('paso').toUpperCase()+' '+b.n+' · '+b.titulo.toUpperCase());
    for(const f of b.filas) L.push('  · '+f.q+'  →  '+f.r);
    for(const x of b.der){ L.push('  ▸ '+x.t+': '+x.p); for(const y of x.l) L.push('      - '+y); }
    for(const a of b.crit) L.push('  [!] '+a.titulo+' — '+a.texto);
    L.push('');
  }
  L.push('—');
  L.push('Documento de apoyo metodológico. No sustituye el juicio del cirujano responsable.');
  return L.join('\\n');
}
function copiarPlan(){
  const t=planTexto();
  const ok=()=>{ const b=document.getElementById('bcopiar'); if(!b) return;
                 const x=b.textContent; b.textContent='Copiado'; setTimeout(()=>b.textContent=x,1600); };
  if(navigator.clipboard&&navigator.clipboard.writeText){ navigator.clipboard.writeText(t).then(ok,()=>caeAtras(t,ok)); }
  else caeAtras(t,ok);
}
function caeAtras(t,ok){
  const a=document.createElement('textarea'); a.value=t;
  a.style.position='fixed'; a.style.opacity='0'; document.body.appendChild(a); a.select();
  try{ document.execCommand('copy'); ok(); }catch(e){ alert('Copia manualmente:\\n\\n'+t); }
  document.body.removeChild(a);
}
function verResumen(){ S.vista='resumen'; render(); window.scrollTo(0,0); }
function verPaso(){ S.vista='paso'; render(); window.scrollTo(0,0); }

/* ------------------------------------------------------- casos por fallo
   Un caso no necesita motor propio: es un estado guardado con las decisiones
   equivocadas. El propio app dispara sus alertas y esas alertas SON la
   explicación del fallo. Después, el mismo caso con el estado corregido. */
const CASOS=DATA.casos||[];
function verCasos(){ S.vista='casos'; S.caso=null; render(); window.scrollTo(0,0); }
function verCaso(id){ S.vista='caso'; S.caso=id; render(); window.scrollTo(0,0); }

// Calcula las alertas de un estado cualquiera sin tocar el caso del usuario.
function alertasDe(estado, n){
  const gP=P, gDec=S.dec, gPaso=S.paso, gPorPaso=S.porPaso;
  S.porPaso={}; for(const k in estado) S.porPaso[k]=estado[k];
  P=pasoDe(n); S.dec=S.porPaso[n]||{}; S.paso=n;
  let out=[];
  try{ out=alertas().filter(a=>!a.siempre); }catch(e){}
  P=gP; S.dec=gDec; S.paso=gPaso; S.porPaso=gPorPaso;
  return out;
}
function cargarCaso(id, cual){
  const c=CASOS.find(x=>x.id===id); if(!c) return;
  const est = cual==='correcto'? c.estadoCorrecto : c.estadoError;
  S.porPaso={}; for(const k in est) S.porPaso[k]=JSON.parse(JSON.stringify(est[k]));
  S.vista='paso'; guardar(); irPaso(c.pasoClave||1);
}
function pintarCasos(){
  if(!CASOS.length) return '<div class="resumen"><h1>'+esc(TR('casos_h1_vacio'))+'</h1>'+
    '<p class="vacio">'+esc(TR('casos_vacio'))+'</p>'+
    '<div class="racc"><button onclick="verPaso()">Volver al Paso '+S.paso+'</button></div></div>';
  let h='<div class="resumen"><h1>'+esc(TR('casos_h1'))+'</h1>'+
    '<p class="sub">'+esc(TR('casos_sub'))+'</p>'+
    '<div class="racc"><button onclick="verPaso()">Volver al Paso '+S.paso+'</button></div>';
  for(const c of CASOS){
    const al=alertasDe(c.estadoError, c.pasoClave||3);
    // cuentan las críticas y las incoherencias: las dos son errores del plan
    const crit=al.filter(a=>a.severidad==='critica'||a.severidad==='advertencia').length;
    h+='<button class="ccard" onclick="verCaso(\\''+c.id+'\\')">'+
      '<div class="cmeta"><span class="creg">'+esc(c.region)+'</span>'+
      (crit?'<span class="ccrit">'+esc(crit===1?TR('caso_error_1'):TR('caso_error_n',{n:crit}))+'</span>':'')+
      '<span class="cmin">'+esc(String(c.minutos||4))+' min</span></div>'+
      '<b>'+esc(c.titulo)+'</b><p>'+esc(c.resumen)+'</p></button>';
  }
  h+='</div>';
  return h;
}
function pintarCaso(){
  const c=CASOS.find(x=>x.id===S.caso); if(!c) return pintarCasos();
  const al=alertasDe(c.estadoError, c.pasoClave||3);
  const alOK=alertasDe(c.estadoCorrecto, c.pasoClave||3);
  const ref=(c.refs||[]).map(id=>{const r=REFS[id]; if(!r) return ''; const u=urlRef(r);
    return u?'<a href="'+u+'" target="_blank" rel="noopener">'+esc(r.cita)+'</a>':esc(r.cita);}).filter(Boolean);
  return '<div class="resumen caso"><div class="racc"><button onclick="verCasos()">'+esc(TR('casos_todos'))+'</button></div>'+
    '<h1>'+esc(c.titulo)+'</h1><p class="sub">'+esc(c.region)+' · '+esc(TR('caso_minutos',{n:c.minutos||4}))+'</p>'+

    '<div class="rbloque"><h3><span>'+esc(TR('caso_b1'))+'</span></h3>'+
      '<p class="ctxt">'+esc(c.loQueSeHizo)+'</p>'+
      '<div class="racc"><button class="pri" onclick="cargarCaso(\\''+c.id+'\\',\\'error\\')">'+
      esc(TR('caso_cargar_error'))+'</button></div></div>'+

    '<div class="rbloque"><h3><span>'+esc(TR('caso_b2'))+'</span></h3>'+
      '<p class="ctxt">'+esc(TR('caso_b2_ctx'))+'</p>'+
      (al.length? al.map(a=>'<div class="alerta a-'+a.severidad+'"><b>'+esc(a.titulo)+'</b><p>'+esc(a.texto)+'</p></div>').join('')
                : '<p class="vacio">'+esc(TR('caso_sin_objecion'))+'</p>')+
      '</div>'+

    '<div class="rbloque"><h3><span>'+esc(TR('caso_b3'))+'</span></h3><p class="ctxt">'+esc(c.porQue)+'</p></div>'+

    '<div class="rbloque"><h3><span>'+esc(TR('caso_b4'))+'</span></h3><p class="ctxt">'+esc(c.loQueTocaba)+'</p>'+
      (alOK.length? '<p class="ctxt" style="margin-top:10px">'+esc(TR('caso_corregido_queda'))+'</p>'+
        alOK.map(a=>'<div class="alerta a-'+a.severidad+'"><b>'+esc(a.titulo)+'</b><p>'+esc(a.texto)+'</p></div>').join('')
        : '<p class="ctxt" style="margin-top:10px">'+esc(TR('caso_corregido_nada'))+'</p>')+
      '<div class="racc"><button class="pri" onclick="cargarCaso(\\''+c.id+'\\',\\'correcto\\')">'+
      esc(TR('caso_cargar_ok'))+'</button></div></div>'+

    '<div class="rec rec-regla"><b>'+esc(TR('caso_llevarse'))+'</b>'+esc(c.mensaje)+'</div>'+
    (ref.length?'<p class="ref">'+ref.join('<br>')+'</p>':'')+
    '</div>';
}

function pintarResumen(){
  const bloques=planCompleto();
  const hechos=bloques.filter(b=>b.completo).length;
  let h='<div class="resumen"><h1>'+esc(TR('plan_h1'))+'</h1>'+
    '<p class="sub">'+esc(TR('plan_sub',{a:hechos,b:DISPONIBLES.length}))+'</p>'+
    '<div class="racc"><button class="pri" id="bcopiar" onclick="copiarPlan()">'+esc(TR('b_copiar'))+'</button>'+
    '<button onclick="window.print()">'+esc(TR('b_imprimir'))+'</button>'+
    '<button onclick="verPaso()">Volver al Paso '+S.paso+'</button></div>';
  if(!hechos) h+='<p class="vacio" style="margin-top:20px">'+esc(TR('plan_vacio'))+'</p>';
  for(const b of bloques){
    if(!b.completo&&!b.der.length) continue;
    h+='<div class="rbloque"><h3><span>'+esc(TR('paso'))+' '+b.n+'</span> '+esc(b.titulo)+'</h3>';
    for(const f of b.filas) h+='<div class="prow"><span>'+esc(f.q)+'</span><span>'+esc(f.r)+'</span></div>';
    for(const x of b.der) h+='<div class="rder"><b>'+esc(x.t)+'</b><p>'+esc(x.p)+'</p>'+
      (x.l.length?'<ul>'+x.l.map(y=>'<li>'+esc(y)+'</li>').join('')+'</ul>':'')+'</div>';
    for(const a of b.crit) h+='<div class="alerta a-'+a.severidad+'"><b>'+esc(a.titulo)+'</b><p>'+esc(a.texto)+'</p></div>';
    h+='</div>';
  }
  const faltan=bloques.filter(b=>!b.completo).map(b=>b.n);
  if(faltan.length&&hechos) h+='<p class="vacio">'+esc(faltan.length===1
    ? TR('plan_faltan_1',{l:faltan.join(', ')}) : TR('plan_faltan_n',{l:faltan.join(', ')}))+'</p>';
  h+='</div>';
  return h;
}
function irPaso(n){
  if(!DATA.pasos[n]) return;
  S.paso=n; P=pasoDe(n); S.vista='paso';
  if(!S.porPaso[n]) S.porPaso[n]={};
  S.dec=S.porPaso[n]; S.resp={}; S.soloFallos=null;
  guardar(); cargar(); window.scrollTo(0,0);
}
function cargar(){
  // El NOMBRE del paso se traduce (es una etiqueta); el subtítulo y las
// preguntas no: eso es la voz del autor y espera a la Fase 2.
const tits=(IDIOMAS[S.idioma]||{}).pasos_titulos||[];
document.getElementById('titulo').textContent=
  TR('paso')+' '+P.numero+' · '+(tits[P.numero-1]||P.titulo);
  document.getElementById('subtitulo').textContent=P.subtitulo;
  document.getElementById('qkey').textContent=P.preguntaClave;
  document.getElementById('objetivos').innerHTML='<h2>'+esc(TR('objetivos_h2'))+'</h2><ul style="margin-left:18px;font-size:14px;line-height:1.75;color:var(--ink2)">'+
    P.objetivos.map(o=>'<li>'+esc(o)+'</li>').join('')+'</ul>';
  document.getElementById('desarrollo').innerHTML=P.esencial.map(bloque).join('');
  tiraPintar();   // el widget se monta después de que exista su contenedor
  document.getElementById('evid').innerHTML='<h2>'+esc(TR('evidencia_h2'))+'</h2>'+P.evidencia.map(e=>{
    const rr=(e.refs||[]).map(id=>{const r=REFS[id];if(!r)return '';const u=urlRef(r);
      return u?'<a href="'+u+'" target="_blank" rel="noopener">'+esc(r.cita)+'</a>':esc(r.cita);}).filter(Boolean);
    return '<div class="ev"><span class="niv">'+esc(TR('nivel'))+' '+esc(e.nivel)+'</span>'+esc(e.afirmacion)+
           (rr.length?'<div class="ref">'+rr.join('<br>')+'</div>':'')+'</div>';
  }).join('');
  document.querySelectorAll('.pchip').forEach(c=>{
    const n=+c.dataset.n;
    c.onclick=()=>irPaso(n);
  });
  pintarQ(); render();
}

/* ------------------------------------------------------------------ examen
   La autoevaluación puntúa, guarda historial y ofrece repasar lo fallado. */
function histQuiz(){
  try{ return JSON.parse(localStorage.getItem(CLAVE_Q)||'{}'); }catch(e){ return {}; }
}
function anotaQuiz(paso,i,bien){
  const h=histQuiz(); const k='p'+paso;
  h[k]=h[k]||{}; h[k][i]={bien:bien,cuando:Date.now()};
  try{ localStorage.setItem(CLAVE_Q,JSON.stringify(h)); }catch(e){}
}
function falladas(paso){
  const h=histQuiz()['p'+paso]||{};
  return Object.keys(h).filter(i=>!h[i].bien).map(Number);
}
function responder(i,j,btn){
  if(S.resp[i]!==undefined) return;
  S.resp[i]=j; const q=P.autoevaluacion[i], bien=(j===q.correcta);
  btn.parentNode.querySelectorAll('button').forEach((b,k)=>{
    if(k===q.correcta) b.classList.add('bien'); else if(k===j) b.classList.add('mal');
  });
  const e=document.createElement('div'); e.className='expl'; e.textContent=q.explicacion;
  btn.parentNode.appendChild(e);
  anotaQuiz(P.numero,i,bien);
  marcadorQuiz();
}
function marcadorQuiz(){
  const m=document.getElementById('qmarcador'); if(!m) return;
  const idx=Object.keys(S.resp).map(Number);
  const total=P.autoevaluacion.length;
  if(!idx.length){
    const f=falladas(P.numero);
    m.innerHTML = f.length
      ? '<button class="vermas" onclick="repasar()">'+esc(TR('quiz_repasar_n',{n:f.length}))+'</button>'
      : '<span class="qmini">'+total+' preguntas</span>';
    return;
  }
  const bien=idx.filter(i=>S.resp[i]===P.autoevaluacion[i].correcta).length;
  const pct=Math.round(bien*100/idx.length);
  m.innerHTML='<span class="qmini'+(pct>=70?' ok':' ko')+'">'+bien+' de '+idx.length+' · '+pct+'%</span>'+
    (idx.length===total? ' <button class="vermas" onclick="repasar()">'+esc(TR('quiz_repasar'))+'</button>':'');
}
function repasar(){
  const f=falladas(P.numero);
  S.soloFallos = f.length? f : null;
  S.resp={}; pintarQ();
  document.getElementById('quiz').scrollIntoView({behavior:'smooth',block:'start'});
}
function pintarQ(){
  const solo=S.soloFallos;
  const lista=P.autoevaluacion.map((q,i)=>({q:q,i:i})).filter(x=>!solo||solo.indexOf(x.i)>=0);
  document.getElementById('quiz').innerHTML = lista.length
    ? (solo?'<p class="ayuda">'+esc(TR('quiz_repaso_de',{n:lista.length}))+
             '<button class="vermas" onclick="S.soloFallos=null;S.resp={};pintarQ()">'+esc(TR('quiz_ver_todas'))+'</button></p>':'')+
      lista.map(x=>'<div class="q"><p>'+(x.i+1)+'. '+esc(x.q.pregunta)+'</p>'+
        x.q.opciones.map((o,j)=>'<button onclick="responder('+x.i+','+j+',this)">'+esc(o)+'</button>').join('')+'</div>').join('')
    : '<p class="vacio">'+esc(TR('quiz_sin_fallos'))+'</p>';
  marcadorQuiz();
}

/* El service worker es lo que permite usar el app sin conexión. Solo se puede
   registrar si la página se sirve por http(s): abierta como archivo suelto no
   hay ámbito donde hacerlo, y eso no es un fallo.
   Se registra de inmediato y no en el evento «load»: diferirlo hacía que en
   algunos navegadores no llegara a registrarse nunca. Y si falla, se dice por
   consola en vez de tragárselo, que fue lo que ocultó el problema. */
if('serviceWorker' in navigator && location.protocol.indexOf('http')===0){
  navigator.serviceWorker.register('sw.js').then(
    r=>{ S.sw=true; },
    e=>console.warn(TR('sw_sin_conexion'), e && e.message));
}

S.dec=S.porPaso[1]={};
const habiaCaso=restaurar();
if(!S.porPaso[S.paso]) S.porPaso[S.paso]={};

/* Idioma de arranque: primero lo que el usuario eligió la última vez; si no,
   el del navegador cuando lo tengamos; si no, español. */
(function(){
  let l=null;
  try{ l=localStorage.getItem(CLAVE_L); }catch(e){}
  if(!IDIOMAS[l]){
    const nav=(navigator.language||'es').slice(0,2).toLowerCase();
    l = IDIOMAS[nav] ? nav : 'es';
  }
  S.idioma=l;
  aplicarIdioma();
  P=pasoDe(S.paso);
})();

cargar();
if(habiaCaso) setTimeout(()=>{
  const b=document.getElementById('prog');
  if(b) b.insertAdjacentHTML('afterend','<span class="retomado">'+esc(TR('caso_recuperado'))+'</span>');
  setTimeout(()=>{const r=document.querySelector('.retomado'); if(r) r.remove();},4000);
},60);
"""


ICONO = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
<rect width="512" height="512" rx="104" fill="#185fa5"/>
<g stroke="#fff" stroke-width="30" stroke-linecap="round" fill="none">
  <path d="M196 96v120M316 96v120M196 416V296M316 416V296"/>
  <path d="M196 216h120M196 296h120"/>
</g>
<circle cx="256" cy="256" r="26" fill="#fff"/>
</svg>"""

SW = """/* Service worker de «I Need To Fix It».
   Estrategia: la app y sus figuras se guardan la primera vez y a partir de ahí
   se sirven del caché. Es lo que permite usarla en quirófano sin conexión. */
const CACHE='infi-v{v}';
// En el sitio publicado el app se llama index.html; prototipo.html solo existe
// en el repositorio. Y como addAll es atómico, basta con que uno de estos
// devuelva 404 para que la instalación entera falle y el modo sin conexión no
// llegue a funcionar nunca. Por eso se cachea uno a uno y se tolera el fallo.
const BASE=['./','./index.html','./manifest.webmanifest','./icono.svg'];

self.addEventListener('install',e=>{{
  e.waitUntil(
    caches.open(CACHE)
      .then(c=>Promise.all(BASE.map(u=>c.add(u).catch(err=>
        console.warn('[sw] no se pudo cachear',u,err&&err.message)))))
      .then(()=>self.skipWaiting()));
}});
self.addEventListener('activate',e=>{{
  e.waitUntil(caches.keys().then(ks=>Promise.all(
    ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));
}});
/* Dos estrategias, y la distinción importa.

   El APP (la navegación y el index.html) va a RED PRIMERO: si hay conexión se
   sirve la versión recién publicada y se guarda una copia; si no la hay, se
   sirve la copia guardada. Con caché primero, como estaba antes, el usuario se
   quedaba clavado en la versión que se descargó el primer día y ninguna
   corrección le llegaba nunca.

   Las FIGURAS del compendio van a CACHÉ PRIMERO: son 604 imágenes que no
   cambian, y volver a pedirlas por red sería tirar datos y batería. */
function esApp(req){{
  return req.mode==='navigate' ||
         req.url.indexOf('/index.html')>=0 ||
         req.url.replace(/[?#].*$/,'').endsWith('/');
}}
self.addEventListener('fetch',e=>{{
  if(e.request.method!=='GET') return;
  if(esApp(e.request)){{
    e.respondWith(
      fetch(e.request).then(res=>{{
        if(res && res.ok){{
          const copia=res.clone();
          caches.open(CACHE).then(c=>c.put('./index.html',copia));
        }}
        return res;
      }}).catch(()=>caches.match('./index.html').then(r=>r||caches.match('./')))
    );
    return;
  }}
  e.respondWith(
    caches.match(e.request).then(hit=>{{
      if(hit) return hit;
      return fetch(e.request).then(res=>{{
        if(res.ok && e.request.url.indexOf('/figuras/')>=0){{
          const copia=res.clone(); caches.open(CACHE).then(c=>c.put(e.request,copia));
        }}
        return res;
      }}).catch(()=>caches.match('./index.html').then(r=>r||caches.match('./')));
    }})
  );
}});
"""

MANIFEST = {
    "name": "I Need To Fix It — Los 10 pasos para resolver cualquier fractura",
    "short_name": "Fix It",
    "description": "Asistente metodológico de planificación quirúrgica en ortopedia y traumatología.",
    # En el sitio publicado el app se llama index.html; «prototipo.html» solo
    # existe en el repositorio. Apuntar aquí a prototipo.html hacía que el icono
    # de la pantalla de inicio abriera un 404 y que el modo sin conexión nunca
    # funcionara, porque el service worker guarda index.html y no ese nombre.
    "start_url": "./index.html",
    "scope": "./",
    "display": "standalone",
    "orientation": "portrait-primary",
    "background_color": "#faf9f7",
    "theme_color": "#185fa5",
    "lang": "es",
    "categories": ["medical", "education"],
    "icons": [
        {"src": "./icono.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any maskable"},
    ],
}


def escribir_pwa(version_cache: str):
    (RAIZ / "icono.svg").write_text(ICONO, encoding="utf-8")
    (RAIZ / "manifest.webmanifest").write_text(
        json.dumps(MANIFEST, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (RAIZ / "sw.js").write_text(SW.replace("{v}", version_cache), encoding="utf-8")


def main():
    pasos, refs, codigos, casos, idiomas, trad = cargar()
    hechos_v = sorted(pasos)
    version_txt = (f"Pasos {hechos_v[0]}-{hechos_v[-1]} de {len(TITULOS_10)}"
                   if hechos_v == list(range(hechos_v[0], hechos_v[-1] + 1))
                   else "Pasos " + ", ".join(map(str, hechos_v)))
    version_txt += " · " + MESES[FECHA.month - 1] + " de " + str(FECHA.year)
    data = json.dumps({"pasos": pasos, "refs": refs, "codigos": codigos, "casos": casos,
                       "idiomas": idiomas, "trad": trad, "version": version_txt},
                      ensure_ascii=False)
    data = data.replace("</", "<\\/")

    # Solo se muestran los pasos que existen: un chip que promete contenido
    # inexistente es peor que no mostrarlo.
    chips = "".join(
        f'<span class="pchip{" on" if i == 0 else ""}" data-n="{i+1}">{i+1}. {t}</span>'
        for i, t in enumerate(TITULOS_10) if (i + 1) in pasos
    )
    # El chip de casos va delante: al final de una fila que hace scroll no lo
    # encuentra nadie.
    if casos:
        chips = ('<span class="pchip casos" id="chipcasos" onclick="verCasos()">'
                 'Casos por fallo</span>') + chips
    version = version_txt
    # Un botón por idioma disponible: añadir uno más es editar interfaz.json.
    botones_idioma = []
    for k, v in idiomas.items():
        marcado = ' class="on"' if k == "es" else ''
        botones_idioma.append(
            '<button data-l="%s"%s onclick="idioma(\'%s\')" title="%s">%s</button>'
            % (k, marcado, k, v.get("_nombre", k), v.get("_etiqueta", k.upper())))
    sel_idioma = "".join(botones_idioma)

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>I Need To Fix It — Los 10 pasos para resolver cualquier fractura</title>
<meta name="description" content="Asistente metodológico de planificación quirúrgica en ortopedia y traumatología.">
<meta name="theme-color" content="#185fa5">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icono.svg" type="image/svg+xml">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Fix It">
<style>{CSS}</style>
</head>
<body>

<header>
  <div class="wrap">
    <div class="hrow">
      <div class="brand">I Need To Fix It<small>Los 10 pasos para resolver cualquier fractura</small></div>
      <div class="hder">
        <div class="idiomas">{sel_idioma}</div>
        <div class="modos">
          <button data-m="consulta" class="on" onclick="modo('consulta')">Consulta</button>
          <button data-m="estudio" onclick="modo('estudio')">Estudio</button>
        </div>
      </div>
    </div>
    <div class="pasos">{chips}</div>
  </div>
</header>

<div class="wrap"><p id="banner" class="banner oculto"></p></div>

<div class="wrap">
  <div id="vistaresumen" class="oculto"></div>

  <div id="vistapaso">
  <h1 id="titulo"></h1>
  <p class="sub" id="subtitulo"></p>
  <p class="qkey" id="qkey"></p>

  <div id="estudio" class="oculto"><section id="objetivos"></section></div>

  <div id="principio"></div>
  <div id="decs"></div>
  <div id="alerts"></div>
  <div class="plan" id="plan"></div>

  <section>
    <h2 id="desh">Desarrollo y tablas de referencia</h2>
    <details id="detdes"><summary id="dessum">Abrir el desarrollo completo del paso</summary><div class="dbody" id="desarrollo"></div></details>
  </section>

  <div id="estudio2" class="oculto">
    <section id="evid"></section>
    <section>
      <div class="qrow"><h2 id="quizh">Autoevaluación</h2><span id="qmarcador"></span></div>
      <div id="quiz"></div>
    </section>
  </div>
  </div>

  <p class="disc" id="aviso">
    <b>Aviso.</b> Prototipo con fines educativos y de apoyo metodológico. No constituye indicación clínica
    ni sustituye el juicio del cirujano responsable ni los protocolos de la institución. Contenido basado en
    el libro «Los 10 pasos para resolver cualquier fractura» y en el documento «Politrauma — Reanimación y
    Decisión Quirúrgica», ambos del Dr. Michael David Kushner Shrem. Versión de contenido: {version}.
    Clasificación AO/OTA 2018 reproducida con fines educativos.
  </p>
</div>

<div class="barra">
  <div class="in">
    <span style="font-size:13px;color:var(--ink3)" id="prog"></span>
    <span style="display:flex;gap:8px">
      <button id="ant">← Atrás</button>
      <button id="brei" onclick="reiniciar()">Reiniciar</button>
      <button id="bplan" onclick="verResumen()">Plan completo</button>
      <button class="pri" id="sig" disabled>Siguiente →</button>
    </span>
  </div>
</div>

<script>const DATA={data};</script>
<script>{JS}</script>
</body>
</html>
"""
    SALIDA.write_text(html, encoding="utf-8")
    # La versión del caché tiene que cambiar cuando cambia el CONTENIDO. Con la
    # fecha, dos publicaciones el mismo día generaban un sw.js idéntico, el
    # navegador no lo consideraba nuevo y el usuario se quedaba con la versión
    # antigua guardada. Con el hash del HTML, cualquier cambio invalida el caché.
    huella = hashlib.sha1(html.encode("utf-8")).hexdigest()[:10]
    escribir_pwa(FECHA.strftime("%Y%m%d") + "-" + huella)
    kb = SALIDA.stat().st_size / 1024
    print(f"Generado: {SALIDA}  ({kb:.0f} KB)")
    print(f"Pasos incrustados: {sorted(pasos)}")
    print(f"Referencias: {len(refs.get('referencias', {}))}")
    print("PWA: manifest.webmanifest · sw.js · icono.svg")


if __name__ == "__main__":
    main()
