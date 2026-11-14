from __future__ import annotations

import time
from threading import RLock

from backend.modelos.configuracion_modelo import ConfiguracionMonitoreo
from backend.modelos.deteccion_modelo import ResultadoDeteccion
from backend.modelos.evento_modelo import EventoAnomalo
from backend.servicios.aglomeracion_servicio import AglomeracionServicio
from backend.servicios.caida_servicio import CaidaServicio
from backend.servicios.fuego_servicio import obtener_fuego
from backend.servicios.permanencia_servicio import PermanenciaServicio
from backend.servicios.zona_restringida_servicio import ZonaRestringidaServicio
from backend.servicios.horario_servicio import HorarioServicio
from backend.servicios.objeto_abandonado_servicio import ObjetoAbandonadoServicio


class ReglasServicio:
    def __init__(self) -> None:
        self.aglomeracion = AglomeracionServicio()
        self.permanencia = PermanenciaServicio()
        self.caida = CaidaServicio()
        self.zona = ZonaRestringidaServicio()
        self.horario = HorarioServicio()
        self.objeto_abandonado = ObjetoAbandonadoServicio()
        self.fuego = obtener_fuego()
        self._ultimas_alertas: dict[str, float] = {}
        self._lock = RLock()

    def evaluar(self, deteccion: ResultadoDeteccion, config: ConfiguracionMonitoreo) -> list[EventoAnomalo]:
        if not config.alertas_activas:
            return []
        candidatos = (
            self.aglomeracion.evaluar(deteccion, config)
            + self.permanencia.evaluar(deteccion, config)
            + self.caida.evaluar(deteccion, config)
            + self.zona.evaluar(deteccion, config)
            + self.horario.evaluar(deteccion, config)
            + self.objeto_abandonado.evaluar(deteccion, config)
            + self.fuego.evaluar(deteccion, config)
        )
        return [e for e in candidatos if self._permitir(e, config.cooldown_segundos)]

    def filtrar_eventos(self, eventos: list[EventoAnomalo], cooldown: int) -> list[EventoAnomalo]:
        return [e for e in eventos if self._permitir(e, cooldown)]

    def _permitir(self, evento: EventoAnomalo, cooldown: int) -> bool:
        clave = f"{evento.tipo}:{evento.id_seguimiento or 'general'}"
        ahora = time.monotonic()
        with self._lock:
            anterior = self._ultimas_alertas.get(clave, 0)
            if ahora - anterior < cooldown:
                return False
            self._ultimas_alertas[clave] = ahora
            return True


_reglas: ReglasServicio | None = None


def obtener_reglas() -> ReglasServicio:
    global _reglas
    if _reglas is None:
        _reglas = ReglasServicio()
    return _reglas