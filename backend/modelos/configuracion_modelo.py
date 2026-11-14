from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ConfiguracionMonitoreo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    nombre_zona: str = Field(alias="nombreZona", min_length=2, max_length=100)
    limite_personas: int = Field(alias="limitePersonas", ge=0, le=50)
    segundos_permanencia: int = Field(alias="segundosPermanencia", ge=2, le=3600)
    zona_restringida_activa: bool = Field(alias="zonaRestringidaActiva")
    zona_x1: float = Field(alias="zonaX1", ge=0, le=1)
    zona_y1: float = Field(alias="zonaY1", ge=0, le=1)
    zona_x2: float = Field(alias="zonaX2", ge=0, le=1)
    zona_y2: float = Field(alias="zonaY2", ge=0, le=1)
    horario_activo: bool = Field(alias="horarioActivo")
    hora_inicio: str = Field(alias="horaInicio", pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    hora_fin: str = Field(alias="horaFin", pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    alertas_activas: bool = Field(alias="alertasActivas")
    cooldown_segundos: int = Field(alias="cooldownSegundos", ge=5, le=3600)
    confianza_minima: float = Field(alias="confianzaMinima", ge=0.1, le=0.95)
    caida_activa: bool = Field(alias="caidaActiva")
    tiempo_riesgo_caida: int = Field(alias="tiempoRiesgoCaida", ge=1, le=300)
    fuego_activo: bool = Field(alias="fuegoActivo", default=False)

    # --- Objeto abandonado (mochila / bolso / maleta) ---
    objeto_abandonado_activo: bool = Field(alias="objetoAbandonadoActivo")
    segundos_objeto_abandonado: int = Field(alias="segundosObjetoAbandonado", ge=5, le=3600)
    distancia_persona_objeto_px: float = Field(alias="distanciaPersonaObjetoPx", ge=20, le=2000)

    @model_validator(mode="after")
    def validar_zona(self):
        if self.zona_x1 >= self.zona_x2 or self.zona_y1 >= self.zona_y2:
            raise ValueError("Las coordenadas iniciales de la zona deben ser menores que las finales")
        return self
