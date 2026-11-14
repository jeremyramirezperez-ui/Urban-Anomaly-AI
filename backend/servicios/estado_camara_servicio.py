from __future__ import annotations

import uuid
from backend.modelos.camara_modelo import EstadoCamaraEntrada
from backend.modelos.configuracion_modelo import ConfiguracionMonitoreo
from backend.modelos.evento_modelo import EventoAnomalo
from backend.utilidades.fecha_utilidad import ahora_local


class EstadoCamaraServicio:
    def evaluar(self, entrada: EstadoCamaraEntrada, config: ConfiguracionMonitoreo) -> list[EventoAnomalo]:
        if entrada.estado == "ACTIVA":
            return []
        titulo = "Cámara apagada" if entrada.estado == "APAGADA" else "Falla de cámara"
        mensaje = entrada.motivo.strip() or f"La cámara {entrada.camara_id} cambió a estado {entrada.estado}."
        return [EventoAnomalo(
            idEvento=str(uuid.uuid4()),
            tipo="CAMARA_APAGADA" if entrada.estado == "APAGADA" else "FALLA_CAMARA",
            titulo=titulo,
            mensaje=mensaje,
            nivel="ALTO",
            fechaHora=ahora_local(),
            zona=config.nombre_zona,
            detalle={"camaraId": entrada.camara_id, "estado": entrada.estado},
        )]
