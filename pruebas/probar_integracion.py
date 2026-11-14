from pathlib import Path
import os, sys
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
os.environ.setdefault("DB_TIPO", "sqlite")

from fastapi.testclient import TestClient
from backend.main import app
from backend.rutas import deteccion_rutas
from backend.modelos.deteccion_modelo import PersonaDetectada, CajaDeteccion
import cv2, numpy as np

# Sustituye solo la inferencia para que la prueba sea rápida y repetible.
deteccion_rutas.detector_personas._motor = "PRUEBA-INTEGRACION"
deteccion_rutas.detector_personas._modelo = object()
deteccion_rutas.detector_personas._detectar_yolo = lambda imagen, confianza: [(30,30,150,250,.95),(200,30,320,250,.92),(360,30,480,250,.90)]

imagen = np.zeros((300, 520, 3), dtype=np.uint8)
ok, buffer = cv2.imencode('.jpg', imagen)
assert ok
with TestClient(app) as cliente:
    assert cliente.get('/api/estado').status_code == 200
    c = cliente.get('/api/configuracion'); assert c.status_code == 200
    datos = c.json(); datos['limitePersonas'] = 2; datos['cooldownSegundos'] = 5
    assert cliente.put('/api/configuracion', json=datos).status_code == 200
    assert cliente.post('/api/destinatarios', json={'nombre':'Prueba','correo':'prueba@example.com'}).status_code == 200
    r = cliente.post('/api/deteccion/analizar', files={'imagen':('prueba.jpg',buffer.tobytes(),'image/jpeg')})
    assert r.status_code == 200, r.text
    salida = r.json(); assert salida['deteccion']['personasDetectadas'] == 3
    assert any(e['tipo']=='AGLOMERACION' for e in salida['eventos'])
    assert cliente.get('/api/alertas').status_code == 200
print('OK: flujo completo API → reglas → alerta → base de datos')
