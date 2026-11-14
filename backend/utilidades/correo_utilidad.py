from __future__ import annotations

from html import escape
from backend.modelos.alerta_modelo import AlertaRespuesta


def construir_asunto(alerta: AlertaRespuesta) -> str:
    return f"[{alerta.nivel}] SecurityAPPCR - {alerta.titulo}"


def construir_texto(alerta: AlertaRespuesta) -> str:
    return (
        f"SecurityAPPCR\n\n"
        f"Tipo: {alerta.tipo}\n"
        f"Alerta: {alerta.titulo}\n"
        f"Detalle: {alerta.mensaje}\n"
        f"Zona: {alerta.zona}\n"
        f"Fecha: {alerta.fecha_hora.isoformat()}\n"
        f"Personas detectadas: {alerta.cantidad_personas}\n"
        f"Estado: {alerta.estado}\n"
    )


def construir_html(alerta: AlertaRespuesta) -> str:
    return f"""
    <html><body style="font-family:Arial,sans-serif;background:#f4f6f8;padding:20px">
      <div style="max-width:620px;margin:auto;background:white;padding:24px;border-radius:12px">
        <h2 style="color:#b42318">SecurityAPPCR - {escape(alerta.titulo)}</h2>
        <p>{escape(alerta.mensaje)}</p>
        <table style="border-collapse:collapse;width:100%">
          <tr><td><b>Tipo</b></td><td>{escape(alerta.tipo)}</td></tr>
          <tr><td><b>Nivel</b></td><td>{escape(alerta.nivel)}</td></tr>
          <tr><td><b>Zona</b></td><td>{escape(alerta.zona)}</td></tr>
          <tr><td><b>Personas</b></td><td>{alerta.cantidad_personas}</td></tr>
          <tr><td><b>Fecha</b></td><td>{escape(alerta.fecha_hora.isoformat())}</td></tr>
        </table>
        <p style="color:#667085;font-size:12px">Alerta automática de demostración académica.</p>
      </div>
    </body></html>
    """
