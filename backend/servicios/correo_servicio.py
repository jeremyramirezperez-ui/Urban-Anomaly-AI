from __future__ import annotations

import smtplib
from email.message import EmailMessage
from pathlib import Path

from backend.configuracion import config
from backend.modelos.alerta_modelo import AlertaRespuesta
from backend.utilidades.correo_utilidad import construir_asunto, construir_html, construir_texto
from backend.utilidades.fecha_utilidad import fecha_para_archivo


class CorreoServicio:
    def configurado(self) -> bool:
        return bool(config.SMTP_USER and config.SMTP_PASSWORD)

    def enviar_alerta(self, alerta: AlertaRespuesta, correos: list[str]) -> tuple[bool, str]:
        if not correos:
            return False, "SIN_DESTINATARIOS"

        mensaje = EmailMessage()
        mensaje["Subject"] = construir_asunto(alerta)
        mensaje["From"] = f"{config.SMTP_FROM_NAME} <{config.SMTP_USER or 'securityappcr@local'}>"
        mensaje["To"] = ", ".join(correos)
        mensaje.set_content(construir_texto(alerta))
        mensaje.add_alternative(construir_html(alerta), subtype="html")

        if not self.configurado():
            ruta = config.CORREOS_SIMULADOS_DIR / f"{fecha_para_archivo()}_alerta_{alerta.id}.eml"
            ruta.write_bytes(mensaje.as_bytes())
            return False, f"SIMULADO:{ruta.name}"

        try:
            with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=15) as servidor:
                if config.SMTP_USE_TLS:
                    servidor.starttls()
                servidor.login(config.SMTP_USER, config.SMTP_PASSWORD)
                servidor.send_message(mensaje)
            return True, "ENVIADO"
        except Exception as exc:
            return False, f"ERROR:{type(exc).__name__}:{exc}"
