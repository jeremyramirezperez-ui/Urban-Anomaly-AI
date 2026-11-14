from __future__ import annotations

import uuid
from backend.modelos.configuracion_modelo import ConfiguracionMonitoreo
from backend.modelos.deteccion_modelo import ResultadoDeteccion
from backend.modelos.evento_modelo import EventoAnomalo
from backend.utilidades.fecha_utilidad import ahora_local


class ZonaRestringidaServicio:
    def evaluar(self, deteccion: ResultadoDeteccion, config: ConfiguracionMonitoreo) -> list[EventoAnomalo]:
        if not config.zona_restringida_activa:
            return []
        eventos = []
        for persona in deteccion.personas:
            nx = persona.centro_x / deteccion.ancho_imagen
            ny = persona.centro_y / deteccion.alto_imagen
            dentro = config.zona_x1 <= nx <= config.zona_x2 and config.zona_y1 <= ny <= config.zona_y2
            if dentro:
                eventos.append(EventoAnomalo(
                    idEvento=str(uuid.uuid4()),
                    tipo="ZONA_RESTRINGIDA",
                    titulo="Ingreso a zona restringida",
                    mensaje=f"La persona {persona.id_seguimiento} ingresó al área restringida.",
                    nivel="ALTO",
                    fechaHora=ahora_local(),
                    cantidadPersonas=deteccion.personas_detectadas,
                    idSeguimiento=persona.id_seguimiento,
                    confianzaPromedio=persona.confianza,
                    zona=config.nombre_zona,
                ))
        return eventos
