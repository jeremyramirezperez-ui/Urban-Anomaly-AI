from __future__ import annotations

from datetime import datetime
from typing import Any

from backend.base_datos import BaseDatos, obtener_base_datos


def _texto_fecha(momento: datetime | None) -> str | None:
    """Convierte a texto ISO (con offset) para que SQL Server la parsee sin ambigüedad."""
    if momento is None:
        return None
    return momento.isoformat(sep=" ", timespec="seconds")


class DashboardRepositorio:
    """Consultas de agregación sobre Alertas para el dashboard de estadísticas."""

    def __init__(self, bd: BaseDatos | None = None) -> None:
        self.bd = bd or obtener_base_datos()

    def totales(
        self,
        fecha_desde: datetime | None = None,
        fecha_hasta: datetime | None = None,
    ) -> dict[str, Any]:
        if self.bd.tipo == "sqlserver":
            fila = self.bd.consultar_uno(
                "EXEC dbo.sp_dashboard_totales ?, ?",
                (_texto_fecha(fecha_desde), _texto_fecha(fecha_hasta)),
            )
        else:
            where, parametros = self._condiciones_sqlite(fecha_desde, fecha_hasta)
            fila = self.bd.consultar_uno(
                f"""
                SELECT
                    COUNT(*) AS total,
                    SUM(CASE WHEN estado = 'PENDIENTE' THEN 1 ELSE 0 END) AS pendientes
                FROM Alertas
                {where}
                """,
                parametros,
            )
        return fila or {"total": 0, "pendientes": 0}

    def resumen_por_tipo(
        self,
        fecha_desde: datetime | None = None,
        fecha_hasta: datetime | None = None,
    ) -> list[dict[str, Any]]:
        if self.bd.tipo == "sqlserver":
            return self.bd.consultar_todos(
                "EXEC dbo.sp_dashboard_resumen_por_tipo ?, ?",
                (_texto_fecha(fecha_desde), _texto_fecha(fecha_hasta)),
            )
        where, parametros = self._condiciones_sqlite(fecha_desde, fecha_hasta)
        return self.bd.consultar_todos(
            f"""
            SELECT tipo, COUNT(*) AS cantidad
            FROM Alertas
            {where}
            GROUP BY tipo
            ORDER BY cantidad DESC, tipo ASC
            """,
            parametros,
        )

    def resumen_por_estado(
        self,
        fecha_desde: datetime | None = None,
        fecha_hasta: datetime | None = None,
    ) -> list[dict[str, Any]]:
        if self.bd.tipo == "sqlserver":
            return self.bd.consultar_todos(
                "EXEC dbo.sp_dashboard_resumen_por_estado ?, ?",
                (_texto_fecha(fecha_desde), _texto_fecha(fecha_hasta)),
            )
        where, parametros = self._condiciones_sqlite(fecha_desde, fecha_hasta)
        return self.bd.consultar_todos(
            f"""
            SELECT estado, COUNT(*) AS cantidad
            FROM Alertas
            {where}
            GROUP BY estado
            ORDER BY cantidad DESC, estado ASC
            """,
            parametros,
        )

    def resumen_por_nivel(
        self,
        fecha_desde: datetime | None = None,
        fecha_hasta: datetime | None = None,
    ) -> list[dict[str, Any]]:
        if self.bd.tipo == "sqlserver":
            return self.bd.consultar_todos(
                "EXEC dbo.sp_dashboard_resumen_por_nivel ?, ?",
                (_texto_fecha(fecha_desde), _texto_fecha(fecha_hasta)),
            )
        where, parametros = self._condiciones_sqlite(fecha_desde, fecha_hasta)
        return self.bd.consultar_todos(
            f"""
            SELECT nivel, COUNT(*) AS cantidad
            FROM Alertas
            {where}
            GROUP BY nivel
            ORDER BY
                CASE nivel WHEN 'ALTO' THEN 1 WHEN 'MEDIO' THEN 2 WHEN 'BAJO' THEN 3 ELSE 4 END
            """,
            parametros,
        )

    def evolucion_diaria(
        self,
        fecha_desde: datetime | None = None,
        fecha_hasta: datetime | None = None,
    ) -> list[dict[str, Any]]:
        if self.bd.tipo == "sqlserver":
            return self.bd.consultar_todos(
                "EXEC dbo.sp_dashboard_evolucion_diaria ?, ?",
                (_texto_fecha(fecha_desde), _texto_fecha(fecha_hasta)),
            )

        where, parametros = self._condiciones_sqlite(fecha_desde, fecha_hasta)
        return self.bd.consultar_todos(
            f"""
            SELECT
                date(fecha_hora) AS dia,
                COUNT(*) AS cantidad
            FROM Alertas
            {where}
            GROUP BY date(fecha_hora)
            ORDER BY dia ASC
            """,
            parametros,
        )

    @staticmethod
    def _condiciones_sqlite(
        fecha_desde: datetime | None,
        fecha_hasta: datetime | None,
    ) -> tuple[str, tuple[Any, ...]]:
        condiciones = []
        parametros: list[Any] = []
        if fecha_desde is not None:
            condiciones.append("fecha_hora >= ?")
            parametros.append(fecha_desde.isoformat())
        if fecha_hasta is not None:
            condiciones.append("fecha_hora <= ?")
            parametros.append(fecha_hasta.isoformat())
        where = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""
        return where, tuple(parametros)