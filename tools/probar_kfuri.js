// probar_kfuri.js — Comprueba la meseta tibial: los cuatro cuadrantes de
// Schatzker modificada por Kfuri y sus cuatro abordajes.
//
// Lo que vigila:
//   · que cada cuadrante emita su hecho y también la mitad a la que pertenece,
//     para que las alertas antiguas (col-medial, col-posterior) sigan valiendo,
//   · que el app avise si marcas un cuadrante y no lo abordas,
//   · que se calle en cuanto añades la ventana correcta,
//   · y que en el segmento 41 se ofrezcan SOLO los cuatro abordajes propios,
//     volviendo los genéricos fuera de la meseta.
//
// Uso:  node tools/probar_kfuri.js

'use strict';
const fs=require('fs'), path=require('path'), vm=require('vm');
const RAIZ=path.resolve(__dirname, '..');
const html=fs.readFileSync(path.join(RAIZ,'prototipo.html'),'utf8');
const bloques=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
const noop=()=>{};
const nodo=()=>({innerHTML:'',textContent:'',value:'',style:{},lang:'',classList:{add:noop,remove:noop,toggle:noop},
  getAttribute:()=>null,setAttribute:noop,appendChild:noop,addEventListener:noop,insertAdjacentHTML:noop,
  querySelector:()=>nodo(),querySelectorAll:()=>[]});
global.document={getElementById:()=>nodo(),querySelector:()=>nodo(),querySelectorAll:()=>[],createElement:()=>nodo(),
  addEventListener:noop,body:nodo(),documentElement:nodo(),title:''};
global.window={scrollTo:noop,addEventListener:noop,print:noop,matchMedia:()=>({matches:false,addListener:noop})};
const mem={}; global.localStorage={getItem:k=>k in mem?mem[k]:null,setItem:(k,v)=>{mem[k]=String(v)},removeItem:k=>{delete mem[k]}};
global.location={hash:'',pathname:'/x.html',search:''}; global.history={replaceState:noop};
Object.defineProperty(global,'navigator',{value:{},configurable:true,writable:true});
for(const b of bloques){ try{ vm.runInThisContext(b); }catch(e){} }
const S=vm.runInThisContext('S'), DATA=vm.runInThisContext('DATA');
const alertas=vm.runInThisContext('alertas'), contexto=vm.runInThisContext('contexto');
const fijarP=vm.runInThisContext('(function(x){ P=x; })');
const opcionesVisibles=vm.runInThisContext('opcionesVisibles');
let fallos=0;
const ok=(n,c,d)=>{ console.log((c?'  ok    ':'  FALLA ')+n+(c||!d?'':' → '+d)); if(!c) fallos++; };

// meseta tibial, cuadrante posteromedial marcado, abordaje lateral elegido
S.porPaso={2:{hueso:'h-4',segmento:'s-41',tipo:'t-41C','cl-columnas':['col-post-med']},
           8:{'via-nombrada':['vn-tp-lateral']}};
S.paso=8; S.dec=S.porPaso[8]; fijarP(DATA.pasos[8]);
const ctx=contexto();
ok('El cuadrante emite su hecho', ctx.indexOf('col-posteromedial')>=0, ctx.filter(x=>x.indexOf('col-')===0).join(','));
ok('Sigue emitiendo la mitad medial (compatibilidad)', ctx.indexOf('col-medial')>=0);
let al=alertas().map(a=>a.id);
ok('Avisa de que no abordas el posteromedial', al.indexOf('tp-cuadrante-posteromedial')>=0, al.join(', ').slice(0,90));

// ahora sí lo aborda: la alerta se calla
S.porPaso[8]['via-nombrada']=['vn-tp-lateral','vn-tp-posteromedial'];
S.dec=S.porPaso[8];
al=alertas().map(a=>a.id);
ok('Con la ventana correcta se calla', al.indexOf('tp-cuadrante-posteromedial')<0, al.join(', ').slice(0,90));

// en la meseta solo se ofrecen los cuatro
const dVia=DATA.pasos[8].decisiones.find(d=>d.id==='via-nombrada');
const vis=opcionesVisibles(dVia).map(o=>o.id);
ok('En la meseta se ofrecen los cuatro cuadrantes',
   ['vn-tp-lateral','vn-tp-medial','vn-tp-posteromedial','vn-tp-posterolateral'].every(v=>vis.indexOf(v)>=0));
ok('En la meseta NO se ofrece parapatelar ni anteromedial genérico',
   vis.indexOf('vn-parapatelar')<0 && vis.indexOf('vn-anteromedial-tibia')<0, vis.join(','));

// fuera de la meseta, las vías genéricas vuelven
S.porPaso[2]={hueso:'h-3',segmento:'s-33'};
const vis2=opcionesVisibles(dVia).map(o=>o.id);
ok('Fuera de la meseta vuelve el parapatelar', vis2.indexOf('vn-parapatelar')>=0);
ok('Fuera de la meseta desaparecen los cuatro de tibia proximal',
   vis2.indexOf('vn-tp-lateral')<0);
console.log('\n'+'='.repeat(58));
console.log(fallos?`${fallos} fallo(s)`:'Kfuri y abordajes: correcto');
process.exit(fallos?1:0);
