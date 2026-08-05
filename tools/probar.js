// probar.js — Ejecuta el motor del prototipo fuera del navegador y comprueba
// que, ante un caso clínico concreto, salen las alertas y los derivados que
// deben salir. Es la red de seguridad de la lógica de decisión.
//
// Uso:  node tools/probar.js
'use strict';
const fs = require('fs');
const path = require('path');

const RAIZ = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(RAIZ, 'prototipo.html'), 'utf8');

// El prototipo trae dos bloques <script>: los datos y el motor.
const bloques = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
if (!bloques.length) throw new Error('No encontré ningún <script> en prototipo.html');

// Stubs mínimos de DOM para poder evaluar el motor sin navegador.
const noop = () => {};
const nodo = () => ({ innerHTML: '', textContent: '', value: '', style: {}, classList: { add: noop, remove: noop, toggle: noop },
  appendChild: noop, addEventListener: noop, setAttribute: noop, querySelector: () => nodo(), querySelectorAll: () => [] });
global.document = { getElementById: () => nodo(), querySelector: () => nodo(), querySelectorAll: () => [],
  createElement: () => nodo(), addEventListener: noop, body: nodo() };
global.window = { scrollTo: noop, addEventListener: noop, matchMedia: () => ({ matches: false, addListener: noop }) };
const _mem = {};
global.localStorage = { getItem: k => (k in _mem ? _mem[k] : null), setItem: (k, v) => { _mem[k] = String(v); }, removeItem: k => { delete _mem[k]; } };
global.location = { hash: '', pathname: '/x.html', search: '' };
global.history = { replaceState: (a, b, url) => { const i = String(url).indexOf('#'); global.location.hash = i >= 0 ? String(url).slice(i) : ''; } };
Object.defineProperty(global, 'navigator', { value: {}, configurable: true, writable: true });

// runInThisContext, y no eval, porque las declaraciones const del prototipo
// tienen que quedar en el ámbito léxico global para verse desde aquí.
const vm = require('vm');
for (const b of bloques) {
  try { vm.runInThisContext(b); } catch (e) { /* el render puede fallar sin DOM real: da igual */ }
}
// Puentes al ámbito léxico global (const/let no cuelgan de globalThis).
const alertas = vm.runInThisContext('alertas');
const cumple = vm.runInThisContext('cumple');
const S = vm.runInThisContext('S');
const DATA = vm.runInThisContext('DATA');
const fijarP = vm.runInThisContext('(function(x){ P = x; })');
const guardar = vm.runInThisContext('guardar');
const restaurar = vm.runInThisContext('restaurar');
const planTexto = vm.runInThisContext('planTexto');
const irACodigo = vm.runInThisContext('irACodigo');
const construirIndice = vm.runInThisContext('construirIndice');
const DISPONIBLES = vm.runInThisContext('DISPONIBLES');
const alertasDe = vm.runInThisContext('alertasDe');
const CASOS = vm.runInThisContext('CASOS');

if (typeof alertas !== 'function') throw new Error('El motor no expuso alertas(); revisa el orden de los <script>');

// ------------------------------------------------------------------ utilidades
let fallos = 0, total = 0;

function preparar(pasos) {
  S.porPaso = {};
  for (const n of Object.keys(pasos)) S.porPaso[n] = Object.assign({}, pasos[n]);
  return S.porPaso;
}

function caso(titulo, nPaso, pasos, espera) {
  total++;
  preparar(pasos);
  S.paso = nPaso;
  S.dec = S.porPaso[nPaso] || (S.porPaso[nPaso] = {});
  const P = DATA.pasos[nPaso];
  fijarP(P);

  const salidas = alertas();
  const ids = salidas.map(a => a.id);
  const textos = [];
  for (const d of (P.derivados || [])) {
    const r = derivados ? derivados(d) : null;
    if (r) textos.push(...(Array.isArray(r) ? r : [r]));
  }

  const problemas = [];
  for (const id of (espera.salen || [])) if (!ids.includes(id)) problemas.push('falta la alerta ' + id);
  for (const id of (espera.noSalen || [])) if (ids.includes(id)) problemas.push('sobra la alerta ' + id);
  for (const frag of (espera.contiene || []))
    if (!textos.some(t => String(t).includes(frag))) problemas.push('ningún derivado dice «' + frag + '»');

  console.log((problemas.length ? '  FALLA  ' : '  ok     ') + titulo);
  for (const p of problemas) { console.log('           · ' + p); fallos++; }
  if (problemas.length) console.log('           alertas obtenidas: ' + (ids.join(', ') || '—'));
}

