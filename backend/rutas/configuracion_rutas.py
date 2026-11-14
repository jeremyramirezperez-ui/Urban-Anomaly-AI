from __future__ import annotations

from fastapi import APIRouter, HTTPException
from backend.modelos.configuracion_modelo import ConfiguracionMonitoreo
from backend.servicios.configuracion_servicio import ConfiguracionServicio

router = APIRouter(prefix="/api/configuracion", tags=["Configuración"])
servicio = ConfiguracionServicio()


@router.get("")
def obtener_configuracion():
    return servicio.obtener().model_dump(by_alias=True, mode="json")


@router.put("")
def actualizar_configuracion(entrada: ConfiguracionMonitoreo):
    try:
        actualizada = servicio.actualizar(entrada)
        return {"ok": True, "mensaje": "Configuración guardada", "configuracion": actualizada.model_dump(by_alias=True, mode="json")}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"No se pudo guardar la configuración: {exc}") from exc
