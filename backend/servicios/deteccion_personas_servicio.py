from __future__ import annotations

import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from threading import RLock

import cv2
import numpy as np

from backend.configuracion import config
from backend.modelos.deteccion_modelo import CajaDeteccion, PersonaDetectada


@dataclass
class _Rastro:
    id: int
    centro: tuple[float, float]
    inicio: float
    ultimo: float


class DeteccionPersonasServicio:
    """Usa YOLO11 si está instalado. Incluye HOG como respaldo para iniciar la demo."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._modelo = None
        self._motor = "sin-cargar"
        self._rastros: dict[int, _Rastro] = {}
        self._siguiente_id = 1
        self._hog = None

    @property
    def motor(self) -> str:
        self._cargar_motor()
        return self._motor

    @property
    def modelo_cargado(self):
        self._cargar_motor()
        return self._modelo

    def _cargar_motor(self) -> None:
        if self._motor != "sin-cargar":
            return
        with self._lock:
            if self._motor != "sin-cargar":
                return
            try:
                from ultralytics import YOLO

                ruta = config.MODELO_YOLO
                # El archivo pequeño incluido es una marca. Ultralytics descarga el oficial.
                if ruta.exists() and ruta.stat().st_size > 1_000_000:
                    self._modelo = YOLO(str(ruta))
                else:
                    self._modelo = YOLO("yolo11n.pt")
                    descargado = Path("yolo11n.pt")
                    if descargado.exists() and descargado.stat().st_size > 1_000_000:
                        ruta.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(descargado, ruta)
                self._motor = "YOLO11n"
            except Exception:
                hog = cv2.HOGDescriptor()
                hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
                self._hog = hog
                self._motor = "OpenCV-HOG (respaldo; instale ultralytics para YOLO11n)"

    def analizar(self, imagen: np.ndarray, confianza_minima: float | None = None) -> list[PersonaDetectada]:
        self._cargar_motor()
        confianza = confianza_minima or config.CONFIANZA_MINIMA
        with self._lock:
            if self._modelo is not None:
                cajas = self._detectar_yolo(imagen, confianza)
            else:
                cajas = self._detectar_hog(imagen, confianza)
            return self._asignar_seguimiento(cajas)

    def _detectar_yolo(self, imagen: np.ndarray, confianza: float) -> list[tuple[int, int, int, int, float]]:
        resultados = self._modelo.predict(
            source=imagen,
            classes=[0],
            conf=confianza,
            verbose=False,
            device="cpu",
        )
        cajas: list[tuple[int, int, int, int, float]] = []
        if not resultados:
            return cajas
        boxes = resultados[0].boxes
        if boxes is None:
            return cajas
        xyxy = boxes.xyxy.cpu().numpy()
        confs = boxes.conf.cpu().numpy()
        for coords, conf in zip(xyxy, confs):
            x1, y1, x2, y2 = map(int, coords.tolist())
            cajas.append((x1, y1, x2, y2, float(conf)))
        return cajas

    def _detectar_hog(self, imagen: np.ndarray, confianza: float) -> list[tuple[int, int, int, int, float]]:
        alto, ancho = imagen.shape[:2]
        escala = min(1.0, 720 / max(ancho, alto))
        trabajo = cv2.resize(imagen, None, fx=escala, fy=escala) if escala < 1 else imagen
        rectangulos, pesos = self._hog.detectMultiScale(
            trabajo, winStride=(8, 8), padding=(8, 8), scale=1.05
        )
        cajas = []
        for (x, y, w, h), peso in zip(rectangulos, pesos):
            conf = min(0.99, max(0.35, float(peso)))
            if conf < confianza:
                continue
            x1, y1, x2, y2 = [int(v / escala) for v in (x, y, x + w, y + h)]
            cajas.append((x1, y1, x2, y2, conf))
        return cajas

    def _asignar_seguimiento(
        self, cajas: list[tuple[int, int, int, int, float]]
    ) -> list[PersonaDetectada]:
        ahora = time.monotonic()
        # Elimina rastros que dejaron de aparecer.
        self._rastros = {k: v for k, v in self._rastros.items() if ahora - v.ultimo <= 3.0}
        disponibles = set(self._rastros.keys())
        personas: list[PersonaDetectada] = []

        for x1, y1, x2, y2, confianza in cajas:
            centro = ((x1 + x2) / 2, (y1 + y2) / 2)
            mejor_id = None
            mejor_distancia = 140.0
            for identificador in disponibles:
                rastro = self._rastros[identificador]
                distancia = ((centro[0] - rastro.centro[0]) ** 2 + (centro[1] - rastro.centro[1]) ** 2) ** 0.5
                if distancia < mejor_distancia:
                    mejor_distancia = distancia
                    mejor_id = identificador

            if mejor_id is None:
                mejor_id = self._siguiente_id
                self._siguiente_id += 1
                self._rastros[mejor_id] = _Rastro(mejor_id, centro, ahora, ahora)
            else:
                rastro = self._rastros[mejor_id]
                rastro.centro = centro
                rastro.ultimo = ahora
                disponibles.remove(mejor_id)

            rastro = self._rastros[mejor_id]
            rastro.ultimo = ahora
            personas.append(
                PersonaDetectada(
                    idSeguimiento=mejor_id,
                    confianza=round(confianza, 4),
                    caja=CajaDeteccion(x1=x1, y1=y1, x2=x2, y2=y2),
                    centroX=centro[0],
                    centroY=centro[1],
                    segundosVisible=round(ahora - rastro.inicio, 2),
                )
            )
        return personas


_detector: DeteccionPersonasServicio | None = None


def obtener_detector_personas() -> DeteccionPersonasServicio:
    global _detector
    if _detector is None:
        _detector = DeteccionPersonasServicio()
    return _detector
