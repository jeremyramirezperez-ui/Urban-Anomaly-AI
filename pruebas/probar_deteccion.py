from pathlib import Path
import os, sys
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
os.environ.setdefault("DB_TIPO", "sqlite")

import numpy as np
from backend.servicios.deteccion_personas_servicio import DeteccionPersonasServicio

servicio = DeteccionPersonasServicio()
# Prueba determinista del seguimiento sin depender de webcam ni internet.
servicio._motor = "PRUEBA"
servicio._modelo = object()
servicio._detectar_yolo = lambda imagen, confianza: [(20, 20, 120, 220, 0.91), (180, 30, 280, 230, 0.88)]
personas = servicio.analizar(np.zeros((300, 400, 3), dtype=np.uint8), 0.4)
assert len(personas) == 2
assert personas[0].id_seguimiento != personas[1].id_seguimiento
print("OK: detección, conteo base e identificadores funcionan")
