// Regresiones de la experiencia: recargas, incertidumbre, notas, revisión y aprendizaje.
// Ejecuta el HTML real generado, sin ignorar errores de arranque. No es una prueba visual.
'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const path=require('node:path');
const html=fs.readFileSync(path.join(__dirname,'../prototipo.html'),'utf8');
const scripts=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
function app(mem={},hash='',confirmValue=true,blocked=false){
 const nodes={};const noop=()=>{};
 function node(id){return nodes[id]||(nodes[id]={id,innerHTML:'',textContent:'',style:{},value:'',dataset:{},disabled:false,open:false,
  classList:{add:noop,remove:noop,toggle:noop},setAttribute:noop,appendChild:noop,remove:noop,focus:noop,scrollIntoView:noop,
  querySelectorAll:()=>[],querySelector:()=>node('x'),addEventListener:noop,insertAdjacentHTML:noop});}
 const loc={hash,pathname:'/index.html',search:'',protocol:'file:',get href(){return 'https://example.org'+this.pathname+this.hash;}};
 const ctx=vm.createContext({console,setTimeout:noop,confirm:()=>confirmValue,
  window:{scrollTo:noop,addEventListener:noop},navigator:{language:'es'},location:loc,
  history:{replaceState:(a,b,url)=>{loc.hash=url.includes('#')?url.slice(url.indexOf('#')):'';}},
  localStorage:{getItem:k=>{if(blocked)throw Error('blocked');return mem[k]||null;},setItem:(k,v)=>{if(blocked)throw Error('blocked');mem[k]=v;}},
  document:{getElementById:node,querySelector:node,querySelectorAll:()=>[],documentElement:node('html'),body:node('body'),createElement:node},
 });
 for(const s of scripts)vm.runInContext(s,ctx);
 return {run:s=>vm.runInContext(s,ctx),nodes,mem,loc};
}
let checks=0;
function test(name,fn){fn();checks++;console.log('  ok  '+name);}
const a=app();
test('El arranque muestra tres caminos y diez pasos navegables',()=>{
 assert.equal(a.run('S.vista'),'inicio');assert.match(a.nodes.vistaresumen.innerHTML,/Resolver un caso/);
 assert.match(a.nodes.vistaresumen.innerHTML,/Autoevaluarme/);assert.equal((a.nodes.vistaresumen.innerHTML.match(/class="ex-step /g)||[]).length,10);
});
test('Un paso vacío no cuenta como registrado',()=>assert.equal(a.run('estadoPaso(1).completo'),false));
a.run("irPaso(1);guardarContexto('Caso docente de prueba');guardarNota('datos','Texto con <img src=x onerror=alert(1)>');pick('estado-fisiologico','ef-estable')");
// usa el ID existente del contenido para no depender del vocabulario del ejemplo
const id=a.run('DATA.pasos[1].decisiones[0].opciones[0].id');
a.run('pick("estado-fisiologico",'+JSON.stringify(id)+')');
test('Notas y decisiones sobreviven a una recarga de la URL propia',()=>{
 const b=app(a.mem,a.loc.hash);assert.equal(b.run('S.contextoCaso'),'Caso docente de prueba');
 assert.match(b.run('notaPaso(1).datos'),/onerror/);assert.equal(b.run('S.dec===S.porPaso[S.paso]'),true);
 b.run("guardarNota('justificacion','Porque debo contrastar los datos');guardar()");
 assert.match(JSON.parse(a.mem['infi-caso-v1']).notas[1].justificacion,/contrastar/);
});
test('Un enlace ajeno no mezcla las notas del caso local',()=>{
 const b=app(a.mem,'#p=2&2=hueso:h-4,segmento:s-42');assert.equal(b.run('S.contextoCaso'),'');assert.equal(b.run('tieneNotas(1)'),false);
 assert.equal(b.run('S.dec.segmento'),'s-42');
});
test('Las notas se escapan al exportarlas a HTML y no viajan en la URL',()=>{
 a.run('verResumen()');assert.match(a.nodes.vistaresumen.innerHTML,/&lt;img/);assert.doesNotMatch(a.nodes.vistaresumen.innerHTML,/<img src=x/);
 assert.doesNotMatch(a.loc.hash,/Caso|onerror/);assert.match(a.run('planTexto()'),/Caso docente de prueba/);
});
test('Cancelar reinicio conserva todo el caso',()=>{
 const b=app(a.mem,a.loc.hash,false);const before=b.run('JSON.stringify(S.porPaso)+JSON.stringify(S.notas)+S.contextoCaso');b.run('reiniciar()');
 assert.equal(b.run('JSON.stringify(S.porPaso)+JSON.stringify(S.notas)+S.contextoCaso'),before);
});
test('Cancelar carga de un ejemplo conserva las notas',()=>{
 const b=app(a.mem,a.loc.hash,false);b.run("cargarCaso(CASOS[0].id,'error')");assert.equal(b.run('S.contextoCaso'),'Caso docente de prueba');
});
test('Confirmar reinicio borra el caso pero conserva aprendizaje',()=>{
 const mem={...a.mem,'infi-quiz-v1':'{"p1":{"0":{"bien":true}}}'};const b=app(mem,'',true);b.run('reiniciar()');
 assert.equal(b.run('hayCaso()'),false);assert.equal(b.run('statsPaso(1).correctas'),1);
});
test('Datos guardados malformados y enlaces inválidos no rompen el arranque',()=>{
 for(const value of ['null','[]','{','{"porPaso":{"1":null},"paso":999,"modo":"invalid","notas":[]}']){
  const b=app({'infi-caso-v1':value},'#p=999&1=estado-fisiologico:inexistente');assert.equal(b.run('S.paso'),1);assert.equal(b.run('S.dec===S.porPaso[1]'),true);
 }
});
test('Información insuficiente permite avanzar pero mantiene el paso incompleto',()=>{
 const b=app();b.run("irPaso(1);for(const d of P.decisiones.filter(visible))marcarPendiente(d.id)");
 assert.equal(b.nodes.sig.disabled,false);assert.equal(b.run('estadoPaso(1).completo'),false);
 assert.match(b.run('planTexto()'),/Preguntas pendientes/);
 b.run('pick(P.decisiones[0].id,P.decisiones[0].opciones[0].id)');assert.equal(b.run('!!S.pendientes[1][P.decisiones[0].id]'),false);
});
test('Cambiar un paso marca decisiones posteriores y conserva las notas',()=>{
 const b=app();b.run("irPaso(3);guardarNota('justificacion','Revisar estabilidad');irPaso(1);pick(P.decisiones[0].id,P.decisiones[0].opciones[0].id)");
 assert.equal(b.run('S.revisar[3]'),true);assert.equal(b.run('notaPaso(3).justificacion'),'Revisar estabilidad');
 b.run('irPaso(3);confirmarRevision()');assert.equal(b.run('!!S.revisar[3]'),false);
 b.run('irACodigo("42B2")');assert.equal(b.run('S.revisar[3]'),true);
});
test('Cambiar anatomía no elimina decisiones previas del registro; pide revisión',()=>{
 const b=app();b.run("S.porPaso[2]={hueso:'h-4',segmento:'s-41'};S.porPaso[8]={'tipo-abordaje':'ab-combinado','via-nombrada':'vn-parapatelar'};irPaso(8)");
 assert.equal(b.run('estadoPaso(8).estado'),'revisar');assert.match(b.run('planTexto()'),/parapatelar/i);
 b.run('confirmarRevision()');assert.equal(b.run('S.porPaso[8]["via-nombrada"]'),undefined);
});
test('Autoevaluación no modifica el caso; contabiliza una vez cada intento',()=>{
 const before=a.run('JSON.stringify(S.porPaso)');a.run('abrirQuiz(3);responderQuiz(0,0);responderQuiz(0,1)');
 assert.equal(a.run('statsPaso(3).intentos'),1);assert.equal(a.run('JSON.stringify(S.porPaso)'),before);
 assert.match(a.nodes.vistaresumen.innerHTML,/Respuesta del material/);
});
test('Repaso de errores y cambio de idioma conservan respuestas y explicación',()=>{
 a.run('abrirQuiz(3,true)');assert.equal(a.run('S.quizIndices.includes(0)'),true);
 a.run('responderQuiz(0,DATA.pasos[3].autoevaluacion[0].correcta);idioma("en")');
 assert.equal(a.run('statsPaso(3).intentos'),2);assert.equal(a.run('statsPaso(3).correctas'),1);assert.equal(a.run('falladas(3).length'),0);
 assert.match(a.nodes.vistaresumen.innerHTML,/Answer in the material/);assert.match(a.nodes.vistaresumen.innerHTML,/disabled/);
});
test('Biblioteca encuentra tablas por texto en ES y EN',()=>{
 a.run('idioma("es");verBiblioteca()');assert(a.run('resultadosBiblioteca("lactato","tablas").length')>0);
 a.run('idioma("en")');assert(a.run('resultadosBiblioteca("lactate","tablas").length')>0);
 assert.equal(a.run('resultadosBiblioteca("zzzznuncaexiste","todo").length'),0);
});
test('Lecturas y estadísticas no afirman dominio',()=>{
 a.run('marcarLeido();verProgreso()');assert.match(a.nodes.vistaresumen.innerHTML,/not a clinical competence score/);
 assert.equal(a.run('!!leidos()[S.paso]'),true);
});
test('Almacenamiento bloqueado permite continuar y avisa',()=>{
 const b=app({},'',true,true);b.run('irPaso(1);guardarNota("datos","Ejemplo")');assert.equal(b.run('S.guardado'),false);
 assert.match(b.nodes['ex-save'].textContent,/No se pudo guardar/);
});
test('Todos los manejadores generados son JavaScript válido',()=>{
 const b=app();const surfaces=[html.replace(/<script>[\s\S]*?<\/script>/g,'').replace(/<style>[\s\S]*?<\/style>/g,'')];
 for(const lang of ['es','en']){
  b.run('idioma('+JSON.stringify(lang)+')');
  for(const call of ['irInicio()','irPaso(1)','irPaso(2)','modo("estudio")','verResumen()','verBiblioteca()','verProgreso()','abrirQuiz(1)','verCasos()','verCaso(CASOS[0].id)']){
   b.run(call);for(const el of Object.values(b.nodes))surfaces.push(el.innerHTML);
  }
 }
 for(const text of surfaces)for(const m of text.matchAll(/\bon(?:click|input|change|blur)="([^"]*)"/g)){
  const code=m[1].replace(/&quot;/g,'"').replace(/&#39;/g,"'").replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&amp;/g,'&');
  assert.doesNotThrow(()=>new Function('event',code),code);
 }
});
console.log('\n'+checks+' pruebas de experiencia correctas.');
