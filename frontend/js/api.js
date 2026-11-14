window.API = {
  async solicitar(ruta, opciones = {}) {
    const respuesta = await fetch(ruta, opciones);
    let datos;
    try { datos = await respuesta.json(); } catch { datos = { detail: await respuesta.text() }; }
    if (!respuesta.ok) throw new Error(datos.detail || datos.detalle || datos.mensaje || `Error ${respuesta.status}`);
    return datos;
  },
  get(ruta) { return this.solicitar(ruta); },
  postJson(ruta, datos) { return this.solicitar(ruta, {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(datos)}); },
  putJson(ruta, datos) { return this.solicitar(ruta, {method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(datos)}); },
  patchJson(ruta, datos) { return this.solicitar(ruta, {method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify(datos)}); },
  mostrarMensaje(elemento, texto, tipo='neutro') { elemento.className = `mensaje ${tipo}`; elemento.textContent = texto; }
};
