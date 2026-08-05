// probar_render.js — Recorre el prototipo con un DOM simulado y comprueba que
// cada pieza de la interfaz se pinta de verdad. Complementa a probar.js, que
// solo verifica la lógica.
//
// Uso:  node tools/probar_render.js
'use strict';
const fs=require('fs'), vm=require('vm'), path=require('path');
const RAIZ=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(RAIZ,'prototipo.html'),'utf8');
const bloques=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]);

const SALIDA={};
const noop=()=>{};
function nodo(id){ return {_id:id, get innerHTML(){return SALIDA[id]||''}, set innerHTML(v){SALIDA[id]=v},
  textContent:'', value:'', open:false, style:{}, dataset:{}, classList:{add:noop,remove:noop,toggle:noop,contains:()=>false},
  appendChild:noop, addEventListener:noop, setAttribute:noop, insertAdjacentHTML:noop,
  scrollIntoView:noop, querySelector:()=>nodo('x'), querySelectorAll:()=>[], parentNode:null, remove:noop}; }
const cache={};
global.document={ getElementById:id=>(cache[id]=cache[id]||nodo(id)), querySelector:()=>nodo('x'),
  querySelectorAll:()=>[], createElement:()=>nodo('new'), addEventListener:noop, body:nodo('body') };
global.window={scrollTo:noop,addEventListener:noop,print:noop,matchMedia:()=>({matches:false,addListener:noop})};
const mem={};
global.localStorage={getItem:k=>k in mem?mem[k]:null,setItem:(k,v)=>{mem[k]=String(v)},removeItem:k=>{delete mem[k]}};
global.location={hash:'',pathname:'/x.html',search:'',protocol:'file:'};
global.history={replaceState:(a,b,u)=>{const i=String(u).indexOf('#');global.location.hash=i>=0?String(u).slice(i):''}};
Object.defineProperty(global,'navigator',{value:{},configurable:true,writable:true});

for(const b of bloques){ try{ vm.runInThisContext(b); }catch(e){ console.log('ERROR al evaluar:',e.message); process.exit(1);} }
const S=vm.runInThisContext('S'), DATA=vm.runInThisContext('DATA');
const irPaso=vm.runInThisContext('irPaso'), pick=vm.runInThisContext('pick');
const verResumen=vm.runInThisContext('verResumen'), render=vm.runInThisContext('render');

let fail=0;
const chk=(t,c,extra)=>{ console.log((c?'  ok     ':'  FALLA  ')+t+(c?'':'  '+(extra||''))); if(!c) fail++; };

// Recorremos un caso real como lo haría un usuario
irPaso(2); pick('hueso','h-4'); pick('segmento','s-41'); pick('tipo','t-41C');
chk('Paso 2 pinta el buscador', /id="binput"/.test(SALIDA.decs||''));
chk('Paso 2 pinta las opciones', /class="opt/.test(SALIDA.decs||''));

irPaso(3); pick('zonas','z-dos'); pick('estab-articular','ea-absoluta'); pick('estab-metafisis','em-relativa');
pick('palancas','p-longitud'); pick('palancas','p-densidad');
chk('Paso 3 separa el principio doctrinal', /class="princ"/.test(SALIDA.principio||''), (SALIDA.principio||'').slice(0,80));
chk('Paso 3 pinta avisos del caso', /Avisos sobre este caso/.test(SALIDA.alerts||''));
chk('Cada aviso ofrece el porqué', /class="porque"/.test(SALIDA.alerts||''));
chk('El plan del paso recoge la dosis', /densidad de tornillos/i.test(SALIDA.plan||''));

irPaso(5); pick('principio-articular','pa-compresion'); pick('principio-meta','pm-ferulaje');
irPaso(6); pick('implante','i-placa'); pick('funcion-placa','fp-sosten'); pick('diseno-placa','pl-bloqueada'); pick('hueso-huesped','hh-normal');

verResumen();
const R=SALIDA.vistaresumen||'';
chk('El resumen se pinta', /Plan quirúrgico completo/.test(R));
chk('El resumen trae el botón de copiar', /id="bcopiar"/.test(R));
for(const n of [2,3,5,6]) chk('El resumen incluye el Paso '+n, new RegExp('Paso '+n+'</span>').test(R));
chk('El resumen arrastra los derivados', /class="rder"/.test(R), R.slice(0,200));

// La URL quedó con el caso
chk('La URL lleva el caso', /p=\d+.*&3=.*palancas:\*/.test(global.location.hash), global.location.hash.slice(0,120));
chk('El caso quedó guardado en disco', !!mem['infi-caso-v1']);

console.log('\n'+(fail? fail+' fallo(s)' : 'Render correcto en todos los puntos'));
process.exit(fail?1:0);
