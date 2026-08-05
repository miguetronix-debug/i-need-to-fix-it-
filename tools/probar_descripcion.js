// probar_descripcion.js — Imprime la descripción encadenada de varios códigos
// AO/OTA para revisar a ojo que no se duplican ni se pierden niveles.
//
// Uso:  node tools/probar_descripcion.js
const fs=require('fs'),vm=require('vm'),path=require('path');
const html=fs.readFileSync(path.join(path.resolve(__dirname,'..'),'prototipo.html'),'utf8');
const noop=()=>{};const nodo=()=>({innerHTML:'',textContent:'',value:'',style:{},dataset:{},open:false,
 classList:{add:noop,remove:noop,toggle:noop},appendChild:noop,addEventListener:noop,setAttribute:noop,
 insertAdjacentHTML:noop,scrollIntoView:noop,querySelector:()=>nodo(),querySelectorAll:()=>[],remove:noop});
global.document={getElementById:()=>nodo(),querySelector:()=>nodo(),querySelectorAll:()=>[],createElement:()=>nodo(),addEventListener:noop,body:nodo()};
global.window={scrollTo:noop,addEventListener:noop,matchMedia:()=>({matches:false,addListener:noop})};
const mem={};global.localStorage={getItem:k=>mem[k]??null,setItem:(k,v)=>{mem[k]=v},removeItem:noop};
global.location={hash:'',pathname:'/x',search:'',protocol:'file:'};
global.history={replaceState:noop};Object.defineProperty(global,'navigator',{value:{},configurable:true,writable:true});
for(const b of [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1])){ try{vm.runInThisContext(b)}catch(e){} }
const S=vm.runInThisContext('S'),DATA=vm.runInThisContext('DATA'),irPaso=vm.runInThisContext('irPaso'),
 pick=vm.runInThisContext('pick'),desc=vm.runInThisContext('descripcionCompleta');
const casos=[['s-41','t-41C','g-41C2','sg-41C2.1'],['s-42','t-42B','g-42B2',null],['s-31','t-31A','g-31A2',null],
 ['s-15','t-15B',null,null],['s-2R3','t-2R3C','g-2R3C1',null],['s-44','t-44B','g-44B2',null]];
for(const [seg,tip,gr,sg] of casos){
  irPaso(2); S.porPaso[2]={};
  const o=DATA.pasos[2].decisiones.find(d=>d.id==='segmento').opciones.find(x=>x.id===seg);
  pick('hueso',o.soloSi.hueso[0]); pick('segmento',seg); if(tip)pick('tipo',tip); if(gr)pick('grupo',gr); if(sg)pick('subgrupo',sg);
  const d=desc();
  console.log((d?d.frase:'—'));
}
