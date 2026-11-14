from __future__ import annotations
import uuid
import logging
from threading import RLock
import numpy as np
import cv2
from backend.configuracion import config
from backend.modelos.configuracion_modelo import ConfiguracionMonitoreo
from backend.modelos.deteccion_modelo import CajaDeteccion, ResultadoDeteccion
from backend.modelos.evento_modelo import EventoAnomalo
from backend.utilidades.fecha_utilidad import ahora_local

class FuegoServicio:
    def __init__(self) -> None:
        self._modelo = None
        self._fire_class_id = None
        self._modelo_cargado = False
        self._lock = RLock()

    def _cargar_modelo(self) -> None:
        if self._modelo_cargado:
            return
        with self._lock:
            if self._modelo_cargado:
                return
            try:
                from ultralytics import YOLO
                if config.MODELO_FUEGO.exists():
                    self._modelo = YOLO(str(config.MODELO_FUEGO))
                    logging.info("Modelo de fuego cargado: %s", self._modelo.names)
                    # identify fire class index
                    for idx, name in self._modelo.names.items():
                        if name.lower() == 'fire':
                            self._fire_class_id = idx
                            break
                    if self._fire_class_id is None:
                        logging.error("Clase 'fire' no encontrada en el modelo.")
                    self._modelo_cargado = True
                else:
                    logging.error("Modelo de detección de fuego no encontrado en %s", config.MODELO_FUEGO)
                    self._modelo_cargado = True
            except Exception as e:
                logging.error("Error al cargar modelo de fuego: %s", e)
                self._modelo_cargado = True

    def detectar(self, imagen: np.ndarray) -> list[CajaDeteccion]:
        self._cargar_modelo()
        if self._modelo is None or self._fire_class_id is None:
            logging.info("Modelo de fuego no disponible.")
            return []

        logging.info("Ejecutando detección de fuego...")
        resultados = self._modelo.predict(
            source=imagen,
            conf=0.35,
            iou=0.10,
            device="cpu",
            verbose=True, # Cambiado a True
        )

        cajas: list[CajaDeteccion] = []
        for box in resultados[0].boxes:
            if int(box.cls) == self._fire_class_id:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                cajas.append(CajaDeteccion(x1=int(x1), y1=int(y1), x2=int(x2), y2=int(y2)))

        if cajas:
            logging.info("¡Fuego detectado! (%d caja(s))", len(cajas))
        return cajas

    def evaluar(self, deteccion: ResultadoDeteccion, config: ConfiguracionMonitoreo) -> list[EventoAnomalo]:
        if not config.fuego_activo or not deteccion.fuego_detectado:
            return []
        
        return [EventoAnomalo(
            idEvento=str(uuid.uuid4()),
            tipo="FUEGO",
            titulo="Fuego detectado",
            mensaje="Se ha detectado fuego en la escena.",
            nivel="CRÍTICO",
            fechaHora=ahora_local(),
            cantidadPersonas=deteccion.personas_detectadas,
            zona=config.nombre_zona,
        )]

_fuego_servicio: FuegoServicio | None = None

def obtener_fuego() -> FuegoServicio:
    global _fuego_servicio
    if _fuego_servicio is None:
        _fuego_servicio = FuegoServicio()
    return _fuego_servicio
