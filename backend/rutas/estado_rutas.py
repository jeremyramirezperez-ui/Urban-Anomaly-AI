from __future__ import annotations

from fastapi import APIRouter
from backend.base_datos import obtener_base_datos
from backend.configuracion import config
from backend.servicios.deteccion_personas_servicio import obtener_detector_personas
from backend.servicios.correo_servicio import CorreoServicio

router = APIRouter(prefix="/api", tags=["Estado"])


@router.get("/estado")
def estado():
    bd_ok = False
    error_bd = None
    try:
        bd_ok = obtener_base_datos().probar_conexion()
    except Exception as exc:
        error_bd = str(exc)
    detector = obtener_detector_personas()
    return {
        "ok": bd_ok,
        "aplicacion": config.NOMBRE,
        "version": config.VERSION,
        "baseDatos": {"tipo": config.DB_TIPO, "funcionando": bd_ok, "error": error_bd},
        "deteccion": {"motor": detector.motor},
        "correo": {"smtpConfigurado": CorreoServicio().configurado()},
    }
