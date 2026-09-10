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
test('Radio y cúbito conservan códigos, lado y notas independientes',()=>{
 const b=app();b.run('irACodigo("2R2A1");ladoLesion("derecho");guardarNota("justificacion","Plan del radio");agregarLesion("h-2U")');
 assert.equal(b.run('S.lesiones.length'),2);assert.equal(b.run('S.dec.hueso'),'h-2U');
 assert.equal(b.run('S.dec.segmento'),undefined); // no se supone el mismo nivel
 b.run('irACodigo("2U2B2");ladoLesion("derecho");guardarNota("justificacion","Plan del cubito");seleccionarLesion(0)');
 assert.equal(b.run('conContexto(2,codigoCanonico)'),'2R2A1');assert.equal(b.run('notaPaso(2).justificacion'),'Plan del radio');
 b.run('seleccionarLesion(1)');assert.equal(b.run('conContexto(2,codigoCanonico)'),'2U2B2');assert.equal(b.run('notaPaso(2).justificacion'),'Plan del cubito');
});
test('Tibia y peroné mantienen clasificaciones diferentes en el plan conjunto',()=>{
 const b=app();b.run('irACodigo("42B2");guardarNota("datos","Datos tibia");agregarLesion("h-4F");irACodigo("4F2A");guardarNota("datos","Datos perone")');
 const before=b.run('JSON.stringify(S.porPaso)');b.run('verResumen()');
 const text=b.run('planTexto()');assert.match(text,/42B2/);assert.match(text,/4F2A/);assert.match(text,/Datos tibia/);assert.match(text,/Datos perone/);
 assert.equal((b.nodes.vistaresumen.innerHTML.match(/id="bcopiar"/g)||[]).length,1);
 assert.equal((b.nodes.vistaresumen.innerHTML.match(/id="share-status"/g)||[]).length,1);
 assert.equal(b.run('JSON.stringify(S.porPaso)'),before);assert.equal(b.run('S.dec===S.porPaso[S.paso]'),true);
 b.run('editarLesionPaso(0,3)');assert.equal(b.run('S.lesionActiva'),0);assert.equal(b.run('S.paso'),3);
});
test('Las alertas y la revisión de pasos no se mezclan entre lesiones',()=>{
 const b=app();b.run('cargarCaso(CASOS[0].id,"error")');const alerts=b.run('JSON.stringify(alertas())');
 b.run('guardarNota("datos","Nota original");agregarLesion("h-2U");irACodigo("2U2A1");irPaso(6);guardarNota("datos","Implante cubito");irPaso(2);pick("tipo","t-2U2B")');
 assert.equal(b.run('S.revisar[6]'),true);b.run('seleccionarLesion(0)');
 assert.equal(b.run('JSON.stringify(alertas())'),alerts);assert.equal(b.run('!!S.revisar[6]'),false);
});
test('Una recarga conserva todas las lesiones y la selección activa',()=>{
 const b=app();b.run('irACodigo("42B2");guardarNota("datos","Tibia privada");agregarLesion("h-4F");irACodigo("4F2A");guardarNota("datos","Perone privado")');
 const c=app(b.mem,b.loc.hash);assert.equal(c.run('S.lesiones.length'),2);assert.equal(c.run('S.lesionActiva'),1);
 assert.equal(c.run('notaPaso(2).datos'),'Perone privado');c.run('seleccionarLesion(0)');assert.equal(c.run('notaPaso(2).datos'),'Tibia privada');
});
test('El enlace comparte todas las clasificaciones y ningún texto libre',()=>{
 const b=app();b.run('irACodigo("2R2A1");guardarContexto("Contexto privado");guardarNota("datos","Nota privada");ladoLesion("izquierdo");agregarLesion("h-2U");irACodigo("2U2B2")');
 assert.doesNotMatch(decodeURIComponent(b.loc.hash),/privad/);
 const c=app({},b.loc.hash);assert.equal(c.run('S.lesiones.length'),2);assert.equal(c.run('S.contextoCaso'),'');
 c.run('seleccionarLesion(0)');assert.equal(c.run('S.lado'),'izquierdo');assert.equal(c.run('tieneNotas(2)'),false);assert.equal(c.run('conContexto(2,codigoCanonico)'),'2R2A1');
 const injected='#fx='+encodeURIComponent(JSON.stringify({v:2,lesiones:[{porPaso:{2:{hueso:'h-4'}},notas:{2:{datos:'inyectado'}},contextoCaso:'inyectado'}]}));
 const d=app({},injected);assert.equal(d.run('tieneNotas(2)'),false);
});
test('Casos antiguos se migran a una lesión y enlaces malformados no rompen la app',()=>{
 const b=app({'infi-caso-v1':JSON.stringify({paso:2,porPaso:{2:{hueso:'h-4',segmento:'s-42'}}})});
 assert.equal(b.run('S.lesiones.length'),1);assert.equal(b.run('S.dec.segmento'),'s-42');
 for(const hash of ['#fx=%ZZ','#fx=null','#fx='+encodeURIComponent('{"v":2,"lesiones":[null,{},7],"lesionActiva":999}')])assert.doesNotThrow(()=>app({},hash));
});
test('Eliminar una lesión conserva las demás y cancelar no borra nada',()=>{
 const b=app();b.run('irACodigo("42B2");guardarNota("datos","Conservar tibia");agregarLesion("h-4F");irACodigo("4F2A")');
 const c=app(b.mem,b.loc.hash,false);c.run('eliminarLesion()');assert.equal(c.run('S.lesiones.length'),2);
 b.run('eliminarLesion()');assert.equal(b.run('S.lesiones.length'),1);assert.equal(b.run('notaPaso(2).datos'),'Conservar tibia');assert.equal(b.run('conContexto(2,codigoCanonico)'),'42B2');
});
test('El nuevo caso limpia todas las lesiones y cargar un ejemplo reemplaza el conjunto',()=>{
 const b=app();b.run('irACodigo("42B2");agregarLesion("h-4F");nuevoCaso()');assert.equal(b.run('S.lesiones.length'),1);assert.equal(b.run('hayCaso()'),false);
 b.run('agregarLesion("h-4F");cargarCaso(CASOS[0].id,"error")');assert.equal(b.run('S.lesiones.length'),1);
});
test('Una lesión vacía activa no oculta los datos guardados en otra',()=>{
 const b=app();b.run('irACodigo("42B2");agregarLesion()');assert.equal(b.run('hayCaso()'),true);assert.match(b.run('planTexto()'),/42B2/);
});
test('Los accesos asociados y la interfaz multilesión se traducen',()=>{
 const b=app();b.run('irACodigo("2R2A1")');assert.match(b.nodes.lesiones.innerHTML,/Añadir cúbito asociado/);
 b.run('idioma("en")');assert.match(b.nodes.lesiones.innerHTML,/Add associated ulna/);
 b.run('agregarLesion("h-2U");verResumen()');assert.match(b.nodes.vistaresumen.innerHTML,/Combined injury plan/);
});
console.log('\n'+checks+' pruebas de experiencia correctas.');
