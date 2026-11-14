from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from backend.modelos.alerta_modelo import CambioEstadoAlerta
from backend.servicios.historial_servicio import HistorialServicio

router = APIRouter(prefix="/api/alertas", tags=["Alertas"])
servicio = HistorialServicio()


@router.get("")
def listar_alertas(
    estado: str | None = None,
    tipo: str | None = None,
    limite: int = Query(default=100, ge=1, le=500),
):
    return [a.model_dump(by_alias=True, mode="json") for a in servicio.listar(estado, tipo, limite)]


@router.patch("/{alerta_id}/estado")
def cambiar_estado(alerta_id: int, entrada: CambioEstadoAlerta):
    alerta = servicio.cambiar_estado(alerta_id, entrada.estado)
    if alerta is None:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    return {"ok": True, "mensaje": "Estado actualizado", "alerta": alerta.model_dump(by_alias=True, mode="json")}
