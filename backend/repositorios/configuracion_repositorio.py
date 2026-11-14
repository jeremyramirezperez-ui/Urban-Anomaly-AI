from __future__ import annotations

from backend.base_datos import BaseDatos, obtener_base_datos
from backend.modelos.configuracion_modelo import ConfiguracionMonitoreo


class ConfiguracionRepositorio:
    def __init__(self, bd: BaseDatos | None = None) -> None:
        self.bd = bd or obtener_base_datos()

    def obtener(self) -> dict:
        fila = self.bd.consultar_uno("SELECT * FROM Configuracion WHERE id = 1")
        if not fila:
            raise RuntimeError("No existe la configuración inicial")
        return fila

    def actualizar(self, config: ConfiguracionMonitoreo) -> dict:
        self.bd.ejecutar(
            """
            UPDATE Configuracion SET
                nombre_zona = ?, limite_personas = ?, segundos_permanencia = ?,
                zona_restringida_activa = ?, zona_x1 = ?, zona_y1 = ?, zona_x2 = ?, zona_y2 = ?,
                horario_activo = ?, hora_inicio = ?, hora_fin = ?, alertas_activas = ?,
                cooldown_segundos = ?, confianza_minima = ?,
                objeto_abandonado_activo = ?, segundos_objeto_abandonado = ?,
                distancia_persona_objeto_px = ?, caida_activa = ?, tiempo_riesgo_caida = ?,
                fuego_activo = ?, actualizado_en = CURRENT_TIMESTAMP
            WHERE id = 1
            """,
            (
                config.nombre_zona, config.limite_personas, config.segundos_permanencia,
                int(config.zona_restringida_activa), config.zona_x1, config.zona_y1,
                config.zona_x2, config.zona_y2, int(config.horario_activo),
                config.hora_inicio, config.hora_fin, int(config.alertas_activas),
                config.cooldown_segundos, config.confianza_minima,
                int(config.objeto_abandonado_activo), config.segundos_objeto_abandonado,
                config.distancia_persona_objeto_px, int(config.caida_activa),
                config.tiempo_riesgo_caida, int(config.fuego_activo),
            ),
        )
        return self.obtener()