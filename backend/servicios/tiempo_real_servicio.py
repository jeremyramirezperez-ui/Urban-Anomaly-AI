from __future__ import annotations

import asyncio
from copy import deepcopy
from datetime import datetime
from threading import RLock
from fastapi import WebSocket

from backend.utilidades.fecha_utilidad import ahora_local


class TiempoRealServicio:
    def __init__(self) -> None:
        self._lock = RLock()
        self._clientes: list[WebSocket] = []
        self._estado = {
            "camara": "APAGADA",
            "ultimaActualizacion": ahora_local().isoformat(),
            "deteccion": None,
            "ultimaAlerta": None,
        }

    def actualizar(self, *, camara: str | None = None, deteccion=None, alerta=None) -> dict:
        with self._lock:
            if camara is not None:
                self._estado["camara"] = camara
            if deteccion is not None:
                self._estado["deteccion"] = deteccion
            if alerta is not None:
                self._estado["ultimaAlerta"] = alerta
            self._estado["ultimaActualizacion"] = ahora_local().isoformat()
            return deepcopy(self._estado)

    def obtener(self) -> dict:
        with self._lock:
            return deepcopy(self._estado)

    async def conectar(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._clientes.append(websocket)
        await websocket.send_json(self.obtener())

    def desconectar(self, websocket: WebSocket) -> None:
        if websocket in self._clientes:
            self._clientes.remove(websocket)

    async def publicar(self) -> None:
        estado = self.obtener()
        muertos = []
        for cliente in list(self._clientes):
            try:
                await cliente.send_json(estado)
            except Exception:
                muertos.append(cliente)
        for cliente in muertos:
            self.desconectar(cliente)


_instancia: TiempoRealServicio | None = None


def obtener_tiempo_real() -> TiempoRealServicio:
    global _instancia
    if _instancia is None:
        _instancia = TiempoRealServicio()
    return _instancia
