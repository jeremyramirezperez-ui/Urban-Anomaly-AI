class ZonaVisual {
  constructor(opciones) {
    this.contenedor = opciones.contenedor;
    this.elementoCamara = opciones.elementoCamara;
    this.editable = Boolean(opciones.editable);
    this.color = opciones.color || '#e63946';
    this.onCambio = typeof opciones.onCambio === 'function' ? opciones.onCambio : null;

    this.zona = null; // coordenadas reales {x1,y1,x2,y2} en resolución nativa de la cámara
    this.TAM_MANEJADOR = 10; // tamaño en px del cuadro de redimensionado
    this._arrastre = null;

    this._crearCanvas();
    this._enlazarEventos();

    this._observador = new ResizeObserver(() => this._redimensionarCanvas());
    this._observador.observe(this.contenedor);
  }

  _crearCanvas() {
    this.canvas = document.createElement('canvas');
    this.canvas.className = 'zona-visual-canvas';
    this.canvas.style.position = 'absolute';
    this.canvas.style.top = '0';
    this.canvas.style.left = '0';
    this.canvas.style.width = '100%';
    this.canvas.style.height = '100%';
    this.canvas.style.pointerEvents = this.editable ? 'auto' : 'none';
    this.canvas.style.cursor = this.editable ? 'crosshair' : 'default';
    this.ctx = this.canvas.getContext('2d');

    const posicionActual = getComputedStyle(this.contenedor).position;
    if (posicionActual === 'static') {
      this.contenedor.style.position = 'relative';
    }
    this.contenedor.appendChild(this.canvas);
    this._redimensionarCanvas();
  }

  _redimensionarCanvas() {
    const ancho = this.contenedor.clientWidth;
    const alto = this.contenedor.clientHeight;
    if (ancho === 0 || alto === 0) return;
    this.canvas.width = ancho;
    this.canvas.height = alto;
    this._redibujar();
  }

  _dimensionesNativas() {
    const el = this.elementoCamara;
    if (!el) return { ancho: this.canvas.width, alto: this.canvas.height };
    if (el.tagName === 'VIDEO' && el.videoWidth) {
      return { ancho: el.videoWidth, alto: el.videoHeight };
    }
    if (el.tagName === 'IMG' && el.naturalWidth) {
      return { ancho: el.naturalWidth, alto: el.naturalHeight };
    }
    return { ancho: el.clientWidth || this.canvas.width, alto: el.clientHeight || this.canvas.height };
  }

  _realAMostrado(coordReal) {
    const nativa = this._dimensionesNativas();
    const escalaX = nativa.ancho > 0 ? this.canvas.width / nativa.ancho : 1;
    const escalaY = nativa.alto > 0 ? this.canvas.height / nativa.alto : 1;
    return {
      x1: coordReal.x1 * escalaX,
      y1: coordReal.y1 * escalaY,
      x2: coordReal.x2 * escalaX,
      y2: coordReal.y2 * escalaY,
    };
  }

  _mostradoAReal(coordMostrado) {
    const nativa = this._dimensionesNativas();
    const escalaX = this.canvas.width > 0 ? nativa.ancho / this.canvas.width : 1;
    const escalaY = this.canvas.height > 0 ? nativa.alto / this.canvas.height : 1;
    return {
      x1: Math.round(coordMostrado.x1 * escalaX),
      y1: Math.round(coordMostrado.y1 * escalaY),
      x2: Math.round(coordMostrado.x2 * escalaX),
      y2: Math.round(coordMostrado.y2 * escalaY),
    };
  }

  _posicionDesdeEvento(evento) {
    const rect = this.canvas.getBoundingClientRect();
    return { x: evento.clientX - rect.left, y: evento.clientY - rect.top };
  }

  _enlazarEventos() {
    if (!this.editable) return;
    this.canvas.addEventListener('pointerdown', (e) => this._alPresionar(e));
    window.addEventListener('pointermove', (e) => this._alMover(e));
    window.addEventListener('pointerup', () => this._alSoltar());
  }

  _zonaMostradaActual() {
    if (!this.zona) return null;
    return this._realAMostrado(this.zona);
  }

  _manejadorEnPosicion(pos, zonaMostrada) {
    const m = this.TAM_MANEJADOR;
    const esquinas = {
      'sup-izq': { x: zonaMostrada.x1, y: zonaMostrada.y1 },
      'sup-der': { x: zonaMostrada.x2, y: zonaMostrada.y1 },
      'inf-izq': { x: zonaMostrada.x1, y: zonaMostrada.y2 },
      'inf-der': { x: zonaMostrada.x2, y: zonaMostrada.y2 },
    };
    for (const [nombre, punto] of Object.entries(esquinas)) {
      if (Math.abs(pos.x - punto.x) <= m && Math.abs(pos.y - punto.y) <= m) return nombre;
    }
    return null;
  }

  _dentroDeZona(pos, zonaMostrada) {
    return pos.x >= zonaMostrada.x1 && pos.x <= zonaMostrada.x2 &&
           pos.y >= zonaMostrada.y1 && pos.y <= zonaMostrada.y2;
  }

  _alPresionar(evento) {
    evento.preventDefault();
    const pos = this._posicionDesdeEvento(evento);
    const zonaMostrada = this._zonaMostradaActual();

    if (zonaMostrada) {
      const manejador = this._manejadorEnPosicion(pos, zonaMostrada);
      if (manejador) {
        this._arrastre = { modo: 'redimensionar', manejador, zonaInicial: { ...zonaMostrada } };
        return;
      }
      if (this._dentroDeZona(pos, zonaMostrada)) {
        this._arrastre = {
          modo: 'mover',
          offsetX: pos.x - zonaMostrada.x1,
          offsetY: pos.y - zonaMostrada.y1,
          ancho: zonaMostrada.x2 - zonaMostrada.x1,
          alto: zonaMostrada.y2 - zonaMostrada.y1,
        };
        return;
      }
    }
    // Clic fuera de la zona existente (o sin zona aún): empieza a dibujar una nueva
    this._arrastre = { modo: 'dibujar', inicioX: pos.x, inicioY: pos.y };
    this.zona = this._mostradoAReal({ x1: pos.x, y1: pos.y, x2: pos.x, y2: pos.y });
  }

  _alMover(evento) {
    if (!this._arrastre) return;
    const pos = this._posicionDesdeEvento(evento);
    const maxX = this.canvas.width;
    const maxY = this.canvas.height;
    const limitar = (v, max) => Math.max(0, Math.min(v, max));

    if (this._arrastre.modo === 'dibujar') {
      const nueva = {
        x1: Math.min(this._arrastre.inicioX, pos.x),
        y1: Math.min(this._arrastre.inicioY, pos.y),
        x2: Math.max(this._arrastre.inicioX, pos.x),
        y2: Math.max(this._arrastre.inicioY, pos.y),
      };
      this.zona = this._mostradoAReal(nueva);
    } else if (this._arrastre.modo === 'mover') {
      const x1 = limitar(pos.x - this._arrastre.offsetX, maxX - this._arrastre.ancho);
      const y1 = limitar(pos.y - this._arrastre.offsetY, maxY - this._arrastre.alto);
      this.zona = this._mostradoAReal({
        x1, y1, x2: x1 + this._arrastre.ancho, y2: y1 + this._arrastre.alto,
      });
    } else if (this._arrastre.modo === 'redimensionar') {
      const z = { ...this._arrastre.zonaInicial };
      const px = limitar(pos.x, maxX);
      const py = limitar(pos.y, maxY);
      if (this._arrastre.manejador.includes('izq')) z.x1 = px;
      if (this._arrastre.manejador.includes('der')) z.x2 = px;
      if (this._arrastre.manejador.includes('sup')) z.y1 = py;
      if (this._arrastre.manejador.includes('inf')) z.y2 = py;
      this.zona = this._mostradoAReal({
        x1: Math.min(z.x1, z.x2), y1: Math.min(z.y1, z.y2),
        x2: Math.max(z.x1, z.x2), y2: Math.max(z.y1, z.y2),
      });
    }
    this._redibujar();
  }

  _alSoltar() {
    if (!this._arrastre) return;
    this._arrastre = null;
    if (this.zona && this.onCambio) this.onCambio({ ...this.zona });
  }

  _redibujar() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    if (!this.zona) return;

    const z = this._realAMostrado(this.zona);
    const ancho = z.x2 - z.x1;
    const alto = z.y2 - z.y1;

    this.ctx.fillStyle = this.color + '33';
    this.ctx.fillRect(z.x1, z.y1, ancho, alto);
    this.ctx.strokeStyle = this.color;
    this.ctx.lineWidth = 2;
    this.ctx.strokeRect(z.x1, z.y1, ancho, alto);

    if (this.editable) {
      this.ctx.fillStyle = this.color;
      const m = this.TAM_MANEJADOR;
      [[z.x1, z.y1], [z.x2, z.y1], [z.x1, z.y2], [z.x2, z.y2]].forEach(([x, y]) => {
        this.ctx.fillRect(x - m / 2, y - m / 2, m, m);
      });
    }
  }

  /** Carga coordenadas reales guardadas (ej. desde la API al cargar la página) */
  cargarZona(coordenadas) {
    this.zona = coordenadas
      ? { x1: coordenadas.x1, y1: coordenadas.y1, x2: coordenadas.x2, y2: coordenadas.y2 }
      : null;
    this._redibujar();
  }

  /** Devuelve las coordenadas reales actuales {x1,y1,x2,y2} o null si no hay zona */
  obtenerZona() {
    return this.zona ? { ...this.zona } : null;
  }

  limpiarZona() {
    this.zona = null;
    this._redibujar();
    if (this.onCambio) this.onCambio(null);
  }

  destruir() {
    this._observador.disconnect();
    this.canvas.remove();
  }
}