// Recoge el texto de un derivado sin depender del render.
function derivados(d) {
  const out = [];
  if (d.tipo === 'plantilla') return d.texto ? [d.texto] : [];
  for (const r of (d.reglas || [])) {
    if (!cumple(r.si)) continue;
    out.push(r.texto);
    if (d.modo === 'primera') break;
  }
  return out;
}

// ------------------------------------------------------------------ contexto base
// Diáfisis tibial 42C conminuta, una zona, estabilidad relativa, reducción
// funcional por vía indirecta, ferulaje con clavo.
const CONMINUTA = {
  2: { hueso: 'h-4', segmento: 's-42', tipo: 't-42C' },
  3: { zonas: 'z-unica', estabilidad: 'e-relativa' },
  4: { 'tipo-reduccion': 't-funcional', via: 'v-indirecta' },
  5: { principio: ['pr-ferulaje'], 'modo-ferulaje': ['mf-clavo'] }
};
// Espiroidea 42A1 simple, estabilidad absoluta, anatómica directa, compresión.
const SIMPLE = {
  2: { hueso: 'h-4', segmento: 's-42', tipo: 't-42A' },
  3: { zonas: 'z-unica', estabilidad: 'e-absoluta' },
  4: { 'tipo-reduccion': 't-anatomica', via: 'v-directa' },
  5: { principio: ['pr-compresion'], 'modo-compresion': ['mc-tornillo-tecnica'], neutralizacion: 'n-si' }
};
// Meseta tibial 41C: dos zonas, absoluta arriba y relativa abajo.
const MESETA = {
  2: { hueso: 'h-4', segmento: 's-41', tipo: 't-41C' },
  3: { zonas: 'z-dos', 'estab-articular': 'ea-absoluta', 'estab-metafisis': 'em-relativa' },
  4: { 'tipo-articular': 'ta-anatomica', 'via-articular': 'va-directa', 'tipo-meta': 'tm-funcional', 'via-meta': 'vm-indirecta' },
  5: { 'principio-articular': ['pa-compresion'], 'principio-meta': ['pm-ferulaje'], 'modo-compresion': ['mc-tornillo-tecnica'] }
};

const con = (base, extra) => Object.assign({}, base, extra);

// ================================================================== PASO 3
console.log('\n=== PASO 3 · Dosificar la estabilidad relativa');
caso('Trazo simple con estabilidad relativa y sin longitud de trabajo', 3,
  { 2: { hueso: 'h-4', segmento: 's-42', tipo: 't-42A' },
    3: { zonas: 'z-unica', estabilidad: 'e-relativa', palancas: ['p-densidad'] } },
  { salen: ['simple-puenteada', 'simple-puenteada-sin-trabajo', 'tierra-de-nadie'],
    contiene: ['denominador de la fórmula es diminuto'] });

caso('Conminuta bien dosificada: trabajo, cobertura y densidad', 3,
  { 2: { hueso: 'h-4', segmento: 's-42', tipo: 't-42C' },
    3: { zonas: 'z-unica', estabilidad: 'e-relativa',
         palancas: ['p-longitud', 'p-span', 'p-densidad', 'p-tornillos'] } },
  { noSalen: ['relativa-sin-dosificar', 'simple-puenteada', 'densidad-alta'],
    salen: ['trabajo-sin-contacto'],
    contiene: ['por debajo de 0,5 en conminutas', 'casi el doble de flexible'] });

