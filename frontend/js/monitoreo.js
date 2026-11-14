document.addEventListener('DOMContentLoaded', async () => {
  const video=document.querySelector('#video'), captura=document.querySelector('#captura'), overlay=document.querySelector('#overlay');
  const gestor=new GestorCamara(video,captura); const ctx=overlay.getContext('2d');
  const btnIniciar=document.querySelector('#btn-iniciar'), btnDetener=document.querySelector('#btn-detener');
  const cantidad=document.querySelector('#cantidad'), limite=document.querySelector('#limite'), motor=document.querySelector('#motor'), estado=document.querySelector('#estado');
  const mensaje=document.querySelector('#mensaje-monitoreo'), lista=document.querySelector('#lista-eventos'), vacio=document.querySelector('#visor-vacio');
  let intervalo=null, ocupado=false, configuracion=null;

  async function cargarConfiguracion(){ configuracion=await API.get('/api/configuracion'); limite.textContent=configuracion.limitePersonas; }
  function ajustarOverlay(){ overlay.width=video.clientWidth; overlay.height=video.clientHeight; }
  function dibujar(deteccion){ ajustarOverlay(); ctx.clearRect(0,0,overlay.width,overlay.height); if(!deteccion)return;
    const sx=overlay.width/deteccion.anchoImagen, sy=overlay.height/deteccion.altoImagen;
    if(configuracion?.zonaRestringidaActiva){ctx.strokeStyle='#ff9f0a';ctx.lineWidth=3;ctx.setLineDash([8,5]);ctx.strokeRect(configuracion.zonaX1*overlay.width,configuracion.zonaY1*overlay.height,(configuracion.zonaX2-configuracion.zonaX1)*overlay.width,(configuracion.zonaY2-configuracion.zonaY1)*overlay.height);ctx.setLineDash([]);}
    deteccion.personas.forEach(p=>{const b=p.caja;ctx.strokeStyle='#00e676';ctx.lineWidth=3;ctx.strokeRect(b.x1*sx,b.y1*sy,(b.x2-b.x1)*sx,(b.y2-b.y1)*sy);ctx.fillStyle='#00e676';ctx.font='bold 15px Arial';ctx.fillText(`Persona ${p.idSeguimiento} · ${Math.round(p.confianza*100)}%`,b.x1*sx+4,Math.max(18,b.y1*sy-5));(deteccion.fuegoCajas||[]).forEach(b=>{ctx.strokeStyle='#ff1744';ctx.lineWidth=4;ctx.strokeRect(b.x1*sx,b.y1*sy,(b.x2-b.x1)*sx,(b.y2-b.y1)*sy);ctx.fillStyle='#ff1744';ctx.font='bold 16px Arial';ctx.fillText('FUEGO',b.x1*sx+4,Math.max(18,b.y1*sy-5));});});
  }
  function mostrarEventos(datos){lista.innerHTML='';[...(datos.eventos||[]),...(datos.alertas||[])].forEach(e=>{const div=document.createElement('div');div.className='evento';div.innerHTML=`<b>${e.titulo||e.tipo}</b><div>${e.mensaje}</div>`;lista.appendChild(div);});}
  async function enviarEstado(valor,motivo=''){try{await API.postJson('/api/camara/estado',{estado:valor,motivo,camaraId:'webcam-principal'});}catch(e){console.error(e)}}
  async function analizar(){if(ocupado)return;const blob=await gestor.capturar();if(!blob)return;ocupado=true;try{const form=new FormData();form.append('imagen',blob,'webcam.jpg');const datos=await API.solicitar('/api/deteccion/analizar',{method:'POST',body:form});cantidad.textContent=datos.deteccion.personasDetectadas;motor.textContent=datos.deteccion.motor;dibujar(datos.deteccion);mostrarEventos(datos);API.mostrarMensaje(mensaje,datos.alertas.length?'Se generó una alerta.':'Monitoreo activo.',''+(datos.alertas.length?'advertencia':'exito'));}catch(e){API.mostrarMensaje(mensaje,e.message,'error');}finally{ocupado=false;}}
  async function detener(motivo='La cámara fue apagada durante el monitoreo'){clearInterval(intervalo);intervalo=null;gestor.detener();ctx.clearRect(0,0,overlay.width,overlay.height);estado.textContent='APAGADA';cantidad.textContent='0';vacio.hidden=false;btnIniciar.disabled=false;btnDetener.disabled=true;await enviarEstado('APAGADA',motivo);}
  gestor.alTerminar=(motivo)=>detener(motivo);
  btnIniciar.addEventListener('click',async()=>{try{await gestor.iniciar();await cargarConfiguracion();vacio.hidden=true;estado.textContent='ACTIVA';btnIniciar.disabled=true;btnDetener.disabled=false;await enviarEstado('ACTIVA');await analizar();intervalo=setInterval(analizar,1200);API.mostrarMensaje(mensaje,'Cámara activa.','exito');}catch(e){API.mostrarMensaje(mensaje,e.message,'error');}});
  btnDetener.addEventListener('click',()=>detener()); window.addEventListener('resize',ajustarOverlay); await cargarConfiguracion();
});
