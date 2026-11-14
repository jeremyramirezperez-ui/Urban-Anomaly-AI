document.addEventListener("DOMContentLoaded", () => {
  const tabla = document.querySelector("#tabla-alertas");
  const resumen = document.querySelector("#resumen");
  const btnActualizar = document.querySelector("#btn-actualizar");
  const btnAnterior = document.querySelector("#btn-anterior");
  const btnSiguiente = document.querySelector("#btn-siguiente");
  const informacionPagina = document.querySelector("#informacion-pagina");

  const alertasPorPagina = 10;

  let paginaActual = 1;
  let totalPaginas = 1;
  let totalRegistros = 0;

  async function cambiarEstado(id, estado) {
    try {
      await API.patchJson(
        `/api/alertas/${id}/estado`,
        { estado }
      );

      await cargar(paginaActual);
    } catch (error) {
      console.error("Error al cambiar el estado:", error);
      alert("No fue posible cambiar el estado de la alerta.");
    }
  }

  window.cambiarEstadoAlerta = cambiarEstado;

  function mostrarResumen(datos) {
    resumen.innerHTML = `
      <div class="tarjeta">
        <h3>${datos.total}</h3>
        <p>Total</p>
      </div>

      <div class="tarjeta">
        <h3>${datos.pendientes}</h3>
        <p>Pendientes</p>
      </div>

      <div class="tarjeta">
        <h3>${datos.porTipo.length}</h3>
        <p>Tipos</p>
      </div>
    `;
  }

  function mostrarAlertas(alertas) {
    if (!Array.isArray(alertas) || alertas.length === 0) {
      tabla.innerHTML = `
        <tr>
          <td colspan="7">
            No hay alertas registradas.
          </td>
        </tr>
      `;

      return;
    }

    tabla.innerHTML = alertas
      .map((alerta) => {
        const enlaceCaptura = alerta.capturaRuta
          ? `
            <br>
            <a
              href="${alerta.capturaRuta}"
              target="_blank"
              rel="noopener noreferrer"
            >
              Ver captura
            </a>
          `
          : "";

        return `
          <tr>
            <td>${alerta.id}</td>

            <td>${alerta.tipo}</td>

            <td>
              ${alerta.mensaje}
              ${enlaceCaptura}
            </td>

            <td>
              ${new Date(alerta.fechaHora).toLocaleString("es-CR")}
            </td>

            <td>
              ${alerta.estadoCorreo || "--"}
            </td>

            <td>
              <span class="estado">
                ${alerta.estado}
              </span>
            </td>

            <td>
              <button
                class="boton secundario"
                type="button"
                onclick="cambiarEstadoAlerta(${alerta.id}, 'REVISADA')"
              >
                Revisada
              </button>

              <button
                class="boton secundario"
                type="button"
                onclick="cambiarEstadoAlerta(${alerta.id}, 'DESCARTADA')"
              >
                Descartar
              </button>
            </td>
          </tr>
        `;
      })
      .join("");
  }

  function actualizarControlesPaginacion() {
    const paginasMostradas = Math.max(1, totalPaginas);

    informacionPagina.textContent =
      `Página ${paginaActual} de ${paginasMostradas} · ${totalRegistros} alertas`;

    btnAnterior.disabled =
      paginaActual <= 1 || totalRegistros === 0;

    btnSiguiente.disabled =
      paginaActual >= totalPaginas || totalRegistros === 0;
  }

  async function cargar(pagina = 1) {
    try {
      btnActualizar.disabled = true;
      btnActualizar.textContent = "Actualizando...";

      const [resultadoHistorial, resultadoResumen] =
        await Promise.all([
          API.get(
            `/api/historial?pagina=${pagina}` +
            `&cantidad_por_pagina=${alertasPorPagina}`
          ),
          API.get("/api/historial/resumen"),
        ]);

      const alertas = Array.isArray(resultadoHistorial.alertas)
        ? resultadoHistorial.alertas
        : [];

      const paginacion = resultadoHistorial.paginacion || {};

      paginaActual = Number(
        paginacion.paginaActual || pagina
      );

      totalPaginas = Number(
        paginacion.totalPaginas || 0
      );

      totalRegistros = Number(
        paginacion.totalRegistros || 0
      );

      mostrarResumen(resultadoResumen);
      mostrarAlertas(alertas);
      actualizarControlesPaginacion();
    } catch (error) {
      console.error("Error al cargar el historial:", error);

      tabla.innerHTML = `
        <tr>
          <td colspan="7">
            No fue posible cargar el historial de alertas.
          </td>
        </tr>
      `;

      totalPaginas = 0;
      totalRegistros = 0;
      actualizarControlesPaginacion();
    } finally {
      btnActualizar.disabled = false;
      btnActualizar.textContent = "Actualizar";
    }
  }

  btnAnterior.addEventListener("click", async () => {
    if (paginaActual > 1) {
      await cargar(paginaActual - 1);
    }
  });

  btnSiguiente.addEventListener("click", async () => {
    if (paginaActual < totalPaginas) {
      await cargar(paginaActual + 1);
    }
  });

  btnActualizar.addEventListener("click", async () => {
    await cargar(1);
  });

  cargar(1);
});