caso('Placa bloqueada sin nada que corrija la asimetría', 3,
  { 2: { hueso: 'h-4', segmento: 's-42', tipo: 't-42C' },
    3: { zonas: 'z-unica', estabilidad: 'e-relativa', palancas: ['p-bloqueada'] } },
  { salen: ['callo-asimetrico', 'bloqueada-rigida'] });

caso('Placa bloqueada con far cortical locking', 3,
  { 2: { hueso: 'h-4', segmento: 's-42', tipo: 't-42C' },
    3: { zonas: 'z-unica', estabilidad: 'e-relativa',
         palancas: ['p-bloqueada', 'p-fcl', 'p-longitud', 'p-densidad'] } },
  { noSalen: ['callo-asimetrico', 'densidad-alta'], contiene: ['simétrico en las dos corticales'] });

caso('Relativa elegida y sin dosificar', 3,
  { 2: { hueso: 'h-4', segmento: 's-42', tipo: 't-42C' },
    3: { zonas: 'z-unica', estabilidad: 'e-relativa' } },
  { salen: ['relativa-sin-dosificar'] });

caso('Trazo simple con estabilidad ABSOLUTA: sin trampa', 3,
  { 2: { hueso: 'h-4', segmento: 's-42', tipo: 't-42A' },
    3: { zonas: 'z-unica', estabilidad: 'e-absoluta' } },
  { noSalen: ['simple-puenteada', 'simple-puenteada-sin-trabajo'] });

// ================================================================== PASO 6
console.log('\n=== PASO 6 · El implante');
caso('42C con clavo fresado y bloqueo estático (correcto)', 6,
  con(CONMINUTA, { 6: { implante: ['i-clavo'], 'clavo-config': ['cl-fresado', 'cl-estatico'], 'hueso-huesped': 'hh-normal', material: 'mat-titanio', defecto: 'df-no' } }),
  { salen: ['fresado-rigidez'], noSalen: ['clavo-sin-bloqueo', 'r6-ferulaje-sin-implante'],
    contiene: ['CARGA COMPARTIDA', 'no controla la rotación'] });

caso('Clavo sin definir el bloqueo', 6,
  con(CONMINUTA, { 6: { implante: ['i-clavo'], 'clavo-config': ['cl-fresado'], 'hueso-huesped': 'hh-normal' } }),
  { salen: ['clavo-sin-bloqueo'] });

caso('LCP a compresión solo con tornillos bloqueados', 6,
  { 2: { hueso: 'h-4', segmento: 's-42', tipo: 't-42A' },
    3: { zonas: 'z-unica', estabilidad: 'e-absoluta' },
    5: { principio: ['pr-compresion'] },
    6: { implante: ['i-placa', 'i-tornillo'], 'tipo-tornillo': ['tor-bloqueado'],
         'funcion-placa': ['fp-compresion'], 'diseno-placa': 'pl-bloqueada', 'hueso-huesped': 'hh-normal' } },
  { salen: ['bloqueada-no-comprime'] });

caso('LCP a compresión con un cortical por el agujero combi', 6,
  con(SIMPLE, { 6: { implante: ['i-placa', 'i-tornillo'], 'tipo-tornillo': ['tor-cortical'],
    'funcion-placa': ['fp-compresion'], 'diseno-placa': 'pl-bloqueada', 'hueso-huesped': 'hh-normal' } }),
  { noSalen: ['bloqueada-no-comprime'] });

caso('VA-LCP avisa del precio de angular', 6,
  con(MESETA, { 6: { implante: ['i-placa'], 'funcion-placa': ['fp-sosten'],
    'diseno-placa': 'pl-va', 'hueso-huesped': 'hh-normal' } }),
  { salen: ['va-angulacion'] });

caso('Placa convencional en hueso osteoporótico', 6,
  con(SIMPLE, { 6: { implante: ['i-placa'], 'funcion-placa': ['fp-proteccion'], 'diseno-placa': 'pl-no-bloqueada', 'hueso-huesped': 'hh-osteoporotico' } }),
  { salen: ['no-bloqueada-osteoporosis'], contiene: ['ángulo fijo'] });

