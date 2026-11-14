from __future__ import annotations

import uuid
from backend.modelos.configuracion_modelo import ConfiguracionMonitoreo
from backend.modelos.deteccion_modelo import ResultadoDeteccion
from backend.modelos.evento_modelo import EventoAnomalo
from backend.utilidades.fecha_utilidad import ahora_local, esta_dentro_del_horario


class HorarioServicio:
    def evaluar(self, deteccion: ResultadoDeteccion, config: ConfiguracionMonitoreo) -> list[EventoAnomalo]:
        if not config.horario_activo or deteccion.personas_detectadas == 0:
            return []
        if esta_dentro_del_horario(config.hora_inicio, config.hora_fin):
            return []
        return [EventoAnomalo(
            idEvento=str(uuid.uuid4()),
            tipo="FUERA_DE_HORARIO",
            titulo="Presencia fuera del horario permitido",
            mensaje=(f"Se detectaron {deteccion.personas_detectadas} personas fuera del horario "
                     f"{config.hora_inicio} - {config.hora_fin}."),
            nivel="ALTO",
            fechaHora=ahora_local(),
            cantidadPersonas=deteccion.personas_detectadas,
            confianzaPromedio=deteccion.confianza_promedio,
            zona=config.nombre_zona,
        )]
