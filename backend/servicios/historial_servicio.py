from __future__ import annotations

import json
from backend.modelos.alerta_modelo import AlertaRespuesta
from backend.repositorios.alertas_repositorio import AlertasRepositorio


class HistorialServicio:
    def __init__(self, repositorio: AlertasRepositorio | None = None) -> None:
        self.repositorio = repositorio or AlertasRepositorio()

    def listar(
        self,
        estado: str | None = None,
        tipo: str | None = None,
        pagina: int = 1,
        cantidad_por_pagina: int = 10,
    ) -> dict:
        pagina = max(1, pagina)
        cantidad_por_pagina = max(1, min(cantidad_por_pagina, 100))

        resultado = self.repositorio.listar(
            estado=estado,
            tipo=tipo,
            pagina=pagina,
            cantidad_por_pagina=cantidad_por_pagina,
        )

        alertas = [
            self._mapear(fila)
            for fila in resultado.get("alertas", [])
        ]

        return {
            "alertas": alertas,
            "paginacion": resultado.get(
                "paginacion",
                {
                    "totalRegistros": 0,
                    "totalPaginas": 0,
                    "paginaActual": pagina,
                    "cantidadPorPagina": cantidad_por_pagina,
                },
            ),
        }

    def cambiar_estado(self, alerta_id: int, estado: str) -> AlertaRespuesta | None:
        fila = self.repositorio.actualizar_estado(alerta_id, estado)
        return self._mapear(fila) if fila else None

    def resumen(self) -> dict:
        return self.repositorio.resumen()

    @staticmethod
    def _mapear(fila: dict) -> AlertaRespuesta:
        detalle = fila.get("detalle_json") or "{}"
        if isinstance(detalle, str):
            try:
                detalle = json.loads(detalle)
            except json.JSONDecodeError:
                detalle = {}
        return AlertaRespuesta(
            id=int(fila["id"]), tipo=fila["tipo"], titulo=fila["titulo"],
            mensaje=fila["mensaje"], nivel=fila["nivel"],
            cantidadPersonas=int(fila.get("cantidad_personas") or 0),
            limitePersonas=fila.get("limite_personas"), idSeguimiento=fila.get("id_seguimiento"),
            confianzaPromedio=fila.get("confianza_promedio"), fechaHora=fila["fecha_hora"],
            estado=fila["estado"], zona=fila["zona"], capturaRuta=fila.get("captura_ruta"),
            correoEnviado=bool(fila.get("correo_enviado")),
            estadoCorreo=fila.get("estado_correo") or "PENDIENTE", detalle=detalle,
        )
