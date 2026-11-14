from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class EstadoCamaraEntrada(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    estado: Literal["ACTIVA", "APAGADA", "FALLA"]
    motivo: str = Field(default="", max_length=200)
    camara_id: str = Field(default="webcam-principal", alias="camaraId", max_length=80)
