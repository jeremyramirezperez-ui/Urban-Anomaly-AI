from __future__ import annotations

from backend.modelos.destinatario_modelo import (
    DestinatarioCrear,
    DestinatarioRespuesta,
)
from backend.repositorios.destinatarios_repositorio import (
    DestinatariosRepositorio,
)


class DestinatariosServicio:
    def __init__(
        self,
        repositorio: DestinatariosRepositorio | None = None,
    ) -> None:
        self.repositorio = repositorio or DestinatariosRepositorio()

    def registrar(
        self,
        entrada: DestinatarioCrear,
    ) -> DestinatarioRespuesta:
        fila = self.repositorio.guardar(
            entrada.nombre.strip(),
            str(entrada.correo).strip().lower(),
        )

        return self._mapear(fila)

    def listar(self) -> list[DestinatarioRespuesta]:
        filas = self.repositorio.listar()

        return [
            self._mapear(fila)
            for fila in filas
        ]

    def desvincular(
        self,
        destinatario_id: int,
    ) -> DestinatarioRespuesta | None:
        if destinatario_id <= 0:
            return None

        fila = self.repositorio.desvincular(
            destinatario_id
        )

        if fila is None:
            return None

        return self._mapear(fila)

    @staticmethod
    def _mapear(
        fila: dict,
    ) -> DestinatarioRespuesta:
        return DestinatarioRespuesta(
            id=int(fila["id"]),
            nombre=fila["nombre"],
            correo=fila["correo"],
            activo=bool(fila["activo"]),
            creadoEn=fila["creado_en"],
        )