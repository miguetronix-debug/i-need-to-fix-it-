// probar_casos.js — Recorre la biblioteca de casos por fallo tal como la usa
// alguien con el móvil en la mano: pulsar el chip, abrir un caso, cargar el
// plan equivocado y después el corregido.
//
// Existe porque `probar.js` comprueba la lógica de cada caso pero nunca el
// RECORRIDO: que la lista pinte tarjetas, que el detalle traiga sus cuatro
// bloques, y que los dos botones de carga dejen el app en el paso correcto.
//
// El invariante que de verdad importa está al final: el plan corregido de cada
// caso NO debe dejar alertas críticas. Si alguna aparece, o el caso está mal
// escrito o el motor penaliza una práctica correcta.
//
// Uso:  node tools/probar_casos.js

'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const RAIZ = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(RAIZ, 'prototipo.html'), 'utf8');
const bloques = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);

const cache = {};
const noop = () => {};
const nodo = id => (cache[id] = cache[id] || {
  id, innerHTML: '', textContent: '', value: '', style: {}, lang: '',
  classList: { add: noop, remove: noop, toggle: noop },
  getAttribute: () => null, setAttribute: noop, appendChild: noop,
  addEventListener: noop, insertAdjacentHTML: noop,
  querySelector: () => nodo('x'), querySelectorAll: () => [],
});
// Chips simulados como en el HTML: los diez de paso llevan data-n; el de casos
// NO, y su único enlace con la lógica es el onclick que trae de fábrica.
const chipCasos = nodo('chipcasos');
chipCasos.dataset = {};
chipCasos.onclick = () => vm.runInThisContext('verCasos')();
const chipsPaso = [];
for (let n = 1; n <= 10; n++) {
  const c = nodo('pchip-' + n);
  c.dataset = { n: String(n) };
  chipsPaso.push(c);
}
const TODOS = [chipCasos].concat(chipsPaso);

global.document = {
  getElementById: id => nodo(id), querySelector: () => nodo('q'),
  // el selector importa: «.pchip» los devuelve todos, «.pchip[data-n]» solo los
  // de paso. Ese matiz es exactamente el que provocó el fallo.
  querySelectorAll: sel => sel === '.pchip' ? TODOS
                         : sel === '.pchip[data-n]' ? chipsPaso : [],
  createElement: () => nodo('n'),
  addEventListener: noop, body: nodo('body'), documentElement: nodo('html'), title: '',
};
global.window = { scrollTo: noop, addEventListener: noop, print: noop,
  matchMedia: () => ({ matches: false, addListener: noop }) };
const mem = {};
global.localStorage = { getItem: k => (k in mem ? mem[k] : null),
  setItem: (k, v) => { mem[k] = String(v); }, removeItem: noop };
global.location = { hash: '', pathname: '/x.html', search: '' };
global.history = { replaceState: noop };
Object.defineProperty(global, 'navigator', { value: {}, configurable: true, writable: true });

for (const b of bloques) {
  try { vm.runInThisContext(b); } catch (e) { /* el render sin DOM real puede quejarse */ }
}
const S = vm.runInThisContext('S');
const CASOS = vm.runInThisContext('CASOS');
const verCasos = vm.runInThisContext('verCasos');
const verCaso = vm.runInThisContext('verCaso');
const cargarCaso = vm.runInThisContext('cargarCaso');
const alertas = vm.runInThisContext('alertas');
const pintarCasos = vm.runInThisContext('pintarCasos');
const pintarCaso = vm.runInThisContext('pintarCaso');

let fallos = 0;
function ok(nombre, cond, detalle) {
  console.log((cond ? '  ok    ' : '  FALLA ') + nombre + (cond || !detalle ? '' : ' → ' + detalle));
  if (!cond) fallos++;
}

console.log('\nBiblioteca: ' + CASOS.length + ' casos\n');

// 0 · EL FALLO QUE MOTIVÓ ESTA PRUEBA
// El chip de casos comparte la clase .pchip con los de paso pero no lleva
// data-n. Con el selector amplio, el render le asignaba onclick=()=>irPaso(NaN)
// y su verCasos() desaparecía: al pulsarlo no ocurría nada. Aquí se PULSA el
// chip, no se llama a la función, que es lo único que lo detecta.
vm.runInThisContext('irPaso')(5);          // fuerza un render completo
S.vista = 'paso';
chipCasos.onclick();
ok('Pulsar el chip de casos lleva a la biblioteca (no lo pisa el render)',
   S.vista === 'casos',
   'vista = ' + S.vista + ' · si es «paso», el render le borró el onclick');

const chip3 = chipsPaso[2];
chip3.onclick();
ok('Los chips de paso siguen funcionando', S.paso === 3, 'paso ' + S.paso);

// 1 · la vista de la biblioteca
verCasos();
ok('Pulsar el chip lleva a la biblioteca', S.vista === 'casos', S.vista);
const lista = pintarCasos();
const tarjetas = (lista.match(/class="ccard"/g) || []).length;
ok('La lista pinta una tarjeta por caso', tarjetas === CASOS.length,
   tarjetas + ' tarjetas para ' + CASOS.length + ' casos');
ok('Cada tarjeta se puede pulsar', (lista.match(/onclick="verCaso\(/g) || []).length === CASOS.length);

// 2 · abrir cada caso y comprobar que trae sus cuatro bloques
for (const c of CASOS) {
  verCaso(c.id);
  const det = pintarCaso();
  const b = (det.match(/rbloque/g) || []).length;
  ok('Caso «' + c.id + '» abre con sus cuatro bloques', b === 4, b + ' bloques');
}

// 3 · los dos botones de carga
const uno = CASOS[0];
cargarCaso(uno.id, 'error');
ok('«Cargar estas decisiones» vuelve a la vista de paso', S.vista === 'paso', S.vista);
ok('…y deja el app en el paso clave del caso', S.paso === (uno.pasoClave || 1),
   'paso ' + S.paso + ', esperado ' + (uno.pasoClave || 1));
const conDecisiones = Object.keys(S.porPaso).filter(k => Object.keys(S.porPaso[k] || {}).length);
ok('…con las decisiones del plan equivocado puestas', conDecisiones.length > 0,
   'pasos con decisiones: ' + conDecisiones.join(', '));

// 4 · el invariante: el plan equivocado grita, el corregido calla
console.log('\nEl motor frente a cada caso:');
for (const c of CASOS) {
  cargarCaso(c.id, 'error');
  const mal = alertas().filter(a => a.severidad === 'critica' || a.severidad === 'alta').length;
  cargarCaso(c.id, 'correcto');
  const bien = alertas().filter(a => a.severidad === 'critica').length;
  console.log('  ' + (c.id + ' ').padEnd(34, '·') +
              ' plan malo: ' + String(mal).padStart(2) + ' avisos graves' +
              ' · plan corregido: ' + bien + ' críticas');
  if (mal === 0) { console.log('    FALLA: el plan equivocado no dispara ninguna alerta grave'); fallos++; }
  if (bien > 0)  { console.log('    FALLA: el plan corregido deja alertas críticas'); fallos++; }
}

console.log('\n' + '='.repeat(58));
console.log(fallos ? `${fallos} comprobación(es) fallida(s)`
                   : 'Casos por fallo: el recorrido completo funciona');
process.exit(fallos ? 1 : 0);
