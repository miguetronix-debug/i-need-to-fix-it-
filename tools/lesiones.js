/* Un caso puede incluir varias lesiones. El motor siempre evalúa una lesión
   por vez: nunca se mezclan códigos, decisiones o alertas de huesos distintos. */
S.lesiones=[];S.lesionActiva=0;S.lado='';
const CAMPOS_LESION=['porPaso','notas','pendientes','revisar','paso','lado'];
function capturarLesion(){
  const out={};for(const k of CAMPOS_LESION)out[k]=S[k];
  return JSON.parse(JSON.stringify(out));
}
function aplicarLesion(lesion){
  const limpia=normalizarCaso(lesion);
  for(const k of CAMPOS_LESION)S[k]=k==='lado'?(['derecho','izquierdo','no-aplica'].includes(lesion.lado)?lesion.lado:''):limpia[k];
  S.dec=S.porPaso[S.paso];P=pasoDe(S.paso);
}
function lesionesDelCaso(){
  const lista=S.lesiones.slice();lista[S.lesionActiva]=capturarLesion();return lista;
}
function sincronizarLesion(){S.lesiones=lesionesDelCaso();}
function normalizarEpisodio(g){
  const base=normalizarCaso(g);
  const lista=objeto(g)&&Array.isArray(g.lesiones)&&g.lesiones.length?g.lesiones.filter(objeto):[g];
  const lesiones=(lista.length?lista:[{}]).map(l=>{
    const n=normalizarCaso(objeto(l)?l:{});return {porPaso:n.porPaso,notas:n.notas,pendientes:n.pendientes,revisar:n.revisar,paso:n.paso,
      lado:objeto(l)&&['derecho','izquierdo','no-aplica'].includes(l.lado)?l.lado:''};
  });
  const activa=objeto(g)&&Number.isInteger(g.lesionActiva)&&g.lesionActiva>=0&&g.lesionActiva<lesiones.length?g.lesionActiva:0;
  return {...base,...lesiones[activa],lesiones,lesionActiva:activa};
}
function lesionTieneDatos(l){
  return !!l.lado||Object.values(l.porPaso||{}).some(d=>Object.values(d||{}).some(v=>Array.isArray(v)?v.length:!!v))||
    Object.values(l.notas||{}).some(d=>Object.values(d||{}).some(v=>typeof v==='string'&&v.trim()))||
    Object.values(l.pendientes||{}).some(d=>Object.values(d||{}).some(Boolean));
}
function conLesion(l,i,fn){
  const anterior={};for(const k of CAMPOS_LESION)anterior[k]=S[k];
  const idx=S.lesionActiva,gP=P,gDec=S.dec;
  try{aplicarLesion(l);S.lesionActiva=i;return fn();}finally{
    for(const k of CAMPOS_LESION)S[k]=anterior[k];S.lesionActiva=idx;P=gP;
    // No usar la copia para S.dec: mantener la referencia que usaba el motor.
    S.dec=gDec;
  }
}
function nombreLesion(l,i){
  return conLesion(l,i,()=>conContexto(2,p=>{
    const d=S.porPaso[2]||{},bone=p.decisiones.find(x=>x.id==='hueso').opciones.find(o=>o.id===d.hueso);
    const codigo=codigoCanonico();
    return TR('fx_num',{n:i+1})+' · '+(bone?bone.etiqueta:TR('fx_sin_clasificar'))+(codigo?' · '+codigo:'')+
      (S.lado?' · '+TR('fx_'+S.lado):'');
  }));
}
function seleccionarLesion(i){
  if(!Number.isInteger(i)||i<0||i>=S.lesiones.length||i===S.lesionActiva)return;
  sincronizarLesion();S.lesionActiva=i;aplicarLesion(S.lesiones[i]);S.verCrit={};S.resp={};S.filtroEstudio='todo';
  S.vista='paso';guardar();cargar();window.scrollTo(0,0);
}
function agregarLesion(hueso){
  const opcion=DATA.pasos[2].decisiones.find(d=>d.id==='hueso').opciones.find(o=>o.id===hueso);
  sincronizarLesion();const nueva=normalizarCaso({paso:2,porPaso:opcion?{2:{hueso}}:{}});
  S.lesiones.push({...nueva,lado:''});S.lesionActiva=S.lesiones.length-1;aplicarLesion(S.lesiones[S.lesionActiva]);
  S.verCrit={};S.resp={};S.filtroEstudio='todo';S.vista='paso';guardar();cargar();window.scrollTo(0,0);
}
function eliminarLesion(){
  if(S.lesiones.length<=1||!confirm(TR('fx_confirm_eliminar',{n:S.lesionActiva+1})))return;
  sincronizarLesion();S.lesiones.splice(S.lesionActiva,1);S.lesionActiva=Math.min(S.lesionActiva,S.lesiones.length-1);
  aplicarLesion(S.lesiones[S.lesionActiva]);S.verCrit={};S.resp={};guardar();cargar();
}
function ladoLesion(lado){
  if(!['','derecho','izquierdo','no-aplica'].includes(lado))return;
  S.lado=lado;guardar();pintarLesiones();
}
function pintarLesiones(){
  const el=document.getElementById('lesiones');if(!el)return;
  const lista=lesionesDelCaso();
  const asociada={'h-2R':'h-2U','h-2U':'h-2R','h-4':'h-4F','h-4F':'h-4'}[(S.porPaso[2]||{}).hueso];
  const etiqueta={'h-2R':'fx_radio','h-2U':'fx_cubito','h-4':'fx_tibia','h-4F':'fx_perone'}[asociada];
  el.innerHTML='<h2>'+esc(TR('fx_titulo'))+'</h2><p class="ex-muted">'+esc(TR('fx_ayuda'))+'</p><div class="ex-row">'+
    lista.map((l,i)=>'<button class="ex-button'+(i===S.lesionActiva?' primary':'')+'" aria-pressed="'+(i===S.lesionActiva)+'" onclick="seleccionarLesion('+i+')">'+esc(nombreLesion(l,i))+'</button>').join('')+'</div>'+
    '<div class="ex-row"><button class="ex-button" onclick="agregarLesion()">'+esc(TR('fx_agregar'))+'</button>'+
    (asociada?'<button class="ex-button primary" onclick="agregarLesion(\''+asociada+'\')">'+esc(TR('fx_asociada',{hueso:TR(etiqueta)}))+'</button>':'')+
    (lista.length>1?'<button class="ex-button" onclick="eliminarLesion()">'+esc(TR('fx_eliminar'))+'</button>':'')+'</div>'+
    '<label class="fx-lado">'+esc(TR('fx_lado'))+' <select onchange="ladoLesion(this.value)">'+['','derecho','izquierdo','no-aplica'].map(k=>'<option value="'+k+'"'+(S.lado===k?' selected':'')+'>'+esc(TR(k?'fx_'+k:'fx_sin_lado'))+'</option>').join('')+'</select></label>';
}
function editarLesionPaso(i,n){seleccionarLesion(i);irPaso(n);}
function planTexto(){
  const lista=lesionesDelCaso();
  if(lista.length===1)return nombreLesion(lista[0],0)+'\n'+planTextoLesion();
  return TR('fx_plan')+'\n'+lista.map((l,i)=>nombreLesion(l,i)+'\n'+conLesion(l,i,planTextoLesion)).join('\n\n');
}
function pintarResumen(){
  const lista=lesionesDelCaso();
  if(lista.length===1)return pintarResumenLesion();
  return '<div class="resumen"><h1>'+esc(TR('fx_plan'))+'</h1><p class="sub">'+esc(TR('fx_resumen',{n:lista.length}))+'</p><div class="racc">'+
    '<button id="bcopiar" class="pri" onclick="copiarPlan()">'+esc(TR('b_copiar'))+'</button><button onclick="window.print()">'+esc(TR('b_imprimir'))+'</button><button onclick="copiarEnlace()">'+esc(TR('ex_share'))+'</button></div><p id="share-status" role="status"></p><p class="ex-muted">'+esc(TR('ex_share_note'))+'</p>'+
    lista.map((l,i)=>'<section class="fx-resumen"><h2>'+esc(nombreLesion(l,i))+'</h2>'+conLesion(l,i,()=>pintarResumenLesion(true))+'</section>').join('')+'</div>';
}
function hashLesiones(){
  sincronizarLesion();
  return '#fx='+encodeURIComponent(JSON.stringify({v:2,lesionActiva:S.lesionActiva,
    lesiones:S.lesiones.map(l=>({porPaso:l.porPaso,paso:l.paso,lado:l.lado}))}));
}
function leerLesionesHash(h){
  try{
    const g=JSON.parse(decodeURIComponent(h.slice(3)));
    if(g.v!==2||!Array.isArray(g.lesiones)||!g.lesiones.length)return null;
    // Se aceptan únicamente las opciones, posición y lado; nunca notas desde una URL.
    return {lesionActiva:g.lesionActiva,lesiones:g.lesiones.filter(objeto).map(l=>({porPaso:l.porPaso,paso:l.paso,lado:l.lado}))};
  }catch(e){return null;}
}
