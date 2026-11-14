from __future__ import annotations

from fastapi import APIRouter, HTTPException
from backend.modelos.camara_modelo import EstadoCamaraEntrada
from backend.servicios.alertas_servicio import AlertasServicio
from backend.servicios.configuracion_servicio import ConfiguracionServicio
from backend.servicios.estado_camara_servicio import EstadoCamaraServicio
from backend.servicios.reglas_servicio import obtener_reglas
from backend.servicios.tiempo_real_servicio import obtener_tiempo_real

router = APIRouter(prefix="/api/camara", tags=["Cámara"])
estado_servicio = EstadoCamaraServicio()
configuracion_servicio = ConfiguracionServicio()
alertas_servicio = AlertasServicio()
reglas_servicio = obtener_reglas()
tiempo_real = obtener_tiempo_real()


@router.post("/estado")
async def cambiar_estado(entrada: EstadoCamaraEntrada):
    try:
        configuracion = configuracion_servicio.obtener()
        eventos = estado_servicio.evaluar(entrada, configuracion)
        eventos = reglas_servicio.filtrar_eventos(eventos, configuracion.cooldown_segundos)
        alertas = alertas_servicio.procesar(eventos, None, None, configuracion)
        tiempo_real.actualizar(
            camara=entrada.estado,
            alerta=alertas[-1].model_dump(by_alias=True, mode="json") if alertas else None,
        )
        await tiempo_real.publicar()
        return {
            "ok": True,
            "mensaje": "Estado de cámara actualizado",
            "estado": entrada.estado,
            "eventos": [e.model_dump(by_alias=True, mode="json") for e in eventos],
            "alertas": [a.model_dump(by_alias=True, mode="json") for a in alertas],
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"No se pudo actualizar la cámara: {exc}") from exc
