// probar_idioma.js — Comprueba la Fase 1 del bilingüe.
//
// Lo que vigila:
//   · que TR() devuelva la cadena del idioma activo,
//   · que una clave ausente en inglés caiga al español en vez de escribir
//     «undefined» en la pantalla,
//   · que los huecos {a} {b} {n} se rellenen,
//   · que el compendio AO sirva el inglés ORIGINAL cuando el idioma es EN,
//   · que ninguna clave del español se haya quedado sin pareja en inglés,
//   · y que el idioma elegido sobreviva a un cierre del navegador.
//
// Uso:  node tools/probar_idioma.js

'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const RAIZ = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(RAIZ, 'prototipo.html'), 'utf8');
const bloques = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);

const noop = () => {};
const nodo = () => ({ innerHTML: '', textContent: '', value: '', style: {}, lang: '',
  classList: { add: noop, remove: noop, toggle: noop }, getAttribute: () => null,
  setAttribute: noop, appendChild: noop, addEventListener: noop,
  insertAdjacentHTML: noop, querySelector: () => nodo(), querySelectorAll: () => [] });
global.document = { getElementById: () => nodo(), querySelector: () => nodo(),
  querySelectorAll: () => [], createElement: () => nodo(), addEventListener: noop,
  body: nodo(), documentElement: nodo(), title: '' };
global.window = { scrollTo: noop, addEventListener: noop, print: noop,
  matchMedia: () => ({ matches: false, addListener: noop }) };
const mem = {};
global.localStorage = { getItem: k => (k in mem ? mem[k] : null),
  setItem: (k, v) => { mem[k] = String(v); }, removeItem: k => { delete mem[k]; } };
global.location = { hash: '', pathname: '/x.html', search: '' };
global.history = { replaceState: noop };
Object.defineProperty(global, 'navigator', { value: { language: 'en-GB' },
  configurable: true, writable: true });

for (const b of bloques) {
  try { vm.runInThisContext(b); } catch (e) { /* el render sin DOM real puede quejarse */ }
}
const TR = vm.runInThisContext('TR');
const S = vm.runInThisContext('S');
const DATA = vm.runInThisContext('DATA');
const IDIOMAS = vm.runInThisContext('IDIOMAS');
const txtDe = vm.runInThisContext('txtDe');
const aplicarIdioma = vm.runInThisContext('aplicarIdioma');

let fallos = 0;
function ok(nombre, cond, detalle) {
  console.log((cond ? '  ok    ' : '  FALLA ') + nombre + (cond || !detalle ? '' : ' → ' + detalle));
  if (!cond) fallos++;
}

console.log('\nIdiomas disponibles: ' + Object.keys(IDIOMAS).join(', ') + '\n');

// 1 · cada idioma devuelve lo suyo
S.idioma = 'es';
const planEs = TR('b_plan');
S.idioma = 'en';
const planEn = TR('b_plan');
ok('Cada idioma devuelve su propia cadena', planEs !== planEn, planEs + ' / ' + planEn);
ok('El español dice «Plan completo»', planEs === 'Plan completo', planEs);
ok('El inglés dice «Full plan»', planEn === 'Full plan', planEn);

// 2 · huecos
S.idioma = 'es';
const prog = TR('prog_paso', { a: 3, b: 10, c: 2, d: 5 });
ok('Los huecos se rellenan', prog === 'Paso 3 de 10 · 2 de 5 decisiones', prog);
ok('No queda ningún hueco sin rellenar', prog.indexOf('{') < 0, prog);

// 3 · una clave inexistente no escribe «undefined»
const inventada = TR('clave_que_no_existe_en_ningun_idioma');
ok('Una clave inexistente devuelve la clave, no «undefined»',
   inventada === 'clave_que_no_existe_en_ningun_idioma', inventada);

// 4 · ninguna clave del español sin pareja en inglés
const es = IDIOMAS.es || {}, en = IDIOMAS.en || {};
const huerfanas = Object.keys(es).filter(k => !k.startsWith('_') && k !== 'banner_es'
                                          && (en[k] === undefined || en[k] === ''));
ok('Ninguna cadena se quedó sin traducir', huerfanas.length === 0,
   huerfanas.length + ' sin pareja: ' + huerfanas.slice(0, 6).join(', '));

// y al revés: nada sobrante en inglés que ya no exista en español
const sobrantes = Object.keys(en).filter(k => !k.startsWith('_') && es[k] === undefined);
ok('No hay cadenas inglesas huérfanas', sobrantes.length === 0, sobrantes.join(', '));

// 5 · el compendio AO sirve el inglés original, que NO es traducción nuestra
const conIngles = Object.keys(DATA.codigos).filter(c => DATA.codigos[c].en);
ok('El compendio conserva su inglés original', conIngles.length > 500,
   conIngles.length + ' códigos con texto en inglés');
if (conIngles.length) {
  const c = conIngles[0];
  S.idioma = 'es'; const tEs = txtDe(c);
  S.idioma = 'en'; const tEn = txtDe(c);
  ok('En inglés el compendio cambia de idioma', tEs !== tEn, c + ': ' + tEs + ' / ' + tEn);
  ok('El inglés del compendio es el del documento AO',
     tEn === DATA.codigos[c].en, c);
}

// 6 · el aviso de que lo clínico sigue en español solo aparece en inglés
S.idioma = 'es';
ok('En español no se muestra la banda de aviso', TR('banner_es') === '');
S.idioma = 'en';
ok('En inglés sí se avisa de que lo clínico sigue en español',
   TR('banner_es').length > 40);

// 7 · el idioma elegido sobrevive
S.idioma = 'es';
vm.runInThisContext('idioma')('en');
ok('El idioma queda guardado', localStorage.getItem('infi-idioma-v1') === 'en',
   String(localStorage.getItem('infi-idioma-v1')));
ok('El atributo lang del documento se actualiza',
   document.documentElement.lang === 'en', document.documentElement.lang);

// 8 · el contenido clínico NO se tradujo: sigue en español, y eso es lo esperado
const p1 = DATA.pasos[1];
ok('El contenido clínico sigue en español (Fase 2 pendiente)',
   /[áéíóúñ¿]/.test(p1.decisiones[0].pregunta), p1.decisiones[0].pregunta.slice(0, 40));

console.log('\n' + '='.repeat(58));
console.log(fallos ? `${fallos} comprobación(es) fallida(s)` : 'Bilingüe correcto: la Fase 1 hace lo que dice');
process.exit(fallos ? 1 : 0);
