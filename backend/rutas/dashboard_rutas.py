from __future__ import annotations

from datetime import datetime, time
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException, Query

from backend.configuracion import config
from backend.servicios.dashboard_servicio import DashboardServicio

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])
servicio = DashboardServicio()


@router.get("")
def obtener_estadisticas(
    fecha_desde: str | None = Query(default=None, alias="fechaDesde"),
    fecha_hasta: str | None = Query(default=None, alias="fechaHasta"),
):
    zona = ZoneInfo(config.ZONA_HORARIA)

    try:
        desde = datetime.fromisoformat(fecha_desde) if fecha_desde else None
        hasta = datetime.fromisoformat(fecha_hasta) if fecha_hasta else None

        # Si "hasta" viene solo con fecha (sin hora), extenderla al final
        # del día para no excluir las alertas de ese mismo día.
        if hasta is not None and hasta.time() == time.min:
            hasta = datetime.combine(hasta.date(), time.max)

        # Las alertas se guardan con la zona horaria local (ver ahora_local()).
        # Si el filtro llega sin zona horaria, hay que asignarle la misma,
        # si no SQL Server compara mal contra fecha_hora (desfase de horas).
        if desde is not None and desde.tzinfo is None:
            desde = desde.replace(tzinfo=zona)
        if hasta is not None and hasta.tzinfo is None:
            hasta = hasta.replace(tzinfo=zona)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="Formato de fecha inválido, use YYYY-MM-DD o ISO 8601",
        ) from exc

    try:
        estadisticas = servicio.obtener_estadisticas(desde, hasta)
        return estadisticas.model_dump(by_alias=True, mode="json")
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"No se pudieron obtener las estadísticas: {exc}"
        ) from exc