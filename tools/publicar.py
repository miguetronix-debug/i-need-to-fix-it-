#!/usr/bin/env python3
"""
publicar.py — Arma la carpeta «sitio/», que es lo único que se publica.

El repositorio contiene también las herramientas, el contenido en JSON y los
documentos internos de trabajo. Nada de eso tiene que acabar en internet, así
que el sitio se construye aparte y solo con lo que el navegador necesita:

    sitio/
      index.html              el app entero
      manifest.webmanifest    para que se instale
      sw.js                   para que funcione sin conexión
      icono.svg
      robots.txt
      content/figuras/        las 506 figuras recortadas y las 98 láminas

Uso:  python3 tools/build_prototipo.py && python3 tools/publicar.py
"""

import shutil
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SITIO = RAIZ / "sitio"

ROBOTS = """User-agent: *
Allow: /
"""

# Lo mismo que vercel.json, en el formato que entiende Netlify. Hace falta
# sobre todo por el manifest: Netlify lo sirve como application/octet-stream y
# con ese tipo algunos navegadores se niegan a instalar la app.
HEADERS = """# manifest.webmanifest tiene que llegar con su tipo propio: si el servidor lo
# manda como application/octet-stream, algunos navegadores se niegan a instalar
# la app. Netlify lee este archivo; Vercel lee vercel.json, que dice lo mismo.

/manifest.webmanifest
  Content-Type: application/manifest+json; charset=utf-8

# Las figuras nunca cambian: caché de un año.
/content/figuras/*
  Cache-Control: public, max-age=31536000, immutable

# El HTML y el service worker sí cambian: nunca en caché, o el usuario se queda
# con una versión vieja y no hay forma de actualizarlo.
/index.html
  Cache-Control: no-cache

/sw.js
  Cache-Control: no-cache
"""

# Vercel y Netlify sirven estáticos sin configuración; esto solo añade caché
# larga para las figuras, que no cambian nunca, y ninguna para el HTML.
VERCEL = """{
  "cleanUrls": false,
  "rewrites": [
    { "source": "/", "destination": "/index.html" }
  ],
  "headers": [
    {
      "source": "/",
      "headers": [{ "key": "Cache-Control", "value": "no-cache" }]
    },
    {
      "source": "/content/figuras/(.*)",
      "headers": [{ "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }]
    },
    {
      "source": "/sw.js",
      "headers": [{ "key": "Cache-Control", "value": "no-cache" }]
    },
    {
      "source": "/index.html",
      "headers": [{ "key": "Cache-Control", "value": "no-cache" }]
    }
  ]
}
"""


def main():
    if not (RAIZ / "prototipo.html").exists():
        raise SystemExit("Falta prototipo.html: ejecuta antes tools/build_prototipo.py")

    # se sobrescribe en lugar de borrar y rehacer: en algunas carpetas
    # sincronizadas el borrado no está permitido y no hace falta.
    SITIO.mkdir(exist_ok=True)

    # el app, con el nombre que espera cualquier servidor estático
    shutil.copy(RAIZ / "prototipo.html", SITIO / "index.html")
    for f in ("manifest.webmanifest", "sw.js", "icono.svg"):
        shutil.copy(RAIZ / f, SITIO / f)

    destino = SITIO / "content" / "figuras"
    shutil.copytree(RAIZ / "content" / "figuras", destino, dirs_exist_ok=True)

    (SITIO / "robots.txt").write_text(ROBOTS, encoding="utf-8")
    (SITIO / "vercel.json").write_text(VERCEL, encoding="utf-8")
    (SITIO / "_headers").write_text(HEADERS, encoding="utf-8")

    archivos = sum(1 for _ in SITIO.rglob("*") if _.is_file())
    peso = sum(f.stat().st_size for f in SITIO.rglob("*") if f.is_file()) / 1024 / 1024
    print(f"sitio/ listo · {archivos} archivos · {peso:.1f} MB")
    print("   index.html · manifest.webmanifest · sw.js · icono.svg · robots.txt · vercel.json")
    print(f"   content/figuras: {sum(1 for _ in destino.rglob('*.jpg'))} imágenes")


if __name__ == "__main__":
    main()
