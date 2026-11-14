from __future__ import annotations

from backend.base_datos import BaseDatos, obtener_base_datos


class CapturasRepositorio:
    def __init__(self, bd: BaseDatos | None = None) -> None:
        self.bd = bd or obtener_base_datos()

    def guardar(self, alerta_id: int, ruta: str, fecha_hora: str) -> int:
        return self.bd.insertar(
            "INSERT INTO Capturas (alerta_id, ruta, fecha_hora) VALUES (?, ?, ?)",
            (alerta_id, ruta, fecha_hora),
        )
