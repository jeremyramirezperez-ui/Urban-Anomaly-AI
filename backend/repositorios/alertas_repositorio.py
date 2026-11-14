from __future__ import annotations

import json

from backend.base_datos import BaseDatos, obtener_base_datos
from backend.modelos.alerta_modelo import AlertaCrear


class AlertasRepositorio:
    def __init__(self, bd: BaseDatos | None = None) -> None:
        self.bd = bd or obtener_base_datos()

    def guardar(self, alerta: AlertaCrear) -> dict:
        identificador = self.bd.insertar(
            """
            INSERT INTO Alertas (
                tipo,
                titulo,
                mensaje,
                nivel,
                cantidad_personas,
                limite_personas,
                id_seguimiento,
                confianza_promedio,
                fecha_hora,
                estado,
                zona,
                captura_ruta,
                correo_enviado,
                estado_correo,
                detalle_json
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?,
                'PENDIENTE',
                ?, ?,
                0,
                'PENDIENTE',
                ?
            )
            """,
            (
                alerta.tipo,
                alerta.titulo,
                alerta.mensaje,
                alerta.nivel,
                alerta.cantidad_personas,
                alerta.limite_personas,
                alerta.id_seguimiento,
                alerta.confianza_promedio,
                alerta.fecha_hora.isoformat(),
                alerta.zona,
                alerta.captura_ruta,
                json.dumps(alerta.detalle, ensure_ascii=False),
            ),
        )

        return self.obtener(identificador) or {}

    def obtener(self, identificador: int) -> dict | None:
        return self.bd.consultar_uno(
            "SELECT * FROM Alertas WHERE id = ?",
            (identificador,),
        )

    def listar(
        self,
        estado: str | None = None,
        tipo: str | None = None,
        pagina: int = 1,
        cantidad_por_pagina: int = 10,
    ) -> dict:
        filas = self.bd.consultar_todos(
            """
            EXEC dbo.sp_alertas_listar
                @estado = ?,
                @tipo = ?,
                @limite = NULL,
                @pagina = ?,
                @cantidad_por_pagina = ?
            """,
            (
                estado,
                tipo,
                pagina,
                cantidad_por_pagina,
            ),
        )

        if not filas:
            return {
                "alertas": [],
                "paginacion": {
                    "totalRegistros": 0,
                    "totalPaginas": 0,
                    "paginaActual": pagina,
                    "cantidadPorPagina": cantidad_por_pagina,
                },
            }

        primera_fila = filas[0]

        total_registros = int(
            primera_fila.get("total_registros", 0)
        )

        total_paginas = int(
            primera_fila.get("total_paginas", 0)
        )

        pagina_actual = int(
            primera_fila.get("pagina_actual", pagina)
        )

        cantidad_actual = int(
            primera_fila.get(
                "cantidad_por_pagina",
                cantidad_por_pagina,
            )
        )

        campos_paginacion = {
            "total_registros",
            "total_paginas",
            "pagina_actual",
            "cantidad_por_pagina",
        }

        alertas: list[dict] = []

        for fila in filas:
            alerta = dict(fila)

            for campo in campos_paginacion:
                alerta.pop(campo, None)

            alertas.append(alerta)

        return {
            "alertas": alertas,
            "paginacion": {
                "totalRegistros": total_registros,
                "totalPaginas": total_paginas,
                "paginaActual": pagina_actual,
                "cantidadPorPagina": cantidad_actual,
            },
        }

    def actualizar_estado(
        self,
        identificador: int,
        estado: str,
    ) -> dict | None:
        self.bd.ejecutar(
            "UPDATE Alertas SET estado = ? WHERE id = ?",
            (estado, identificador),
        )

        return self.obtener(identificador)

    def actualizar_correo(
        self,
        identificador: int,
        enviado: bool,
        estado_correo: str,
    ) -> dict | None:
        self.bd.ejecutar(
            """
            UPDATE Alertas
            SET correo_enviado = ?,
                estado_correo = ?
            WHERE id = ?
            """,
            (
                int(enviado),
                estado_correo,
                identificador,
            ),
        )

        return self.obtener(identificador)

    def resumen(self) -> dict:
        total = self.bd.consultar_uno(
            "SELECT COUNT(*) AS total FROM Alertas"
        ) or {"total": 0}

        pendientes = self.bd.consultar_uno(
            """
            SELECT COUNT(*) AS total
            FROM Alertas
            WHERE estado = 'PENDIENTE'
            """
        ) or {"total": 0}

        por_tipo = self.bd.consultar_todos(
            """
            SELECT
                tipo,
                COUNT(*) AS cantidad
            FROM Alertas
            GROUP BY tipo
            ORDER BY cantidad DESC
            """
        )

        return {
            "total": int(total["total"]),
            "pendientes": int(pendientes["total"]),
            "porTipo": por_tipo,
        }