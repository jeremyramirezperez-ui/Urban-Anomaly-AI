from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ConteoPorCategoria(BaseModel):
    """Un conteo genérico: sirve para tipo, estado o nivel de alerta."""

    model_config = ConfigDict(populate_by_name=True)

    etiqueta: str = Field(alias="etiqueta")
    cantidad: int = Field(alias="cantidad", ge=0)


class PuntoEvolucionDiaria(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    dia: str = Field(alias="dia")
    cantidad: int = Field(alias="cantidad", ge=0)


class DashboardEstadisticas(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    total: int = Field(alias="total", ge=0)
    pendientes: int = Field(alias="pendientes", ge=0)
    tipos_distintos: int = Field(alias="tiposDistintos", ge=0)
    por_tipo: list[ConteoPorCategoria] = Field(alias="porTipo", default_factory=list)
    por_estado: list[ConteoPorCategoria] = Field(alias="porEstado", default_factory=list)
    por_nivel: list[ConteoPorCategoria] = Field(alias="porNivel", default_factory=list)
    evolucion_diaria: list[PuntoEvolucionDiaria] = Field(
        alias="evolucionDiaria", default_factory=list
    )