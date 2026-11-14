document.addEventListener("DOMContentLoaded", () => {
  const resumen = document.querySelector("#resumen");
  const graficoTipo = document.querySelector("#grafico-tipo");
  const graficoEstado = document.querySelector("#grafico-estado");
  const graficoNivel = document.querySelector("#grafico-nivel");
  const graficoEvolucion = document.querySelector("#grafico-evolucion");

  const btnActualizar = document.querySelector("#btn-actualizar");
  const btnFiltrar = document.querySelector("#btn-filtrar");
  const btnLimpiarFiltro = document.querySelector("#btn-limpiar-filtro");
  const filtroDesde = document.querySelector("#filtro-desde");
  const filtroHasta = document.querySelector("#filtro-hasta");

  function mostrarResumen(datos) {
    resumen.innerHTML = `
      <div class="tarjeta">
        <h3>${datos.total}</h3>
        <p>Total de alertas</p>
      </div>

      <div class="tarjeta">
        <h3>${datos.pendientes}</h3>
        <p>Pendientes</p>
      </div>

      <div class="tarjeta">
        <h3>${datos.tiposDistintos}</h3>
        <p>Tipos distintos</p>
      </div>
    `;
  }

  function renderizarBarras(contenedor, items, etiquetaVacio) {
    if (!items || items.length === 0) {
      contenedor.innerHTML = `<p class="db-vacio">${etiquetaVacio}</p>`;
      return;
    }

    const maximo = Math.max(...items.map((item) => item.cantidad), 1);

    contenedor.innerHTML = items
      .map((item) => {
        const porcentaje = Math.round((item.cantidad / maximo) * 100);

        return `
          <div class="db-fila">
            <span class="db-etiqueta">${item.etiqueta}</span>

            <div class="db-barra-fondo">
              <div
                class="db-barra-relleno"
                style="width: ${porcentaje}%"
              ></div>
            </div>

            <span class="db-cantidad">${item.cantidad}</span>
          </div>
        `;
      })
      .join("");
  }

  function formatearFechaLocal(fechaIso) {
    // "new Date('2026-08-05')" interpreta la fecha como UTC y, al mostrarla
    // en hora local (Costa Rica, UTC-6), la corre un día para atrás.
    // Armamos la fecha con año/mes/día explícitos para evitar eso.
    const [anio, mes, dia] = fechaIso.split("-").map(Number);
    return new Date(anio, mes - 1, dia).toLocaleDateString("es-CR");
  }

  function hayFiltroActivo() {
    return Boolean(filtroDesde.value || filtroHasta.value);
  }

  function mensajeVacio() {
    return hayFiltroActivo()
      ? "No se registraron alertas en el rango de fechas seleccionado."
      : "No hay alertas registradas todavía.";
  }

  function renderizarEvolucion(contenedor, puntos) {
    if (!puntos || puntos.length === 0) {
      contenedor.innerHTML = `<p class="db-vacio">${mensajeVacio()}</p>`;
      return;
    }

    const items = puntos.map((punto) => ({
      etiqueta: formatearFechaLocal(punto.dia),
      cantidad: punto.cantidad,
    }));

    renderizarBarras(contenedor, items, mensajeVacio());
  }

  function construirQuery() {
    const parametros = new URLSearchParams();

    if (filtroDesde.value) {
      parametros.set("fechaDesde", filtroDesde.value);
    }

    if (filtroHasta.value) {
      parametros.set("fechaHasta", filtroHasta.value);
    }

    const query = parametros.toString();
    return query ? `?${query}` : "";
  }

  async function cargar() {
    try {
      btnActualizar.disabled = true;
      btnActualizar.textContent = "Actualizando...";

      const datos = await API.get(`/api/dashboard${construirQuery()}`);

      mostrarResumen(datos);
      renderizarBarras(graficoTipo, datos.porTipo, mensajeVacio());
      renderizarBarras(graficoEstado, datos.porEstado, mensajeVacio());
      renderizarBarras(graficoNivel, datos.porNivel, mensajeVacio());
      renderizarEvolucion(graficoEvolucion, datos.evolucionDiaria);
    } catch (error) {
      console.error("Error al cargar el dashboard:", error);

      resumen.innerHTML = `<p class="db-vacio">No fue posible cargar las estadísticas.</p>`;
    } finally {
      btnActualizar.disabled = false;
      btnActualizar.textContent = "Actualizar";
    }
  }

  btnActualizar.addEventListener("click", cargar);
  btnFiltrar.addEventListener("click", cargar);

  btnLimpiarFiltro.addEventListener("click", () => {
    filtroDesde.value = "";
    filtroHasta.value = "";
    cargar();
  });

  cargar();
});