caso('Compresión con placa sobre foco multifragmentario', 6,
  con(CONMINUTA, { 6: { implante: ['i-placa'], 'funcion-placa': ['fp-compresion'], 'diseno-placa': 'pl-no-bloqueada', 'hueso-huesped': 'hh-normal' } }),
  { salen: ['compresion-en-conminuta'] });

caso('Ferulaje elegido en el 5 pero sin implante que lo materialice', 6,
  con(CONMINUTA, { 6: { implante: ['i-tornillo'], 'hueso-huesped': 'hh-normal' } }),
  { salen: ['r6-ferulaje-sin-implante'] });

caso('Placa de protección sin tornillo que proteger', 6,
  con(SIMPLE, { 6: { implante: ['i-placa'], 'funcion-placa': ['fp-proteccion'], 'diseno-placa': 'pl-no-bloqueada', 'hueso-huesped': 'hh-normal' } }),
  { salen: ['r6-proteccion-sin-tornillo'] });

// ================================================================== PASO 7
console.log('\n=== PASO 7 · La posición');
caso('Mesa de tracción sin declarar protecciones', 7,
  con(CONMINUTA, { 7: { posicion: 'pos-mesa-traccion', traccion: 'tr-mesa', imagen: ['im-dos-planos'], proteccion: ['pt-presion'], checklist: ['ck-abordaje'] } }),
  { salen: ['mesa-pudendo', 'mesa-sin-proteger', 'checklist-incompleta'] });

caso('Mesa de tracción con protecciones y checklist completa', 7,
  con(CONMINUTA, { 7: { posicion: 'pos-mesa-traccion', traccion: 'tr-mesa', imagen: ['im-dos-planos', 'im-lado-sano'],
    proteccion: ['pt-presion', 'pt-perineal', 'pt-contralateral'],
    checklist: ['ck-abordaje', 'ck-reduccion', 'ck-imagen', 'ck-seguridad', 'ck-anestesia'] } }),
  { salen: ['mesa-pudendo'], noSalen: ['mesa-sin-proteger', 'checklist-incompleta'] });

caso('Prono sin protección ocular', 7,
  con(MESETA, { 7: { posicion: 'pos-prono', traccion: 'tr-gravedad', imagen: ['im-dos-planos'], proteccion: ['pt-presion'], checklist: ['ck-abordaje'] } }),
  { salen: ['prono-ojos', 'prono-sin-proteccion'] });

caso('Región tibial: sugerencia de posición', 7,
  con(CONMINUTA, { 7: { posicion: 'pos-supino', traccion: 'tr-distractor', imagen: ['im-lado-sano'],
    proteccion: ['pt-presion'], checklist: ['ck-abordaje', 'ck-reduccion', 'ck-imagen', 'ck-seguridad', 'ck-anestesia'] } }),
  { salen: ['distractor-libera', 'lado-sano-accesible'], noSalen: ['checklist-incompleta'],
    contiene: ['Diáfisis tibial'] });

// ================================================================== PASO 8
console.log('\n=== PASO 8 · El abordaje');
caso('Ferulaje puenteado por abordaje extenso', 8,
  con(CONMINUTA, { 8: { 'tipo-abordaje': 'ab-extenso', 'via-nombrada': 'vn-anteromedial-tibia',
    'partes-blandas': ['pb-colgajo', 'pb-periostio', 'pb-internervioso', 'pb-cierre'], herida: 'he-unica', ventana: 'vt-si' } }),
  { salen: ['extenso-sobre-puenteo'] });

caso('Ferulaje por MIPO (coherente)', 8,
  con(CONMINUTA, { 8: { 'tipo-abordaje': 'ab-mipo', 'via-nombrada': 'vn-anteromedial-tibia',
    'partes-blandas': ['pb-colgajo', 'pb-periostio', 'pb-internervioso', 'pb-cierre'], herida: 'he-unica', ventana: 'vt-si' } }),
  { noSalen: ['extenso-sobre-puenteo', 'ventana-cerrada'],
    contiene: ['Coherente. Vas a puentear'] });

