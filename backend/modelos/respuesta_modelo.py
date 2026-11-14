from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from backend.modelos.deteccion_modelo import ResultadoDeteccion
from backend.modelos.evento_modelo import EventoAnomalo
from backend.modelos.alerta_modelo import AlertaRespuesta


class RespuestaBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    ok: bool = True
    mensaje: str


class RespuestaAnalisis(RespuestaBase):
    deteccion: ResultadoDeteccion
    eventos: list[EventoAnomalo] = Field(default_factory=list)
    alertas: list[AlertaRespuesta] = Field(default_factory=list)


class RespuestaEstado(RespuestaBase):
    datos: dict = Field(default_factory=dict)
