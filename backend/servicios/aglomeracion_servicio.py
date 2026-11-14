from __future__ import annotations

import uuid
from backend.modelos.configuracion_modelo import ConfiguracionMonitoreo
from backend.modelos.deteccion_modelo import ResultadoDeteccion
from backend.modelos.evento_modelo import EventoAnomalo
from backend.utilidades.fecha_utilidad import ahora_local


class AglomeracionServicio:
    def evaluar(self, deteccion: ResultadoDeteccion, config: ConfiguracionMonitoreo) -> list[EventoAnomalo]:
        if deteccion.personas_detectadas <= config.limite_personas:
            return []
        return [EventoAnomalo(
            idEvento=str(uuid.uuid4()),
            tipo="AGLOMERACION",
            titulo="Aglomeración detectada",
            mensaje=(f"Se detectaron {deteccion.personas_detectadas} personas; "
                     f"el límite configurado es {config.limite_personas}."),
            nivel="ALTO",
            fechaHora=ahora_local(),
            cantidadPersonas=deteccion.personas_detectadas,
            limitePersonas=config.limite_personas,
            confianzaPromedio=deteccion.confianza_promedio,
            zona=config.nombre_zona,
        )]