caso('Ventana de partes blandas cerrada', 8,
  con(MESETA, { 8: { 'tipo-abordaje': 'ab-extenso', 'via-nombrada': 'vn-parapatelar',
    'partes-blandas': ['pb-colgajo', 'pb-periostio', 'pb-internervioso', 'pb-cierre'], herida: 'he-unica', ventana: 'vt-no' } }),
  { salen: ['ventana-cerrada', 'r8-ventana-abierta-tarde'] });

caso('Estructura en riesgo del posterior de húmero', 8,
  { 2: { hueso: 'h-1', segmento: 's-12', tipo: 't-12A' },
    3: { zonas: 'z-unica', estabilidad: 'e-absoluta' },
    4: { 'tipo-reduccion': 't-anatomica', via: 'v-directa' },
    5: { principio: ['pr-compresion'] },
    8: { 'tipo-abordaje': 'ab-extenso', 'via-nombrada': 'vn-posterior-humero',
      'partes-blandas': ['pb-colgajo', 'pb-periostio', 'pb-internervioso', 'pb-cierre'], herida: 'he-unica', ventana: 'vt-nc' } },
  { salen: ['radial-posterior'], contiene: ['RADIAL'] });

// ================================================================== PASO 9
console.log('\n=== PASO 9 · Las técnicas');
caso('Conminuta por vía indirecta sin distractor', 9,
  con(CONMINUTA, { 9: { basicas: ['tb-traccion'], avanzadas: ['ta-ninguna'], provisional: ['pv-agujas'],
    control: ['cn-proyecciones', 'cn-longitud', 'cn-eje', 'cn-rotacion'] } }),
  { salen: ['distractor-recomendado'], noSalen: ['rotacion-no-se-corrige', 'sin-provisional', 'longitud-sin-referencia'],
    contiene: ['distractor'] });

caso('Sin verificar rotación ni longitud', 9,
  con(CONMINUTA, { 9: { basicas: ['tb-traccion'], avanzadas: ['ta-distractor'], provisional: ['pv-fijador'],
    control: ['cn-proyecciones'] } }),
  { salen: ['rotacion-no-se-corrige', 'longitud-sin-referencia', 'r9-sin-control'] });

caso('Sin fijación provisional', 9,
  con(SIMPLE, { 9: { basicas: ['tb-pinzas'], avanzadas: ['ta-ninguna'], provisional: [],
    control: ['cn-proyecciones', 'cn-longitud', 'cn-eje', 'cn-rotacion'] } }),
  { salen: ['sin-provisional', 'pinza-mal-orientada'], contiene: ['contacto cortical exacto'] });

caso('Meseta: hundido elevado, secuencia correcta', 9,
  con(MESETA, { 9: { basicas: ['tb-joystick'], avanzadas: ['ta-distractor', 'ta-laminares'],
    'secuencia-articular': 'sa-articular-primero', hundido: 'hu-si', provisional: ['pv-agujas', 'pv-tornillo'],
    control: ['cn-proyecciones', 'cn-longitud', 'cn-eje', 'cn-rotacion', 'cn-articular'] } }),
  { salen: ['r9-hundido-sin-relleno'], noSalen: ['hundido-sin-elevar', 'secuencia-invertida', 'rotacion-no-se-corrige'] });

caso('Ferulaje con pinzas sobre el foco', 9,
  con(CONMINUTA, { 9: { basicas: ['tb-pinzas'], avanzadas: ['ta-distractor'], provisional: ['pv-fijador'],
    control: ['cn-proyecciones', 'cn-longitud', 'cn-eje', 'cn-rotacion'] } }),
  { salen: ['directa-sobre-puenteo'] });

// ================================================================== HERRAMIENTA
console.log('\n=== HERRAMIENTA · persistencia, plan y buscador');

