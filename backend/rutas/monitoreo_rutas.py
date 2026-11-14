from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.servicios.tiempo_real_servicio import obtener_tiempo_real

router = APIRouter(prefix="/api/monitoreo", tags=["Monitoreo"])
servicio = obtener_tiempo_real()


@router.get("/ultimo")
def ultimo_estado():
    return servicio.obtener()


@router.websocket("/ws")
async def websocket_monitoreo(websocket: WebSocket):
    await servicio.conectar(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        servicio.desconectar(websocket)
    except Exception:
        servicio.desconectar(websocket)
