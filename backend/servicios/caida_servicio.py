from __future__ import annotations

import time
import uuid

from backend.modelos.configuracion_modelo import ConfiguracionMonitoreo
from backend.modelos.deteccion_modelo import ResultadoDeteccion
from backend.modelos.evento_modelo import EventoAnomalo
from backend.utilidades.fecha_utilidad import ahora_local


class CaidaServicio:
    def __init__(self) -> None:
        self._temporizadores: dict[int, dict[str, float]] = {}

    def evaluar(self, deteccion: ResultadoDeteccion, config: ConfiguracionMonitoreo) -> list[EventoAnomalo]:
        if not config.caida_activa:
            self._temporizadores.clear()
            return []

        eventos = []
        personas_actuales = {p.id_seguimiento for p in deteccion.personas}
        ahora = time.monotonic()

        # 1. Verificar caídas
        for persona in deteccion.personas:
            # Añadir filtros: confianza y tamaño mínimo
            if persona.confianza < config.confianza_minima:
                continue
            
            caja = persona.caja
            ancho = caja.x2 - caja.x1
            alto = caja.y2 - caja.y1
            
            if ancho < 20 or alto < 20:
                continue

            # Ratio umbral para considerar postura de caída
            es_caida = ancho > alto * 1.2
            
            if es_caida:
                if persona.id_seguimiento not in self._temporizadores:
                    self._temporizadores[persona.id_seguimiento] = {'inicio': ahora, 'ultima_deteccion': ahora}
                else:
                    self._temporizadores[persona.id_seguimiento]['ultima_deteccion'] = ahora
                    inicio = self._temporizadores[persona.id_seguimiento]['inicio']
                    if ahora - inicio >= config.tiempo_riesgo_caida:
                        eventos.append(
                            EventoAnomalo(
                                idEvento=str(uuid.uuid4()),
                                tipo="CAIDA_DETECTADA",
                                titulo="Caída detectada",
                                mensaje=(f"Persona {persona.id_seguimiento} en postura de caída por "
                                         f"{config.tiempo_riesgo_caida} segundos."),
                                nivel="ALTO",
                                fechaHora=ahora_local(),
                                cantidadPersonas=deteccion.personas_detectadas,
                                idSeguimiento=persona.id_seguimiento,
                                confianzaPromedio=persona.confianza,
                                zona=config.nombre_zona,
                            )
                        )
            else:
                # Si la persona está presente pero no cae, resetear
                if persona.id_seguimiento in self._temporizadores:
                    del self._temporizadores[persona.id_seguimiento]
        
        # 2. Limpiar temporizadores de personas que dejaron de detectarse (con gracia)
        for id_seg in list(self._temporizadores.keys()):
            if id_seg not in personas_actuales:
                if ahora - self._temporizadores[id_seg]['ultima_deteccion'] > 1.0: # 1s grace period
                    del self._temporizadores[id_seg]
        
        return eventos
