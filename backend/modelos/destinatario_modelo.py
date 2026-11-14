from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class DestinatarioCrear(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    nombre: str = Field(min_length=2, max_length=100)
    correo: EmailStr


class DestinatarioRespuesta(DestinatarioCrear):
    id: int
    activo: bool
    creado_en: datetime | str = Field(alias="creadoEn")
