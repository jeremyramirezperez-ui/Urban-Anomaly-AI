from __future__ import annotations

from datetime import datetime

from backend.modelos.dashboard_modelo import (
    ConteoPorCategoria,
    DashboardEstadisticas,
    PuntoEvolucionDiaria,
)
from backend.repositorios.dashboard_repositorio import DashboardRepositorio


class DashboardServicio:
    def __init__(self, repositorio: DashboardRepositorio | None = None) -> None:
        self.repositorio = repositorio or DashboardRepositorio()

    def obtener_estadisticas(
        self,
        fecha_desde: datetime | None = None,
        fecha_hasta: datetime | None = None,
    ) -> DashboardEstadisticas:
        # Las tarjetas de totales quedan fijas: siempre muestran el total
        # general, sin importar el filtro de fechas. Solo los gráficos de
        # abajo (por tipo/estado/nivel y evolución) respetan el filtro.
        totales = self.repositorio.totales()
        tipos_totales = self.repositorio.resumen_por_tipo()
        por_tipo = self.repositorio.resumen_por_tipo(fecha_desde, fecha_hasta)
        por_estado = self.repositorio.resumen_por_estado(fecha_desde, fecha_hasta)
        por_nivel = self.repositorio.resumen_por_nivel(fecha_desde, fecha_hasta)
        evolucion = self.repositorio.evolucion_diaria(fecha_desde, fecha_hasta)

        return DashboardEstadisticas(
            total=int(totales.get("total") or 0),
            pendientes=int(totales.get("pendientes") or 0),
            tiposDistintos=len(tipos_totales),
            porTipo=[
                ConteoPorCategoria(etiqueta=str(f["tipo"]), cantidad=int(f["cantidad"]))
                for f in por_tipo
            ],
            porEstado=[
                ConteoPorCategoria(etiqueta=str(f["estado"]), cantidad=int(f["cantidad"]))
                for f in por_estado
            ],
            porNivel=[
                ConteoPorCategoria(etiqueta=str(f["nivel"]), cantidad=int(f["cantidad"]))
                for f in por_nivel
            ],
            evolucionDiaria=[
                PuntoEvolucionDiaria(dia=str(f["dia"]), cantidad=int(f["cantidad"]))
                for f in evolucion
            ],
        )