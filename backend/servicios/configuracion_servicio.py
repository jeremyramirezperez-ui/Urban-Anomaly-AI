from __future__ import annotations

from backend.modelos.configuracion_modelo import ConfiguracionMonitoreo
from backend.repositorios.configuracion_repositorio import ConfiguracionRepositorio


class ConfiguracionServicio:
    def __init__(self, repositorio: ConfiguracionRepositorio | None = None) -> None:
        self.repositorio = repositorio or ConfiguracionRepositorio()

    def obtener(self) -> ConfiguracionMonitoreo:
        fila = self.repositorio.obtener()
        return ConfiguracionMonitoreo(
            nombreZona=fila["nombre_zona"],
            limitePersonas=int(fila["limite_personas"]),
            segundosPermanencia=int(fila["segundos_permanencia"]),
            zonaRestringidaActiva=bool(fila["zona_restringida_activa"]),
            zonaX1=float(fila["zona_x1"]), zonaY1=float(fila["zona_y1"]),
            zonaX2=float(fila["zona_x2"]), zonaY2=float(fila["zona_y2"]),
            horarioActivo=bool(fila["horario_activo"]),
            horaInicio=str(fila["hora_inicio"]), horaFin=str(fila["hora_fin"]),
            alertasActivas=bool(fila["alertas_activas"]),
            cooldownSegundos=int(fila["cooldown_segundos"]),
            confianzaMinima=float(fila["confianza_minima"]),
            objetoAbandonadoActivo=bool(fila["objeto_abandonado_activo"]),
            segundosObjetoAbandonado=int(fila["segundos_objeto_abandonado"]),
            distanciaPersonaObjetoPx=float(fila["distancia_persona_objeto_px"]),
            caidaActiva=bool(fila["caida_activa"]),
            tiempoRiesgoCaida=int(fila["tiempo_riesgo_caida"]),
            fuegoActivo=bool(fila["fuego_activo"]),
        )

    def actualizar(self, nueva: ConfiguracionMonitoreo) -> ConfiguracionMonitoreo:
        self.repositorio.actualizar(nueva)
        return self.obtener()