from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ModeloBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class CajaDeteccion(ModeloBase):
    x1: int
    y1: int
    x2: int
    y2: int


class PersonaDetectada(ModeloBase):
    id_seguimiento: int = Field(alias="idSeguimiento")
    confianza: float
    caja: CajaDeteccion
    centro_x: float = Field(alias="centroX")
    centro_y: float = Field(alias="centroY")
    segundos_visible: float = Field(alias="segundosVisible")


class ObjetoDetectado(ModeloBase):
    id_seguimiento: int = Field(alias="idSeguimiento")
    tipo: str  # "mochila", "bolso" o "maleta"
    confianza: float
    caja: CajaDeteccion
    centro_x: float = Field(alias="centroX")
    centro_y: float = Field(alias="centroY")
    segundos_visible: float = Field(alias="segundosVisible")
    segundos_sin_persona_cerca: float = Field(default=0.0, alias="segundosSinPersonaCerca")


class ResultadoDeteccion(ModeloBase):
    ancho_imagen: int = Field(alias="anchoImagen")
    alto_imagen: int = Field(alias="altoImagen")
    personas_detectadas: int = Field(alias="personasDetectadas")
    confianza_promedio: float = Field(alias="confianzaPromedio")
    motor: str
    personas: list[PersonaDetectada]
    objetos: list[ObjetoDetectado] = Field(default_factory=list)
    fuego_detectado: bool = Field(default=False, alias="fuegoDetectado")
    fuego_cajas: list[CajaDeteccion] = Field(default_factory=list, alias="fuegoCajas")