from __future__ import annotations

import time
from dataclasses import dataclass
from threading import RLock

import numpy as np

from backend.modelos.deteccion_modelo import CajaDeteccion, ObjetoDetectado, PersonaDetectada
from backend.servicios.deteccion_personas_servicio import DeteccionPersonasServicio, obtener_detector_personas

# Clases COCO que usa YOLO11n para objetos que una persona puede dejar abandonados.
CLASES_OBJETOS = {24: "mochila", 26: "bolso", 28: "maleta"}

DISTANCIA_MAX_SEGUIMIENTO = 140.0
SEGUNDOS_SIN_RASTRO = 3.0

# YOLO11n (versión "nano") es mucho menos seguro reconociendo mochilas/bolsos/
# maletas que reconociendo personas. Usamos un piso de confianza dedicado y
# más bajo SOLO para objetos, para no tener que bajar la confianza general
# del sistema (que sí funciona bien para personas). Ojo: cuanto más bajo,
# más riesgo de falsos positivos (confundir una silla con una maleta, etc.).
CONFIANZA_MINIMA_OBJETOS = 0.12


@dataclass
class _RastroObjeto:
    id: int
    tipo: str
    centro: tuple[float, float]
    inicio: float
    ultimo: float
    ultimo_cercano: float  # última vez (time.monotonic) que hubo una persona cerca


class SeguimientoObjetosServicio:
    """Detecta mochilas/bolsos/maletas con YOLO11n y les da seguimiento entre
    cuadros, calculando cuánto tiempo lleva cada objeto sin tener una persona
    cerca (para que ObjetoAbandonadoServicio decida si generar la alerta)."""

    def __init__(self, detector_base: DeteccionPersonasServicio | None = None) -> None:
        self._detector_base = detector_base or obtener_detector_personas()
        self._lock = RLock()
        self._rastros: dict[int, _RastroObjeto] = {}
        self._siguiente_id = 1

    def analizar(
        self,
        imagen: np.ndarray,
        personas: list[PersonaDetectada],
        confianza_minima: float,
        distancia_persona_px: float,
    ) -> list[ObjetoDetectado]:
        modelo = self._detector_base.modelo_cargado
        if modelo is None:
            # Sin YOLO disponible (respaldo HOG activo): no se pueden detectar objetos.
            return []
        # Usamos el piso dedicado para objetos (más permisivo) en vez de
        # confianza_minima, que está pensada para personas y es más exigente
        # de lo que YOLO11n logra para mochilas/bolsos/maletas.
        confianza_objetos = min(confianza_minima, CONFIANZA_MINIMA_OBJETOS)
        with self._lock:
            cajas = self._detectar(modelo, imagen, confianza_objetos)
            return self._asignar_seguimiento(cajas, personas, distancia_persona_px)

    def _detectar(self, modelo, imagen: np.ndarray, confianza: float):
        resultados = modelo.predict(
            source=imagen,
            classes=list(CLASES_OBJETOS.keys()),
            conf=confianza,
            verbose=False,
            device="cpu",
        )
        cajas: list[tuple[int, int, int, int, float, str]] = []
        if not resultados:
            return cajas
        boxes = resultados[0].boxes
        if boxes is None:
            return cajas
        xyxy = boxes.xyxy.cpu().numpy()
        confs = boxes.conf.cpu().numpy()
        clases = boxes.cls.cpu().numpy()
        for coords, conf, clase in zip(xyxy, confs, clases):
            x1, y1, x2, y2 = map(int, coords.tolist())
            tipo = CLASES_OBJETOS.get(int(clase), "objeto")
            cajas.append((x1, y1, x2, y2, float(conf), tipo))
        return cajas

    def _asignar_seguimiento(
        self,
        cajas: list[tuple[int, int, int, int, float, str]],
        personas: list[PersonaDetectada],
        distancia_persona_px: float,
    ) -> list[ObjetoDetectado]:
        ahora = time.monotonic()
        self._rastros = {
            k: v for k, v in self._rastros.items() if ahora - v.ultimo <= SEGUNDOS_SIN_RASTRO
        }
        disponibles = set(self._rastros.keys())
        objetos: list[ObjetoDetectado] = []

        for x1, y1, x2, y2, confianza, tipo in cajas:
            centro = ((x1 + x2) / 2, (y1 + y2) / 2)
            mejor_id = None
            mejor_distancia = DISTANCIA_MAX_SEGUIMIENTO
            for identificador in disponibles:
                rastro = self._rastros[identificador]
                distancia = (
                    (centro[0] - rastro.centro[0]) ** 2 + (centro[1] - rastro.centro[1]) ** 2
                ) ** 0.5
                if distancia < mejor_distancia:
                    mejor_distancia = distancia
                    mejor_id = identificador

            hay_persona_cerca = self._hay_persona_cerca(centro, personas, distancia_persona_px)

            if mejor_id is None:
                mejor_id = self._siguiente_id
                self._siguiente_id += 1
                self._rastros[mejor_id] = _RastroObjeto(
                    id=mejor_id,
                    tipo=tipo,
                    centro=centro,
                    inicio=ahora,
                    ultimo=ahora,
                    ultimo_cercano=ahora,  # arranca "acompañado" hasta que se demuestre lo contrario
                )
            else:
                disponibles.remove(mejor_id)

            rastro = self._rastros[mejor_id]
            rastro.centro = centro
            rastro.ultimo = ahora
            rastro.tipo = tipo
            if hay_persona_cerca:
                rastro.ultimo_cercano = ahora

            segundos_sin_persona = round(ahora - rastro.ultimo_cercano, 2)
            objetos.append(
                ObjetoDetectado(
                    idSeguimiento=mejor_id,
                    tipo=tipo,
                    confianza=round(confianza, 4),
                    caja=CajaDeteccion(x1=x1, y1=y1, x2=x2, y2=y2),
                    centroX=centro[0],
                    centroY=centro[1],
                    segundosVisible=round(ahora - rastro.inicio, 2),
                    segundosSinPersonaCerca=segundos_sin_persona,
                )
            )
        return objetos

    @staticmethod
    def _hay_persona_cerca(
        centro_objeto: tuple[float, float],
        personas: list[PersonaDetectada],
        distancia_max: float,
    ) -> bool:
        for persona in personas:
            distancia = (
                (centro_objeto[0] - persona.centro_x) ** 2 + (centro_objeto[1] - persona.centro_y) ** 2
            ) ** 0.5
            if distancia <= distancia_max:
                return True
        return False


_seguimiento: SeguimientoObjetosServicio | None = None


def obtener_seguimiento_objetos() -> SeguimientoObjetosServicio:
    global _seguimiento
    if _seguimiento is None:
        _seguimiento = SeguimientoObjetosServicio()
    return _seguimiento