function comprueba(titulo, fn) {
  total++;
  let problemas = [];
  try { problemas = fn() || []; } catch (e) { problemas = ['excepción: ' + e.message]; }
  console.log((problemas.length ? '  FALLA  ' : '  ok     ') + titulo);
  for (const p of problemas) { console.log('           · ' + p); fallos++; }
}

comprueba('El caso sobrevive a un cierre del navegador', () => {
  preparar(MESETA); S.paso = 5; S.modo = 'estudio';
  guardar();
  S.porPaso = {}; S.paso = 1; S.modo = 'consulta';
  global.location.hash = '';                       // sin hash manda localStorage
  const hubo = restaurar();
  const p = [];
  if (!hubo) p.push('restaurar() no detectó caso guardado');
  if (S.paso !== 5) p.push('no recuperó el paso (' + S.paso + ')');
  if ((S.porPaso[3] || {}).zonas !== 'z-dos') p.push('no recuperó las decisiones del Paso 3');
  if (!Array.isArray((S.porPaso[5] || {})['principio-articular'])) p.push('la multiselección perdió el tipo array');
  return p;
});

comprueba('La URL lleva el caso y lo devuelve intacto', () => {
  preparar(CONMINUTA); S.paso = 6;
  guardar();
  const hash = global.location.hash;
  const p = [];
  if (!hash.includes('p=6')) p.push('el hash no lleva el paso: ' + hash);
  if (!hash.includes('*')) p.push('el hash no marca la multiselección: ' + hash);
  _mem['infi-caso-v1'] = '';                       // vaciar localStorage: manda el hash
  S.porPaso = {}; S.paso = 1;
  restaurar();
  if (S.paso !== 6) p.push('el hash no restauró el paso');
  if ((S.porPaso[2] || {}).tipo !== 't-42C') p.push('el hash no restauró el Paso 2');
  const pr = (S.porPaso[5] || {}).principio;
  if (!Array.isArray(pr) || pr[0] !== 'pr-ferulaje') p.push('el hash no restauró la multiselección como array');
  return p;
});

comprueba('El plan consolidado recoge los nueve pasos', () => {
  preparar(Object.assign({}, MESETA, {
    6: { implante: ['i-placa'], 'funcion-placa': ['fp-sosten'], 'diseno-placa': 'pl-bloqueada', 'hueso-huesped': 'hh-normal' },
    7: { posicion: 'pos-supino', checklist: ['ck-abordaje', 'ck-reduccion', 'ck-imagen', 'ck-seguridad', 'ck-anestesia'] },
    8: { 'tipo-abordaje': 'ab-combinado', 'via-nombrada': 'vn-parapatelar', herida: 'he-doble', ventana: 'vt-si' },
    9: { basicas: ['tb-joystick'], avanzadas: ['ta-distractor'], hundido: 'hu-si',
         control: ['cn-proyecciones', 'cn-longitud', 'cn-eje', 'cn-rotacion', 'cn-articular'] }
  }));
  S.paso = 9; fijarP(DATA.pasos[9]);
  const t = planTexto();
  const p = [];
  for (const n of [2, 3, 4, 5, 6, 7, 8, 9]) if (!t.includes('PASO ' + n + ' ·')) p.push('falta el Paso ' + n);
  if (!t.includes('PLAN QUIRÚRGICO')) p.push('sin encabezado');
  if (!t.includes('Sostén')) p.push('no recoge la función de la placa del Paso 6');
  if (!t.includes('parapatelar') && !t.includes('Parapatelar')) p.push('no recoge el abordaje del Paso 8');
  if (t.split('\n').length < 25) p.push('el plan sale demasiado corto (' + t.split('\n').length + ' líneas)');
  return p;
});

comprueba('El buscador resuelve un código completo a decisiones', () => {
  S.porPaso = {}; S.paso = 2; fijarP(DATA.pasos[2]);
  irACodigo('42B2');
  const d = S.porPaso[2] || {};
  const p = [];
  if (d.hueso !== 'h-4') p.push('no dedujo el hueso (' + d.hueso + ')');
  if (d.segmento !== 's-42') p.push('no puso el segmento (' + d.segmento + ')');
  if (d.tipo !== 't-42B') p.push('no puso el tipo (' + d.tipo + ')');
  if (!d.grupo) p.push('no puso el grupo');
  return p;
});

