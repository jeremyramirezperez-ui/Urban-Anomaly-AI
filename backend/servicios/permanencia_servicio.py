from __future__ import annotations

import uuid
from backend.modelos.configuracion_modelo import ConfiguracionMonitoreo
from backend.modelos.deteccion_modelo import ResultadoDeteccion
from backend.modelos.evento_modelo import EventoAnomalo
from backend.utilidades.fecha_utilidad import ahora_local


class PermanenciaServicio:
    def evaluar(self, deteccion: ResultadoDeteccion, config: ConfiguracionMonitoreo) -> list[EventoAnomalo]:
        eventos = []
        for persona in deteccion.personas:
            if persona.segundos_visible >= config.segundos_permanencia:
                eventos.append(EventoAnomalo(
                    idEvento=str(uuid.uuid4()),
                    tipo="PERMANENCIA_PROLONGADA",
                    titulo="Permanencia prolongada",
                    mensaje=(f"La persona {persona.id_seguimiento} permanece visible durante "
                             f"{persona.segundos_visible:.0f} segundos."),
                    nivel="MEDIO",
                    fechaHora=ahora_local(),
                    cantidadPersonas=deteccion.personas_detectadas,
                    idSeguimiento=persona.id_seguimiento,
                    confianzaPromedio=persona.confianza,
                    zona=config.nombre_zona,
                    detalle={"segundos": persona.segundos_visible},
                ))
        return eventos
