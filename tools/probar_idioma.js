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

// 6 · la banda dice la verdad y desaparece sola cuando ya no hace falta
const textoBanner = vm.runInThisContext('textoBanner');
const pasosTraducidos = vm.runInThisContext('pasosTraducidos');
S.idioma = 'es';
ok('En español no se muestra ninguna banda', textoBanner() === '');
S.idioma = 'en';
const hechos = pasosTraducidos();
ok('La banda nombra los pasos ya traducidos',
   hechos.every(n => textoBanner().indexOf(String(n)) >= 0),
   hechos + ' → ' + textoBanner().slice(0, 90));
ok('La banda sigue avisando de que quedan pasos en español',
   /still in Spanish/.test(textoBanner()), textoBanner().slice(0, 60));

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

// 9 · el Paso 2 sí cambia de idioma: su vocabulario es el de la AO
const pasoDe = vm.runInThisContext('pasoDe');
const fusiona = vm.runInThisContext('fusiona');

// la fusión respeta la forma y empareja por id, no por posición
const probaFus = fusiona(
  { a: 'uno', lista: [{ id: 'x', t: 'equis' }, { id: 'y', t: 'ye' }], intacto: 'igual' },
  { a: 'one', lista: [{ id: 'y', t: 'why' }] });
ok('La fusión traduce el campo suelto', probaFus.a === 'one', probaFus.a);
ok('La fusión empareja por id, no por posición',
   probaFus.lista[0].t === 'equis' && probaFus.lista[1].t === 'why',
   JSON.stringify(probaFus.lista));
ok('La fusión deja intacto lo que no se tradujo', probaFus.intacto === 'igual');

S.idioma = 'es'; const p2es = pasoDe(2);
S.idioma = 'en'; const p2en = pasoDe(2);
const dh = id => p2en.decisiones.find(d => d.id === id);
ok('«Which bone?» en inglés', dh('hueso').pregunta === 'Which bone?', dh('hueso').pregunta);
ok('El hueso se traduce', dh('hueso').opciones[0].etiqueta.indexOf('Humerus') >= 0,
   dh('hueso').opciones[0].etiqueta);
ok('El segmento viene del compendio AO',
   dh('segmento').opciones[0].etiqueta.indexOf('Humerus') >= 0,
   dh('segmento').opciones[0].etiqueta);
ok('Las clasificaciones regionales se traducen',
   /split/i.test(dh('cl-schatzker').opciones[0].etiqueta),
   dh('cl-schatzker').opciones[0].etiqueta);
ok('Los cuadrantes de Kfuri son cuatro y en inglés',
   dh('cl-columnas').opciones.length === 4 &&
   dh('cl-columnas').opciones.map(o => o.etiqueta).join(',') ===
     'Anterolateral,Anteromedial,Posterolateral,Posteromedial',
   dh('cl-columnas').opciones.map(o => o.etiqueta).join(','));
ok('El español queda intacto tras fundir',
   p2es.decisiones.find(d => d.id === 'hueso').pregunta === '¿Qué hueso?',
   p2es.decisiones.find(d => d.id === 'hueso').pregunta);

// lo estructural no necesita traducción y debe quedarse como está
ok('Los códigos de tipo/grupo no se tocan',
   dh('tipo').opciones[0].etiqueta === p2es.decisiones.find(d => d.id === 'tipo').opciones[0].etiqueta,
   dh('tipo').opciones[0].etiqueta);

// 10 · cada paso traducido, revisado entero: ni un resto de español
const esEspanol = s => /[áéíóúñ¿¡]|\b(el|la|los|las|que|con|para|una|del|sin|por)\b/i.test(String(s || ''));
S.idioma = 'en';
for (const n of pasosTraducidos()) {
  const p = pasoDe(n);
  const restos = [];
  for (const campo of ['titulo', 'subtitulo', 'preguntaClave', 'sintesis'])
    if (esEspanol(p[campo])) restos.push(campo);
  for (const o of (p.objetivos || [])) if (esEspanol(o)) restos.push('objetivo');
  for (const d of (p.decisiones || [])) {
    if (esEspanol(d.pregunta)) restos.push('pregunta: ' + d.pregunta.slice(0, 30));
    if (esEspanol(d.ayuda)) restos.push('ayuda de ' + d.id);
    for (const o of d.opciones) {
      if (esEspanol(o.etiqueta)) restos.push('opción: ' + o.etiqueta.slice(0, 30));
      for (const c of (o.criterios || [])) if (esEspanol(c)) restos.push('criterio: ' + c.slice(0, 30));
    }
  }
  for (const a of (p.alertas || [])) {
    if (esEspanol(a.titulo)) restos.push('alerta: ' + a.titulo.slice(0, 30));
    if (esEspanol(a.texto)) restos.push('texto de ' + a.id);
  }
  for (const r of (p.reglasCoherencia || [])) if (esEspanol(r.mensaje)) restos.push('regla ' + r.id);
  for (const dv of (p.derivados || []))
    for (const rg of (dv.reglas || [])) if (esEspanol(rg.texto)) restos.push('derivado ' + dv.id);
  for (const b of (p.esencial || [])) {
    if (esEspanol(b.texto)) restos.push('bloque: ' + String(b.texto).slice(0, 30));
    if (esEspanol(b.titulo)) restos.push('título de bloque');
    for (const fila of (b.filas || [])) for (const c of fila) if (esEspanol(c)) restos.push('celda: ' + c.slice(0, 30));
    for (const h of (b.encabezados || [])) if (esEspanol(h)) restos.push('encabezado: ' + h);
  }
  for (const q of (p.autoevaluacion || [])) {
    if (esEspanol(q.pregunta)) restos.push('quiz: ' + q.pregunta.slice(0, 30));
    for (const o of q.opciones) if (esEspanol(o)) restos.push('quiz opción: ' + o.slice(0, 30));
    if (esEspanol(q.explicacion)) restos.push('quiz explicación');
  }
  for (const e of (p.evidencia || [])) if (esEspanol(e.afirmacion)) restos.push('evidencia');
  ok('Paso ' + n + ' sin restos de español', restos.length === 0,
     restos.length + ': ' + restos.slice(0, 3).join(' | '));
  // el español original no se toca
  S.idioma = 'es';
  ok('Paso ' + n + ' en español intacto', esEspanol(pasoDe(n).titulo), pasoDe(n).titulo);
  S.idioma = 'en';
}

// y lo que NO debe cambiar, no cambia
S.idioma = 'en';
ok('El Paso 1 sigue en español (Fase 2 pendiente)',
   esEspanol(pasoDe(1).decisiones[0].pregunta),
   pasoDe(1).decisiones[0].pregunta.slice(0, 40));

console.log('\n' + '='.repeat(58));
console.log(fallos ? `${fallos} comprobación(es) fallida(s)` : 'Bilingüe correcto: la Fase 1 hace lo que dice');
process.exit(fallos ? 1 : 0);
