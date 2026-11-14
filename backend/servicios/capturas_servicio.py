from __future__ import annotations

from pathlib import Path
import numpy as np

from backend.configuracion import config
from backend.modelos.configuracion_modelo import ConfiguracionMonitoreo
from backend.modelos.deteccion_modelo import ResultadoDeteccion
from backend.utilidades.fecha_utilidad import fecha_para_archivo
from backend.utilidades.imagen_utilidad import dibujar_resultado, guardar_jpeg


class CapturasServicio:
    def guardar(
        self,
        imagen: np.ndarray | None,
        deteccion: ResultadoDeteccion | None,
        configuracion: ConfiguracionMonitoreo | None,
        tipo: str,
    ) -> str | None:
        if imagen is None:
            return None
        nombre = f"{fecha_para_archivo()}_{tipo.lower()}.jpg"
        ruta = config.CAPTURAS_DIR / nombre
        salida = dibujar_resultado(imagen, deteccion, configuracion)
        guardar_jpeg(salida, ruta)
        return f"/capturas/{nombre}"
