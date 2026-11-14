from __future__ import annotations

import numpy as np
from backend.configuracion import config
from backend.utilidades.imagen_utilidad import decodificar_imagen


class CamaraServicio:
    def preparar_imagen(self, datos: bytes) -> np.ndarray:
        maximo = config.TAMANO_MAX_IMAGEN_MB * 1024 * 1024
        if not datos:
            raise ValueError("No se recibió una imagen")
        if len(datos) > maximo:
            raise ValueError(f"La imagen supera el máximo de {config.TAMANO_MAX_IMAGEN_MB} MB")
        imagen = decodificar_imagen(datos)
        alto, ancho = imagen.shape[:2]
        if ancho < 160 or alto < 120:
            raise ValueError("La imagen es demasiado pequeña")
        return imagen
