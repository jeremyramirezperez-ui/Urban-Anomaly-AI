"""Script de diagnóstico manual (no es parte de la suite de pruebas).
Corré esto con la mochila/bolso/maleta puesta frente a la webcam:

    python pruebas/diagnostico_yolo.py

Abre la cámara, toma una foto y muestra TODO lo que YOLO11n detecta en la
imagen (sin filtrar por clase ni por confianza mínima), para confirmar si el
modelo ve el objeto y con qué nombre/confianza exactos.
"""
from pathlib import Path
import os, sys
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
os.environ.setdefault("DB_TIPO", "sqlite")

import cv2
from ultralytics import YOLO

print("Abriendo la cámara (índice 0)...")
camara = cv2.VideoCapture(0)
if not camara.isOpened():
    print("ERROR: no se pudo abrir la cámara. Cerrá cualquier otra app que la esté usando "
          "(por ejemplo, la pestaña del navegador con /monitoreo) e intentá de nuevo.")
    sys.exit(1)

# Descarta los primeros cuadros para que la cámara termine de ajustar exposición/foco.
for _ in range(10):
    camara.read()

ok, cuadro = camara.read()
camara.release()

if not ok:
    print("ERROR: no se pudo capturar un cuadro de la cámara.")
    sys.exit(1)

cv2.imwrite("diagnostico_captura.jpg", cuadro)
print("Foto guardada como diagnostico_captura.jpg (revisala para confirmar qué se vio).")

print("Cargando modelo YOLO11n...")
modelo = YOLO("yolo11n.pt")

print("Analizando imagen SIN filtro de clase ni confianza mínima...")
resultados = modelo.predict(source=cuadro, conf=0.05, verbose=False, device="cpu")

boxes = resultados[0].boxes
if boxes is None or len(boxes) == 0:
    print("YOLO no detectó NADA en la imagen (ni personas, ni objetos, ni nada de las 80 "
          "clases de COCO). Puede ser un problema de cámara/imagen, no de tu código.")
else:
    print(f"\nYOLO detectó {len(boxes)} elemento(s):\n")
    nombres = modelo.names  # diccionario {id_clase: nombre}
    confs = boxes.conf.cpu().numpy()
    clases = boxes.cls.cpu().numpy()
    for conf, clase in sorted(zip(confs, clases), key=lambda t: -t[0]):
        nombre = nombres.get(int(clase), f"clase_{int(clase)}")
        print(f"  - {nombre:15s}  (id={int(clase):2d})  confianza={conf:.2f}")

    print("\nClases que tu código busca para objetos abandonados: "
          "24=backpack, 26=handbag, 28=suitcase")
