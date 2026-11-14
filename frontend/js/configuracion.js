document.addEventListener('DOMContentLoaded', async () => {
  const form = document.querySelector('#form-configuracion');
  const mensaje = document.querySelector('#mensaje');
  const contenedor = document.getElementById('contenedor-camara');
  const camara = document.getElementById('vista-camara');

  const inX1 = document.querySelector('input[name="zonaX1"]');
  const inY1 = document.querySelector('input[name="zonaY1"]');
  const inX2 = document.querySelector('input[name="zonaX2"]');
  const inY2 = document.querySelector('input[name="zonaY2"]');

  let zonaVisual = null;

  // Conserva la configuración cargada desde el backend.
  // Esto permite mantener valores que después no estarán visibles
  // en el formulario, como los parámetros antiguos de caída y
  // la distancia interna para objetos abandonados.
  let configuracionActual = {};

  // Inicializar el dibujador sobre la cámara
  if (contenedor && camara) {
    zonaVisual = new ZonaVisual({
      contenedor: contenedor,
      elementoCamara: camara,
      editable: true,
      color: '#e63946',
      onCambio: (coord) => {
        if (!coord) return;

        const ancho = camara.clientWidth || contenedor.clientWidth;
        const alto = camara.clientHeight || contenedor.clientHeight;

        if (ancho > 0 && alto > 0) {
          inX1.value = (coord.x1 / ancho).toFixed(2);
          inY1.value = (coord.y1 / alto).toFixed(2);
          inX2.value = (coord.x2 / ancho).toFixed(2);
          inY2.value = (coord.y2 / alto).toFixed(2);
        }
      }
    });
  }

  function llenar(c) {
    Object.entries(c).forEach(([k, v]) => {
      const e = document.querySelector(`[name="${k}"]`);

      if (!e) return;

      if (e.type === 'checkbox') {
        e.checked = Boolean(v);
      } else {
        e.value = v;
      }
    });

    // Dibujar recuadro en pantalla si ya existían coordenadas guardadas
    if (zonaVisual && c.zonaX1 !== undefined && camara) {
      const ancho = camara.clientWidth || contenedor.clientWidth;
      const alto = camara.clientHeight || contenedor.clientHeight;

      if (ancho > 0 && alto > 0) {
        zonaVisual.cargarZona({
          x1: c.zonaX1 * ancho,
          y1: c.zonaY1 * alto,
          x2: c.zonaX2 * ancho,
          y2: c.zonaY2 * alto
        });
      }
    }
  }

  function obtenerCheckbox(nombre, valorRespaldo = false) {
    const elemento = document.querySelector(
      `input[name="${nombre}"]`
    );

    if (!elemento) {
      return Boolean(valorRespaldo);
    }

    return elemento.checked;
  }

  function obtenerNumeroFormulario(
    formData,
    nombre,
    valorRespaldo
  ) {
    const valor = formData.get(nombre);

    if (
      valor === null ||
      valor === undefined ||
      valor === ''
    ) {
      return Number(valorRespaldo);
    }

    return Number(valor);
  }

  // Cargar datos actuales desde el backend
  try {
    const config = await API.get('/api/configuracion');

    configuracionActual = {
      ...config
    };

    llenar(config);
  } catch (e) {
    API.mostrarMensaje(
      mensaje,
      e.message,
      'error'
    );
  }

  // Guardar datos
  form.addEventListener('submit', async (ev) => {
    ev.preventDefault();

    const f = new FormData(form);

    const datos = {
      nombreZona: f.get('nombreZona'),

      limitePersonas: Number(
        f.get('limitePersonas')
      ),

      segundosPermanencia: Number(
        f.get('segundosPermanencia')
      ),

      cooldownSegundos: Number(
        f.get('cooldownSegundos')
      ),

      confianzaMinima: Number(
        f.get('confianzaMinima')
      ),

      alertasActivas: obtenerCheckbox(
        'alertasActivas',
        configuracionActual.alertasActivas
      ),

      fuegoActivo: obtenerCheckbox(
        'fuegoActivo',
        configuracionActual.fuegoActivo
      ),

      // ---------------------------------------------------
      // Objetos abandonados
      // ---------------------------------------------------

      objetoAbandonadoActivo: obtenerCheckbox(
        'objetoAbandonadoActivo',
        configuracionActual.objetoAbandonadoActivo
      ),

      segundosObjetoAbandonado: obtenerNumeroFormulario(
        f,
        'segundosObjetoAbandonado',
        configuracionActual.segundosObjetoAbandonado ?? 15
      ),

      // Se conserva internamente.
      // No es necesario mostrarlo en la interfaz.
      distanciaPersonaObjetoPx: Number(
        configuracionActual.distanciaPersonaObjetoPx ?? 150
      ),

      // ---------------------------------------------------
      // Compatibilidad con la configuración antigua de caída
      // ---------------------------------------------------
      // Estos valores se mantienen aunque los controles
      // desaparezcan visualmente del formulario.

      caidaActiva: obtenerCheckbox(
        'caidaActiva',
        configuracionActual.caidaActiva
      ),

      tiempoRiesgoCaida: obtenerNumeroFormulario(
        f,
        'tiempoRiesgoCaida',
        configuracionActual.tiempoRiesgoCaida ?? 5
      ),

      // ---------------------------------------------------
      // Zona restringida
      // ---------------------------------------------------

      zonaRestringidaActiva: obtenerCheckbox(
        'zonaRestringidaActiva',
        configuracionActual.zonaRestringidaActiva
      ),

      zonaX1: Number(
        f.get('zonaX1')
      ),

      zonaY1: Number(
        f.get('zonaY1')
      ),

      zonaX2: Number(
        f.get('zonaX2')
      ),

      zonaY2: Number(
        f.get('zonaY2')
      ),

      // ---------------------------------------------------
      // Horario
      // ---------------------------------------------------

      horarioActivo: obtenerCheckbox(
        'horarioActivo',
        configuracionActual.horarioActivo
      ),

      horaInicio: f.get('horaInicio'),
      horaFin: f.get('horaFin')
    };

    try {
      const actualizada = await API.putJson(
        '/api/configuracion',
        datos
      );

      // Mantener en memoria los últimos valores guardados.
      configuracionActual = {
        ...configuracionActual,
        ...datos,
        ...(actualizada || {})
      };

      API.mostrarMensaje(
        mensaje,
        "Configuración guardada.",
        "exito"
      );

      setTimeout(() => {
        mensaje.textContent = "";
        mensaje.className = "mensaje neutro";
      }, 1000);
    } catch (e) {
      API.mostrarMensaje(
        mensaje,
        e.message,
        'error'
      );
    }
  });
});