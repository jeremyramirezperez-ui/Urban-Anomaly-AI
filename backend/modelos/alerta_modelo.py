from __future__ import annotations

from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class ModeloAlertaBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class AlertaCrear(ModeloAlertaBase):
    tipo: str
    titulo: str
    mensaje: str
    nivel: str
    cantidad_personas: int = Field(default=0, alias="cantidadPersonas")
    limite_personas: int | None = Field(default=None, alias="limitePersonas")
    id_seguimiento: int | None = Field(default=None, alias="idSeguimiento")
    confianza_promedio: float | None = Field(default=None, alias="confianzaPromedio")
    fecha_hora: datetime = Field(alias="fechaHora")
    zona: str
    captura_ruta: str | None = Field(default=None, alias="capturaRuta")
    detalle: dict = Field(default_factory=dict)


class AlertaRespuesta(AlertaCrear):
    id: int
    estado: str = "PENDIENTE"
    correo_enviado: bool = Field(default=False, alias="correoEnviado")
    estado_correo: str = Field(default="PENDIENTE", alias="estadoCorreo")


class CambioEstadoAlerta(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    estado: Literal["PENDIENTE", "REVISADA", "DESCARTADA"]
