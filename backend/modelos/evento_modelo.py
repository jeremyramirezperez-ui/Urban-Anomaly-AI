from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class EventoAnomalo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id_evento: str = Field(alias="idEvento")
    tipo: str
    titulo: str
    mensaje: str
    nivel: str
    fecha_hora: datetime = Field(alias="fechaHora")
    cantidad_personas: int = Field(default=0, alias="cantidadPersonas")
    limite_personas: int | None = Field(default=None, alias="limitePersonas")
    id_seguimiento: int | None = Field(default=None, alias="idSeguimiento")
    confianza_promedio: float | None = Field(default=None, alias="confianzaPromedio")
    zona: str
    detalle: dict = Field(default_factory=dict)