comprueba('El índice de búsqueda cubre el compendio', () => {
  const idx = construirIndice();
  const p = [];
  if (idx.length < 600) p.push('índice corto: ' + idx.length + ' entradas');
  if (!idx.some(e => e.cod === '42B2')) p.push('no indexó 42B2');
  if (!idx.some(e => /meseta|tibia proximal/i.test(e.region))) p.push('no indexó la región de la meseta');
  return p;
});

comprueba('Lo doctrinal sale del bloque de avisos', () => {
  preparar(CONMINUTA); S.paso = 9; S.dec = S.porPaso[9] = {}; fijarP(DATA.pasos[9]);
  const todas = alertas();
  const p = [];
  const siempre = todas.filter(a => a.siempre);
  if (!siempre.length) p.push('ninguna alerta quedó marcada como doctrinal');
  if (siempre.some(a => !a.mostrarSiempre)) p.push('marcó como doctrinal algo que no lo es');
  if (todas.filter(a => !a.siempre).some(a => a.mostrarSiempre)) p.push('quedó doctrina entre los avisos del caso');
  return p;
});

// ================================================================== PASO 10
console.log('\n=== PASO 10 · Las complicaciones');
caso('Sin plan B decidido', 10,
  con(CONMINUTA, { 10: { vigilancia: ['vg-nounion'], 'tipo-nounion': 'nu-biologica' } }),
  { salen: ['sin-plan-b', 'septica-primero'], contiene: ['Pasos 3 y 5'] });

caso('Vigila la no unión pero no anticipa el tipo', 10,
  con(CONMINUTA, { 10: { 'plan-b': ['pb-reduccion'], vigilancia: ['vg-nounion'] } }),
  { salen: ['nounion-sin-tipo', 'septica-primero'], noSalen: ['sin-plan-b'] });

caso('Hueso osteoporótico sin recurso de rescate', 10,
  { 2: { hueso: 'h-4', segmento: 's-41', tipo: 't-41C' },
    6: { implante: ['i-placa'], 'funcion-placa': ['fp-puente'], 'diseno-placa': 'pl-bloqueada',
         'hueso-huesped': 'hh-osteoporotico' },
    10: { 'plan-b': ['pb-reduccion'], vigilancia: ['vg-fallo'] } },
  { salen: ['osteoporotico-sin-recurso', 'puente-fatiga'] });

caso('Fractura abierta sin vigilar la infección', 10,
  { 1: { 'partes-blandas': 'abierta-gustilo-3b' },
    2: { hueso: 'h-4', segmento: 's-42', tipo: 't-42C' },
    10: { 'plan-b': ['pb-implante'], vigilancia: ['vg-nounion'], 'tipo-nounion': 'nu-biologica' } },
  { salen: ['r10-abierta-sin-infeccion'] });

caso('Hertel y Hawkins aterrizan su pronóstico en el Paso 10', 10,
  { 2: { hueso: 'h-1', segmento: 's-11', tipo: 't-11C', 'cl-hertel': ['her-calcar'] },
    10: { 'plan-b': ['pb-conversion'], vigilancia: ['vg-necrosis'] } },
  { contiene: ['isquemia de la cabeza humeral'] });

caso('Relativa elegida sin vigilar la consolidación', 10,
  con(CONMINUTA, { 10: { 'plan-b': ['pb-reduccion'], vigilancia: ['vg-infeccion'] } }),
  { salen: ['r10-relativa-sin-vigilar'] });

// ================================================================== REGIONALES
console.log('\n=== CLASIFICACIONES REGIONALES · tienen que mover el razonamiento');

const regional = (titulo, dec2, nPaso, espera) => caso(titulo, nPaso,
  { 2: Object.assign({ hueso: 'h-4' }, dec2), 3: {}, 5: {}, 6: {}, 7: {}, 8: {}, 9: {} }, espera);

