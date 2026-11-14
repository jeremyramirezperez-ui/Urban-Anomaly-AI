from __future__ import annotations

import base64
from pathlib import Path
import cv2
import numpy as np

from backend.modelos.deteccion_modelo import ResultadoDeteccion
from backend.modelos.configuracion_modelo import ConfiguracionMonitoreo


def decodificar_imagen(datos: bytes) -> np.ndarray:
    arreglo = np.frombuffer(datos, dtype=np.uint8)
    imagen = cv2.imdecode(arreglo, cv2.IMREAD_COLOR)
    if imagen is None:
        raise ValueError("La imagen enviada no se pudo leer")
    return imagen


def codificar_jpeg(imagen: np.ndarray, calidad: int = 85) -> bytes:
    correcto, buffer = cv2.imencode(".jpg", imagen, [int(cv2.IMWRITE_JPEG_QUALITY), calidad])
    if not correcto:
        raise ValueError("No se pudo convertir la imagen a JPG")
    return buffer.tobytes()


def imagen_a_base64(imagen: np.ndarray) -> str:
    return base64.b64encode(codificar_jpeg(imagen)).decode("ascii")


def dibujar_resultado(
    imagen: np.ndarray,
    deteccion: ResultadoDeteccion | None,
    configuracion: ConfiguracionMonitoreo | None,
) -> np.ndarray:
    salida = imagen.copy()
    alto, ancho = salida.shape[:2]

    if configuracion and configuracion.zona_restringida_activa:
        p1 = (int(configuracion.zona_x1 * ancho), int(configuracion.zona_y1 * alto))
        p2 = (int(configuracion.zona_x2 * ancho), int(configuracion.zona_y2 * alto))
        cv2.rectangle(salida, p1, p2, (0, 165, 255), 2)
        cv2.putText(salida, "ZONA RESTRINGIDA", (p1[0], max(20, p1[1] - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 165, 255), 2)

    if deteccion:
        for persona in deteccion.personas:
            caja = persona.caja
            cv2.rectangle(salida, (caja.x1, caja.y1), (caja.x2, caja.y2), (0, 210, 90), 2)
            texto = f"Persona {persona.id_seguimiento} {persona.confianza:.0%}"
            cv2.putText(salida, texto, (caja.x1, max(20, caja.y1 - 7)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 210, 90), 2)
            for caja in deteccion.fuego_cajas:
                cv2.rectangle(salida, (caja.x1, caja.y1), (caja.x2, caja.y2), (0, 0, 255), 3)
                cv2.putText(salida, "FUEGO", (caja.x1, max(20, caja.y1 - 7)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    return salida


def guardar_jpeg(imagen: np.ndarray, ruta: Path) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(ruta), imagen):
        raise IOError(f"No se pudo guardar la captura en {ruta}")
