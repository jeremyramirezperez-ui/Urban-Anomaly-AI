document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("#form-destinatario");
  const lista = document.querySelector("#lista-destinatarios");
  const mensaje = document.querySelector("#mensaje");
  const btnProbar = document.querySelector("#btn-probar");

  function escaparHTML(valor) {
    const elemento = document.createElement("div");
    elemento.textContent = valor ?? "";
    return elemento.innerHTML;
  }

  async function cargar() {
    try {
      const destinatarios = await API.get("/api/destinatarios");

      btnProbar.disabled = destinatarios.length === 0;

      if (destinatarios.length === 0) {
        lista.innerHTML = `
          <div class="mensaje neutro">
            No hay correos registrados.
          </div>
        `;

        return;
      }

      lista.innerHTML = destinatarios
        .map(
          (destinatario) => `
            <div class="lista-item destinatario-item">
              <div class="destinatario-informacion">
                <strong>
                  ${escaparHTML(destinatario.nombre)}
                </strong>

                <span>
                  ${escaparHTML(destinatario.correo)}
                </span>
              </div>

              <button
                class="boton boton-desvincular"
                type="button"
                data-destinatario-id="${destinatario.id}"
                data-destinatario-correo="${escaparHTML(destinatario.correo)}"
              >
                Desvincular
              </button>
            </div>
          `
        )
        .join("");
    } catch (error) {
      API.mostrarMensaje(
        mensaje,
        error.message,
        "error"
      );
    }
  }

  async function desvincular(
    destinatarioId,
    correo,
    boton
  ) {
    const confirmado = window.confirm(
      `¿Desea desvincular el correo ${correo}?\n\n` +
      "Este correo dejará de recibir alertas."
    );

    if (!confirmado) {
      return;
    }

    const textoOriginal = boton.textContent;

    try {
      boton.disabled = true;
      boton.textContent = "Desvinculando...";

      const resultado = await API.patchJson(
        `/api/destinatarios/${destinatarioId}/desvincular`,
        {}
      );

      await cargar();

      API.mostrarMensaje(
        mensaje,
        resultado.mensaje || "Correo desvinculado correctamente.",
        "exito"
      );
    } catch (error) {
      boton.disabled = false;
      boton.textContent = textoOriginal;

      API.mostrarMensaje(
        mensaje,
        error.message,
        "error"
      );
    }
  }

  form.addEventListener("submit", async (evento) => {
    evento.preventDefault();

    const datosFormulario = new FormData(form);

    try {
      const resultado = await API.postJson(
        "/api/destinatarios",
        {
          nombre: datosFormulario.get("nombre"),
          correo: datosFormulario.get("correo"),
        }
      );

      form.reset();

      await cargar();

      API.mostrarMensaje(
        mensaje,
        resultado.mensaje || "Correo registrado.",
        "exito"
      );
    } catch (error) {
      API.mostrarMensaje(
        mensaje,
        error.message,
        "error"
      );
    }
  });

  lista.addEventListener("click", async (evento) => {
    const boton = evento.target.closest(
      ".boton-desvincular"
    );

    if (!boton) {
      return;
    }

    const destinatarioId = Number(
      boton.dataset.destinatarioId
    );

    const correo = boton.dataset.destinatarioCorreo;

    if (!destinatarioId) {
      API.mostrarMensaje(
        mensaje,
        "No se pudo identificar el destinatario.",
        "error"
      );

      return;
    }

    await desvincular(
      destinatarioId,
      correo,
      boton
    );
  });

  btnProbar.addEventListener("click", async () => {
    const textoOriginal = btnProbar.textContent;

    try {
      btnProbar.disabled = true;
      btnProbar.textContent = "Enviando...";

      const resultado = await API.postJson(
        "/api/destinatarios/probar-correo",
        {}
      );

      API.mostrarMensaje(
        mensaje,
        resultado.enviado
          ? "Correo de prueba enviado."
          : `Prueba generada: ${resultado.estado}`,
        resultado.enviado
          ? "exito"
          : "advertencia"
      );
    } catch (error) {
      API.mostrarMensaje(
        mensaje,
        error.message,
        "error"
      );
    } finally {
      btnProbar.textContent = textoOriginal;

      const destinatarios = await API.get(
        "/api/destinatarios"
      );

      btnProbar.disabled =
        destinatarios.length === 0;
    }
  });

  cargar();
});