caso('Pauwels III avisa de cizallamiento en el Paso 5', 5,
  { 2: { hueso: 'h-3', segmento: 's-31', tipo: 't-31B', 'cl-pauwels': 'pau-III' } },
  { salen: ['rg-pauwels'] });

caso('Schatzker IV: la placa lateral no basta (Paso 8)', 8,
  { 2: { hueso: 'h-4', segmento: 's-41', tipo: 't-41B', 'cl-schatzker': 'sch-IV' } },
  { salen: ['rg-placa-lateral-insuficiente'] });

caso('Columna posteromedial: cambia posición y abordaje', 7,
  { 2: { hueso: 'h-4', segmento: 's-41', tipo: 't-41C', 'cl-columnas': ['col-post-med'] } },
  { salen: ['rg-columna-posterior-pos'] });

caso('Vancouver B2: revisar el vástago, no fijar', 6,
  { 2: { hueso: 'h-3', segmento: 's-32', tipo: 't-32A', 'cl-vancouver': 'van-B2' } },
  { salen: ['rg-vancouver-b2'] });

caso('Winquist IV con bloqueo dinámico', 6,
  { 2: { hueso: 'h-3', segmento: 's-32', tipo: 't-32C', 'cl-winquist': 'win-IV' },
    6: { implante: ['i-clavo'], 'clavo-config': ['cl-dinamico'], 'hueso-huesped': 'hh-normal' } },
  { salen: ['rg-winquist-dinamizar'] });

caso('Hawkins III: urgencia en el Paso 1', 1,
  { 2: { hueso: 'h-8', segmento: 's-81', 'cl-hawkins': 'haw-III' } },
  { salen: ['rg-astragalo-urgente'] });

caso('Pelvis en libro abierto: sangra (Paso 1)', 1,
  { 2: { hueso: 'h-6', segmento: 's-61', 'cl-young-burgess': 'yb-apc2' } },
  { salen: ['rg-pelvis-sangrado'] });

caso('Hertel con calcar corto: riesgo de necrosis (Paso 6)', 6,
  { 2: { hueso: 'h-1', segmento: 's-11', tipo: 't-11C', 'cl-hertel': ['her-calcar'] } },
  { salen: ['rg-necrosis-humeral'] });

caso('Lauge-Hansen orienta la maniobra (Paso 9)', 9,
  { 2: { hueso: 'h-4', segmento: 's-44', tipo: 't-44B', 'cl-lauge-hansen': 'lh-ser' } },
  { salen: ['rg-lauge-maniobra'] });

caso('Sin clasificación regional no aparece ninguna alerta regional', 5,
  { 2: { hueso: 'h-4', segmento: 's-42', tipo: 't-42A' } },
  { noSalen: ['rg-pauwels', 'rg-sa-medial'] });

// ================================================================== CASOS
console.log('\n=== CASOS · el error tiene que dispararse solo');
for (const c of CASOS) {
  comprueba(c.id, () => {
    const p = [];
    const mal = alertasDe(c.estadoError, c.pasoClave);
    const bien = alertasDe(c.estadoCorrecto, c.pasoClave);
    const criticas = mal.filter(a => a.severidad === 'critica' || a.severidad === 'advertencia');
    if (!criticas.length) p.push('el plan erróneo no dispara ninguna alerta crítica: el caso no se explica solo');
    const graves = a => a.severidad === 'critica' || a.severidad === 'advertencia';
    if (bien.some(graves)) p.push('el plan corregido todavía deja avisos graves: ' + bien.filter(graves).map(a => a.id).join(', '));
    if (!p.length) console.log('           ' + mal.length + ' avisos en el plan erróneo → ' + bien.length + ' en el corregido');
    return p;
  });
}

// ------------------------------------------------------------------ informe
console.log('\n' + '='.repeat(58));
console.log(fallos ? `${fallos} comprobación(es) fallida(s) en ${total} casos` : `Todo correcto: ${total} casos`);
console.log('='.repeat(58));
process.exit(fallos ? 1 : 0);
