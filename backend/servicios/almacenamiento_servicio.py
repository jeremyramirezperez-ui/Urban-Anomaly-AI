from __future__ import annotations

from backend.modelos.alerta_modelo import AlertaCrear
from backend.repositorios.alertas_repositorio import AlertasRepositorio
from backend.repositorios.capturas_repositorio import CapturasRepositorio


class AlmacenamientoServicio:
    def __init__(
        self,
        alertas_repo: AlertasRepositorio | None = None,
        capturas_repo: CapturasRepositorio | None = None,
    ) -> None:
        self.alertas_repo = alertas_repo or AlertasRepositorio()
        self.capturas_repo = capturas_repo or CapturasRepositorio()

    def guardar_alerta(self, alerta: AlertaCrear) -> dict:
        fila = self.alertas_repo.guardar(alerta)
        if alerta.captura_ruta:
            self.capturas_repo.guardar(int(fila["id"]), alerta.captura_ruta, alerta.fecha_hora.isoformat())
        return fila

    def actualizar_correo(self, alerta_id: int, enviado: bool, estado: str) -> dict | None:
        return self.alertas_repo.actualizar_correo(alerta_id, enviado, estado)
