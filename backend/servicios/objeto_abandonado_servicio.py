from __future__ import annotations

import uuid

from backend.modelos.configuracion_modelo import ConfiguracionMonitoreo
from backend.modelos.deteccion_modelo import ResultadoDeteccion
from backend.modelos.evento_modelo import EventoAnomalo
from backend.utilidades.fecha_utilidad import ahora_local

_NOMBRES_TIPO = {
    "mochila": "una mochila",
    "bolso": "un bolso",
    "maleta": "una maleta",
}


class ObjetoAbandonadoServicio:
    """Sigue el mismo patrón que PermanenciaServicio: evaluar(deteccion, config)
    devuelve la lista de eventos a generar. La detección y el conteo de
    segundos sin persona cerca ya vienen resueltos en ResultadoDeteccion.objetos
    (calculados por SeguimientoObjetosServicio)."""

    def evaluar(self, deteccion: ResultadoDeteccion, config: ConfiguracionMonitoreo) -> list[EventoAnomalo]:
        if not config.objeto_abandonado_activo:
            return []

        eventos: list[EventoAnomalo] = []
        for objeto in deteccion.objetos:
            if objeto.segundos_sin_persona_cerca >= config.segundos_objeto_abandonado:
                nombre = _NOMBRES_TIPO.get(objeto.tipo, "un objeto")
                eventos.append(
                    EventoAnomalo(
                        idEvento=str(uuid.uuid4()),
                        tipo="OBJETO_ABANDONADO",
                        titulo="Objeto abandonado detectado",
                        mensaje=(
                            f"Se detectó {nombre} sin ninguna persona cerca durante "
                            f"{objeto.segundos_sin_persona_cerca:.0f} segundos."
                        ),
                        nivel="ALTO",
                        fechaHora=ahora_local(),
                        cantidadPersonas=deteccion.personas_detectadas,
                        idSeguimiento=objeto.id_seguimiento,
                        confianzaPromedio=objeto.confianza,
                        zona=config.nombre_zona,
                        detalle={
                            "tipoObjeto": objeto.tipo,
                            "segundosSinPersonaCerca": objeto.segundos_sin_persona_cerca,
                        },
                    )
                )
        return eventos
