from __future__ import annotations

from fastapi import APIRouter, Query

from backend.servicios.historial_servicio import HistorialServicio


router = APIRouter(prefix="/api/historial", tags=["Historial"])
servicio = HistorialServicio()


@router.get("")
def obtener_historial(
    estado: str | None = Query(default=None),
    tipo: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    cantidad_por_pagina: int = Query(default=10, ge=1, le=100),
):
    resultado = servicio.listar(
        estado=estado,
        tipo=tipo,
        pagina=pagina,
        cantidad_por_pagina=cantidad_por_pagina,
    )

    return {
        "alertas": [
            alerta.model_dump(by_alias=True, mode="json")
            for alerta in resultado["alertas"]
        ],
        "paginacion": resultado["paginacion"],
    }


@router.get("/resumen")
def obtener_resumen():
    return servicio.resumen()