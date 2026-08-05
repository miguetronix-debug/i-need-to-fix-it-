// probar_sw.js — Vigila el service worker, que es lo único del app capaz de
// dejar a un usuario clavado en una versión antigua sin que nadie se entere.
//
// El fallo que motivó esta prueba: la versión del caché era la FECHA, así que
// dos publicaciones el mismo día generaban un sw.js idéntico; el navegador no
// lo veía como nuevo, y el usuario seguía viendo el app de la primera visita.
// Michael lo detectó porque el Paso 7 le seguía saliendo en español después de
// haberlo traducido y publicado.
//
// Lo que comprueba:
//   · que la versión del caché dependa del CONTENIDO y no solo de la fecha,
//   · que dos contenidos distintos den versiones de caché distintas,
//   · que el app se sirva a RED PRIMERO, para que las correcciones lleguen,
//   · que las figuras sigan a CACHÉ PRIMERO, que es lo que da el modo avión,
//   · y que el sw.js publicado sea JavaScript válido.
//
// Uso:  node tools/probar_sw.js

'use strict';
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const RAIZ = path.resolve(__dirname, '..');
const SW = path.join(RAIZ, 'sitio', 'sw.js');

let fallos = 0;
function ok(nombre, cond, detalle) {
  console.log((cond ? '  ok    ' : '  FALLA ') + nombre + (cond || !detalle ? '' : ' → ' + detalle));
  if (!cond) fallos++;
}

const sw = fs.readFileSync(SW, 'utf8');

// 1 · sintaxis
let valido = true;
try { new Function(sw); } catch (e) { valido = false; }
ok('El service worker es JavaScript válido', valido);

// 2 · la versión del caché lleva huella de contenido, no solo la fecha
const m = sw.match(/const CACHE='([^']+)'/);
ok('El service worker declara una versión de caché', !!m, m && m[1]);
if (m) {
  const v = m[1];
  ok('La versión del caché lleva huella del contenido, no solo la fecha',
     /^infi-v\d{8}-[0-9a-f]{6,}$/.test(v),
     v + '  ← con solo la fecha, dos publicaciones el mismo día no invalidan nada');
}

// 3 · dos contenidos distintos tienen que dar versiones distintas
const antes = m ? m[1] : null;
const paso7 = path.join(RAIZ, 'content', 'traducciones', '07-en.json');
const copia = fs.readFileSync(paso7, 'utf8');
try {
  const tocado = JSON.parse(copia);
  tocado._prueba_marca = 'cambio artificial para comprobar la huella';
  fs.writeFileSync(paso7, JSON.stringify(tocado, null, 2) + '\n');
  execFileSync('python3', [path.join(RAIZ, 'tools', 'build_prototipo.py')], { stdio: 'ignore' });
  execFileSync('python3', [path.join(RAIZ, 'tools', 'publicar.py')], { stdio: 'ignore' });
  const despues = (fs.readFileSync(SW, 'utf8').match(/const CACHE='([^']+)'/) || [])[1];
  ok('Cambiar el contenido cambia la versión del caché', antes !== despues,
     antes + ' → ' + despues);
} finally {
  fs.writeFileSync(paso7, copia);
  execFileSync('python3', [path.join(RAIZ, 'tools', 'build_prototipo.py')], { stdio: 'ignore' });
  execFileSync('python3', [path.join(RAIZ, 'tools', 'publicar.py')], { stdio: 'ignore' });
}

const swFinal = fs.readFileSync(SW, 'utf8');

// 4 · el app a red primero; las figuras a caché primero
ok('El app se pide a la red antes que al caché',
   /esApp\(e\.request\)/.test(swFinal) && /if\(esApp[\s\S]{0,200}fetch\(e\.request\)/.test(swFinal),
   'sin esto, una corrección publicada no le llega nunca a quien ya abrió el app');
ok('Sin conexión, el app cae en la copia guardada',
   /catch\(\(\)=>caches\.match\('\.\/index\.html'\)/.test(swFinal));
ok('Las figuras siguen sirviéndose del caché primero',
   /figuras\/'\)>=0/.test(swFinal) && /caches\.match\(e\.request\)\.then\(hit=>/.test(swFinal),
   'son 604 imágenes que no cambian: pedirlas por red gastaría datos sin motivo');

// 5 · la instalación tiene que tolerar que falte un recurso
ok('La instalación tolera que un recurso falle',
   /c\.add\(u\)\.catch\(/.test(swFinal),
   'addAll es atómico: un solo 404 dejaría el modo sin conexión sin instalar');
ok('El service worker nuevo toma el control sin esperar',
   /skipWaiting/.test(swFinal) && /clients\.claim/.test(swFinal));
ok('Los cachés antiguos se borran al activar',
   /caches\.delete\(k\)/.test(swFinal));

console.log('\n' + '='.repeat(58));
console.log(fallos ? `${fallos} comprobación(es) fallida(s)`
                   : 'Service worker correcto: las correcciones llegarán al usuario');
process.exit(fallos ? 1 : 0);
