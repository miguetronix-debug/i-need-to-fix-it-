/* Experiencia educativa. Usa DATA, traducciones y reglas del motor existente.
   Sin inferencias clínicas nuevas. Notas y aprendizaje quedan en este navegador. */
const CLAVE_ESTUDIO='infi-estudio-v1';
S.notas={}; S.pendientes={}; S.revisar={}; S.contextoCaso=''; S.guardado=true;
S.quizPaso=1; S.quizRespuestas={}; S.quizSoloFallos=false; S.filtroEstudio='todo';

function objeto(v){return v!==null&&typeof v==='object'&&!Array.isArray(v);}
function objetoGuardado(key){
  try {const v=JSON.parse(localStorage.getItem(key)||'{}'); return objeto(v)?v:{};} catch(e){return {};}
}
function normalizarCaso(g){
  const out={porPaso:{},notas:{},pendientes:{},revisar:{},contextoCaso:'',paso:1,modo:'consulta'};
  if(!objeto(g)) return out;
  out.paso=DISPONIBLES.includes(Number(g.paso))?Number(g.paso):1;
  out.modo=['consulta','estudio'].includes(g.modo)?g.modo:'consulta';
  out.contextoCaso=typeof g.contextoCaso==='string'?g.contextoCaso.slice(0,1500):'';
  for(const n of DISPONIBLES){
    const ds=objeto(g.porPaso)&&objeto(g.porPaso[n])?g.porPaso[n]:{};
    out.porPaso[n]={}; out.pendientes[n]={};
    for(const d of DATA.pasos[n].decisiones){
      const valido=id=>typeof id==='string'&&d.opciones.some(o=>o.id===id);
      if(esMulti(d)&&Array.isArray(ds[d.id])){
        const a=[...new Set(ds[d.id].filter(valido))];if(a.length)out.porPaso[n][d.id]=a;
      }else if(!esMulti(d)&&valido(ds[d.id]))out.porPaso[n][d.id]=ds[d.id];
      if(objeto(g.pendientes)&&objeto(g.pendientes[n])&&g.pendientes[n][d.id]===true&&!out.porPaso[n][d.id])out.pendientes[n][d.id]=true;
    }
    const nota=objeto(g.notas)&&objeto(g.notas[n])?g.notas[n]:{};
    out.notas[n]={};
    for(const k of ['datos','interpretacion','justificacion','faltante'])if(typeof nota[k]==='string')out.notas[n][k]=nota[k].slice(0,2000);
    if(objeto(g.revisar)&&g.revisar[n]===true)out.revisar[n]=true;
  }
  return out;
}
function notaPaso(n){return S.notas[n]||{};}
function tieneNotas(n){return Object.values(notaPaso(n)).some(v=>v&&v.trim());}
function conContexto(n,fn){
  const anterior={p:P,dec:S.dec,paso:S.paso};
  try{P=pasoDe(n);S.paso=n;S.dec=S.porPaso[n]||{};return fn(P);}finally{P=anterior.p;S.dec=anterior.dec;S.paso=anterior.paso;}
}
function estadoPaso(n){
  return conContexto(n,p=>{
    const visibles=p.decisiones.filter(visible);
    const respuesta=d=>{
      const ids=Array.isArray(S.dec[d.id])?S.dec[d.id]:[S.dec[d.id]];
      return opcionesVisibles(d).some(o=>ids.includes(o.id));
    };
    const oblig=visibles.filter(d=>!esMulti(d));
    const hechas=visibles.filter(respuesta).length;
    const faltan=visibles.filter(d=>!esMulti(d)&&!respuesta(d));
    const inciertas=visibles.filter(d=>(S.pendientes[n]||{})[d.id]);
    const guardadas=Object.values(S.dec).some(v=>Array.isArray(v)?v.length:!!v);
    const obsoletas=p.decisiones.some(d=>{const ids=Array.isArray(S.dec[d.id])?S.dec[d.id]:S.dec[d.id]?[S.dec[d.id]]:[];return ids.length&&(!visible(d)||ids.some(id=>!opcionesVisibles(d).some(o=>o.id===id)));});
    const tocado=guardadas||inciertas.length>0||tieneNotas(n);
    const completo=hechas>0&&faltan.length===0&&inciertas.length===0&&!obsoletas;
    return {hechas,total:visibles.length,faltan,inciertas,tocado,completo,
      estado:S.revisar[n]||obsoletas?'revisar':completo?'registrado':tocado?'parcial':'pendiente'};
  });
}
function etiquetaEstado(estado){return TR({revisar:'ex_review',registrado:'ex_recorded',parcial:'ex_partial',pendiente:'ex_pending'}[estado]);}
function tituloPaso(n){return ((IDIOMAS[S.idioma]||{}).pasos_chips||[])[n-1]||pasoDe(n).titulo;}
function marcarPosteriores(n){
  for(const k of DISPONIBLES)if(k>n&&estadoPaso(k).tocado)S.revisar[k]=true;
}
function actualizarGuardado(){
  const el=document.getElementById('ex-save');
  if(el){el.textContent=TR(S.guardado?'ex_saved':'ex_storage_error');el.classList.toggle('warning',!S.guardado);}
}
function guardarNota(campo,valor){
  if(!['datos','interpretacion','justificacion','faltante'].includes(campo))return;
  S.notas[S.paso]=S.notas[S.paso]||{};S.notas[S.paso][campo]=valor.slice(0,2000);
  guardar();actualizarGuardado();
}
function guardarContexto(valor){S.contextoCaso=valor.slice(0,1500);guardar();actualizarGuardado();}
function marcarPendiente(id){
  if(!P.decisiones.some(d=>d.id===id&&visible(d)))return;
  const pendientes=S.pendientes[S.paso]=S.pendientes[S.paso]||{};
  pendientes[id]=!pendientes[id];
  if(pendientes[id])delete S.dec[id];
  depurarSelecciones();marcarPosteriores(S.paso);guardar();render();
}
function confirmarRevision(){depurarSelecciones();delete S.revisar[S.paso];guardar();render();}
function depurarSelecciones(){
  // Limpia dependencias del paso actual hasta converger; los demás conservan
  // sus decisiones para que el usuario pueda revisarlas, nunca se borran solos.
  for(let i=0;i<P.decisiones.length;i++){
    let cambio=false;
    for(const d of P.decisiones){
      const v=S.dec[d.id];if(!v)continue;
      const ids=opcionesVisibles(d).map(o=>o.id);
      const valor=!visible(d)?undefined:Array.isArray(v)?v.filter(id=>ids.includes(id)):ids.includes(v)?v:undefined;
      if(JSON.stringify(v)!==JSON.stringify(valor)){cambio=true;if(valor&&(!Array.isArray(valor)||valor.length))S.dec[d.id]=valor;else delete S.dec[d.id];}
    }
    if(!cambio)break;
  }
}
function irInicio(){S.vista='inicio';render();window.scrollTo(0,0);}
function continuarCaso(){S.modo='consulta';irPaso(S.paso);}
function nuevoCaso(){
  if(hayCaso()&&!confirm(TR('ex_reset_confirm')))return;
  Object.assign(S,normalizarEpisodio({}));S.dec=S.porPaso[1];S.resp={};S.caso=null;S.vista='paso';guardar();irPaso(1);
}
function iniciarEstudio(){S.modo='estudio';irPaso(S.paso);}
function mapaPasos(accion){
  return '<div class="ex-map">'+DISPONIBLES.map(n=>{
    const e=estadoPaso(n);
    return '<button class="ex-step '+e.estado+(S.vista==='paso'&&n===S.paso?' current':'')+'" onclick="'+accion+'('+n+')"><b>'+n+'</b><strong>'+esc(tituloPaso(n))+'</strong><small>'+esc(etiquetaEstado(e.estado))+'</small></button>';
  }).join('')+'</div>';
}
function pintarInicio(){
  const rutas=[['ex_consulta','ex_consulta_sub','continuarCaso()'],['ex_estudio','ex_estudio_sub','iniciarEstudio()'],['ex_quiz','ex_quiz_sub','abrirQuiz()']];
  return '<div class="ex-hero"><p class="ex-eyebrow">'+esc(TR('ex_eyebrow'))+'</p><h1>'+esc(TR('ex_title'))+'</h1><p class="sub">'+esc(TR('ex_intro'))+'</p></div>'+
    '<div class="ex-paths">'+rutas.map(r=>'<button class="ex-path" onclick="'+r[2]+'"><strong>'+esc(TR(r[0]))+'</strong><span>'+esc(TR(r[1]))+'</span><i>'+esc(TR('ex_start'))+'</i></button>').join('')+'</div>'+
    (hayCaso()?'<div class="ex-row"><button class="ex-button primary" onclick="continuarCaso()">'+esc(TR('ex_continue',{n:S.paso}))+'</button><button class="ex-button" onclick="nuevoCaso()">'+esc(TR('ex_new'))+'</button></div>':'')+
    '<p class="ex-muted">'+esc(TR('ex_local'))+'</p>'+(!S.guardado?'<p class="ex-status warning">'+esc(TR('ex_storage_error'))+'</p>':'')+
    '<details class="ex-guide"'+(!hayCaso()?' open':'')+'><summary>'+esc(TR('ex_guide'))+'</summary><ol>'+['ex_g1','ex_g2','ex_g3','ex_g4'].map(k=>'<li>'+esc(TR(k))+'</li>').join('')+'</ol></details>'+
    '<section><h2>'+esc(TR('ex_map'))+'</h2><p class="ex-muted">'+esc(TR('ex_map_note'))+'</p>'+mapaPasos('irPaso')+'</section>'+
    '<div class="ex-row"><button class="ex-button" onclick="verCasos()">'+esc(TR('ex_failures'))+'</button><button class="ex-button" onclick="verBiblioteca()">'+esc(TR('biblioteca'))+'</button></div>';
}
function campoNota(campo,clave){return '<label>'+esc(TR(clave))+'<textarea maxlength="2000" oninput="guardarNota(\''+campo+'\',this.value)">'+esc(notaPaso(S.paso)[campo]||'')+'</textarea></label>';}
function pintarRazonamiento(){
  const el=document.getElementById('razonamiento');if(!el)return;
  el.innerHTML=(estadoPaso(S.paso).estado==='revisar'?'<div class="alerta a-advertencia"><p>'+esc(TR('ex_review_note'))+'</p><button class="ex-button" onclick="confirmarRevision()">'+esc(TR('ex_review_done'))+'</button></div>':'')+
    (S.paso===1?'<details class="ex-journal" open><summary>'+esc(TR('ex_case'))+'</summary><div class="dbody"><p class="ex-muted">'+esc(TR('ex_context_help'))+'</p><div class="ex-fields"><label class="wide">'+esc(TR('ex_context'))+'<textarea maxlength="1500" oninput="guardarContexto(this.value)">'+esc(S.contextoCaso)+'</textarea></label></div></div></details>':'')+
    '<details class="ex-journal"><summary>'+esc(TR('ex_journal'))+'</summary><div class="dbody"><p class="ex-muted">'+esc(TR('ex_user'))+'</p><div class="ex-fields">'+campoNota('datos','ex_data')+campoNota('interpretacion','ex_meaning')+campoNota('justificacion','ex_why')+campoNota('faltante','ex_missing')+'</div></div></details><p id="ex-save" class="ex-status" role="status"></p>';
  actualizarGuardado();
}
function notasResumen(n){
  const nota=notaPaso(n);const campos=[['datos','ex_data'],['interpretacion','ex_meaning'],['justificacion','ex_why'],['faltante','ex_missing']];
  return '<div class="ex-notes">'+campos.filter(([k])=>nota[k]).map(([k,t])=>'<h4>'+esc(TR(t))+'</h4><p class="ex-note">'+esc(nota[k])+'</p>').join('')+'</div>';
}
function fuentesPaso(n){
  const p=pasoDe(n), ids=[...new Set((p.refs||[]).concat(...p.evidencia.map(e=>e.refs||[])))];
  return '<p class="ex-reference">'+esc(TR('ex_source',{version:VERSION}))+'</p><details><summary>'+esc(TR('ex_sources'))+'</summary><div class="dbody">'+ids.map(id=>{
    const r=REFS[id];if(!r)return '';const u=urlRef(r);return '<p class="ex-reference">'+(u?'<a href="'+esc(u)+'" target="_blank" rel="noopener">'+esc(r.cita)+'</a>':esc(r.cita))+'</p>';
  }).join('')+'</div></details>';
}
function leidos(){return objetoGuardado(CLAVE_ESTUDIO);}
function marcarLeido(){
  const h=leidos();h[S.paso]={cuando:Date.now()};
  try{localStorage.setItem(CLAVE_ESTUDIO,JSON.stringify(h));S.guardado=true;}catch(e){S.guardado=false;}
  pintarEstudio();actualizarGuardado();
}
function encajaBloque(b,tipo){
  if(tipo==='tablas')return b.tipo==='tabla';
  if(tipo==='perlas')return b.tipo==='recuadro'||b.tipo==='parrafo';
  if(tipo==='errores')return /error|mistake|pitfall|trampa|trap/i.test(b.titulo||'')||b.variante==='error';
  return true;
}
function pintarEstudio(){
  const el=document.getElementById('studytools');if(!el)return;
  el.classList.toggle('oculto',S.modo!=='estudio');
  el.innerHTML='<h2>'+esc(TR('ex_study_sections'))+'</h2>'+[['todo','ex_all'],['tablas','ex_tables'],['perlas','ex_pearls'],['errores','ex_errors']].map(([f,k])=>'<button class="ex-button" aria-pressed="'+(S.filtroEstudio===f)+'" onclick="filtrarEstudio(\''+f+'\')">'+esc(TR(k))+'</button>').join('')+
    '<div class="ex-row"><button class="ex-button" onclick="marcarLeido()">'+esc(TR(leidos()[S.paso]?'ex_read_done':'ex_read'))+'</button><button class="ex-button primary" onclick="abrirQuiz('+S.paso+')">'+esc(TR('ex_quiz'))+'</button></div><p class="ex-muted">'+esc(TR('ex_read_note'))+'</p>';
}
function filtrarEstudio(tipo){
  S.filtroEstudio=tipo;
  document.getElementById('desarrollo').innerHTML=P.esencial.filter(b=>encajaBloque(b,tipo)).map(bloque).join('')||'<p class="ex-muted">'+esc(TR('ex_no_results'))+'</p>';
  document.getElementById('detdes').open=true;tiraPintar();pintarEstudio();
}
function verBiblioteca(){S.vista='biblioteca';render();window.scrollTo(0,0);}
function pintarBiblioteca(){
  return '<h1>'+esc(TR('biblioteca'))+'</h1><p class="sub">'+esc(TR('ex_library_sub'))+'</p><button class="ex-button" onclick="modo(\'consulta\');irPaso(2)">'+esc(TR('ex_ao'))+'</button><div class="ex-search"><label>'+esc(TR('ex_search'))+'<input type="search" id="libquery" oninput="buscarBiblioteca()"></label><label>'+esc(TR('ex_type'))+'<select id="libtype" onchange="buscarBiblioteca()"><option value="todo">'+esc(TR('ex_all'))+'</option><option value="tablas">'+esc(TR('ex_tables'))+'</option><option value="perlas">'+esc(TR('ex_pearls'))+'</option><option value="errores">'+esc(TR('ex_errors'))+'</option></select></label></div><p id="libcount" class="ex-live" role="status"></p><div id="libresults"></div>';
}
function resultadosBiblioteca(q,tipo){
  const terminos=sinTildes(q).trim().split(/\s+/).filter(Boolean);const resultados=[];
  for(const n of DISPONIBLES)pasoDe(n).esencial.forEach((b,i)=>{
    if(!encajaBloque(b,tipo))return;
    const texto=sinTildes([b.titulo,b.texto,...(b.items||[]),...(b.encabezados||[]),...(b.filas||[]).flat()].filter(Boolean).join(' '));
    if(terminos.every(t=>texto.includes(t)))resultados.push({n,i,b});
  });return resultados;
}
function buscarBiblioteca(){
  const q=document.getElementById('libquery'),t=document.getElementById('libtype'),out=document.getElementById('libresults');if(!out)return;
  const r=resultadosBiblioteca(q?q.value:'',t?t.value:'todo');
  document.getElementById('libcount').textContent=TR('ex_results',{n:r.length});
  out.innerHTML=r.map(({n,i,b})=>'<details><summary>'+esc(n+'. '+tituloPaso(n)+' · '+(b.titulo||TR('ex_pearls')))+'</summary><div class="dbody">'+(b.tipo==='tiraTornillos'?'<p>'+esc(b.titulo||'')+'</p>':bloque(b))+'<button class="ex-button" onclick="abrirBloque('+n+','+i+')">'+esc(TR('ex_open'))+'</button></div></details>').join('')||'<p class="ex-muted">'+esc(TR('ex_no_results'))+'</p>';
}
function abrirBloque(n,i){S.modo='estudio';irPaso(n);document.getElementById('detdes').open=true;document.getElementById('desarrollo').innerHTML=P.esencial.map((b,k)=>'<div id="bloque-'+k+'">'+bloque(b)+'</div>').join('');tiraPintar();const el=document.getElementById('bloque-'+i);if(el&&el.scrollIntoView)el.scrollIntoView({block:'center'});}
function statsPaso(n){
  const h=histQuiz()['p'+n]||{},qs=DATA.pasos[n].autoevaluacion;
  const entradas=qs.map((q,i)=>h[i]).filter(v=>objeto(v)&&typeof v.bien==='boolean');
  return {respondidas:entradas.length,correctas:entradas.filter(v=>v.bien).length,intentos:entradas.reduce((a,v)=>a+(Number.isSafeInteger(v.intentos)&&v.intentos>0?v.intentos:1),0)};
}
function verProgreso(){S.vista='progreso';render();window.scrollTo(0,0);}
function pintarProgreso(){
  const lecturas=leidos(),stats=DISPONIBLES.map(statsPaso),total=stats.reduce((a,s)=>a+s.respondidas,0),bien=stats.reduce((a,s)=>a+s.correctas,0);
  return '<h1>'+esc(TR('progreso'))+'</h1><p class="sub">'+esc(TR('ex_progress_sub'))+'</p><div class="ex-metrics">'+[[DISPONIBLES.filter(n=>lecturas[n]).length+'/10','ex_read_count'],[total,'ex_answer_count'],[total?Math.round(100*bien/total)+'%':'—','ex_correct_count']].map(([v,k])=>'<div class="ex-metric"><b>'+esc(v)+'</b><span>'+esc(TR(k))+'</span></div>').join('')+'</div><p class="ex-muted">'+esc(TR('ex_stats_note'))+'</p><div class="tscroll ex-stats"><table><thead><tr>'+['ex_step','ex_reading','ex_answers','ex_attempts','ex_review_errors'].map(k=>'<th>'+esc(TR(k))+'</th>').join('')+'</tr></thead><tbody>'+DISPONIBLES.map((n,i)=>'<tr><td><button class="vermas" onclick="S.modo=\'estudio\';irPaso('+n+')">'+n+'. '+esc(tituloPaso(n))+'</button></td><td>'+esc(TR(lecturas[n]?'ex_read_done':'ex_pending'))+'</td><td>'+stats[i].correctas+' / '+stats[i].respondidas+'</td><td>'+stats[i].intentos+'</td><td>'+(falladas(n).length?'<button class="vermas" onclick="abrirQuiz('+n+',true)">'+esc(TR('ex_review_errors'))+' ('+falladas(n).length+')</button>':'—')+'</td></tr>').join('')+'</tbody></table></div><p class="ex-muted">'+esc(TR('ex_local'))+'</p>';
}
function abrirQuiz(n,fallos){
  S.quizPaso=DISPONIBLES.includes(n)?n:S.paso;S.quizRespuestas={};S.quizSoloFallos=!!fallos;
  S.quizIndices=S.quizSoloFallos?falladas(S.quizPaso):DATA.pasos[S.quizPaso].autoevaluacion.map((_,i)=>i);
  S.vista='quiz';render();window.scrollTo(0,0);
}
function responderQuiz(i,j){
  const q=DATA.pasos[S.quizPaso].autoevaluacion[i];
  if(!q||!S.quizIndices.includes(i)||!Number.isInteger(j)||j<0||j>=q.opciones.length||S.quizRespuestas[i]!==undefined)return;
  S.quizRespuestas[i]=j;anotaQuiz(S.quizPaso,i,j===q.correcta);
  // Conserva posición de lectura al actualizar el bloque y el marcador.
  render();
  const feedback=document.getElementById('quiz-feedback-'+i);if(feedback&&feedback.focus)feedback.focus({preventScroll:true});
}
function pintarQuiz(){
  const n=S.quizPaso,p=pasoDe(n),indices=S.quizIndices||p.autoevaluacion.map((_,i)=>i),respondidas=Object.keys(S.quizRespuestas),bien=respondidas.filter(i=>S.quizRespuestas[i]===p.autoevaluacion[i].correcta).length;
  return '<h1>'+esc(TR('ex_quiz'))+'</h1><p class="sub">'+esc(TR('ex_quiz_intro'))+'</p><div class="ex-row">'+DISPONIBLES.map(k=>'<button class="ex-button" aria-pressed="'+(k===n)+'" onclick="abrirQuiz('+k+')">'+k+'. '+esc(tituloPaso(k))+'</button>').join('')+'</div><h2>'+n+'. '+esc(tituloPaso(n))+'</h2><p role="status" class="ex-live">'+esc(TR('ex_quiz_count',{a:respondidas.length,b:indices.length,c:bien}))+'</p>'+
    indices.map(i=>{const q=p.autoevaluacion[i],r=S.quizRespuestas[i],respondida=r!==undefined;return '<div class="q ex-quiz"><p>'+(i+1)+'. '+esc(q.pregunta)+'</p>'+q.opciones.map((o,j)=>'<button '+(respondida?'disabled ':'')+'class="'+(respondida&&j===q.correcta?'bien':respondida&&j===r?'mal':'')+'" onclick="responderQuiz('+i+','+j+')">'+esc(o)+'</button>').join('')+(respondida?'<div class="ex-feedback" id="quiz-feedback-'+i+'" tabindex="-1"><b>'+esc(TR(r===q.correcta?'ex_correct':'ex_incorrect'))+'</b><p>'+esc(TR('ex_correct_answer',{answer:q.opciones[q.correcta]}))+'</p><p>'+esc(q.explicacion)+'</p><button class="ex-button" onclick="S.modo=\'estudio\';irPaso('+n+')">'+esc(TR('ex_estudio'))+'</button></div>':'')+'</div>';}).join('')+
    (!indices.length?'<p class="ex-muted">'+esc(TR('ex_no_errors'))+'</p>':'')+
    (indices.length&&respondidas.length===indices.length?'<p class="ex-muted">'+esc(TR('ex_quiz_complete'))+'</p>':'')+
    '<div class="ex-row"><button class="ex-button" onclick="abrirQuiz('+n+',true)">'+esc(TR('ex_review_errors'))+'</button><button class="ex-button" onclick="abrirQuiz('+n+')">'+esc(TR('ex_try_again'))+'</button><button class="ex-button" onclick="verProgreso()">'+esc(TR('progreso'))+'</button></div>'+fuentesPaso(n)+(!S.guardado?'<p class="ex-status warning">'+esc(TR('ex_storage_error'))+'</p>':'');
}
function copiarEnlace(){
  escribirHash();const url=location.href;const el=document.getElementById('share-status');
  const ok=()=>{if(el)el.textContent=TR('ex_copied');};
  const fail=()=>{if(el)el.textContent=TR('ex_copy_failed');};
  if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(url).then(ok,fail);else fail();
}
function pintarExperiencia(){
  const nav=document.getElementById('ex-nav');if(nav)nav.innerHTML=[['inicio','irInicio()'],['biblioteca','verBiblioteca()'],['ex_quiz','abrirQuiz()'],['progreso','verProgreso()']].map(([k,a])=>'<button onclick="'+a+'">'+esc(TR(k))+'</button>').join('');
  const barra=document.querySelector('.barra');if(barra)barra.classList.toggle('oculto',['inicio','quiz','biblioteca','progreso'].includes(S.vista));
  const pasos=document.querySelector('.pasos');if(pasos)pasos.classList.toggle('oculto',S.vista==='inicio');
  const cc=document.getElementById('chipcasos');if(cc)cc.textContent=TR('ex_failures');
  const skip=document.getElementById('skip');if(skip)skip.textContent=TR('ex_skip');
}
