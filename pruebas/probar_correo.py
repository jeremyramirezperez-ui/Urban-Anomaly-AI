from pathlib import Path
import os, sys
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
os.environ.setdefault("DB_TIPO", "sqlite")

from backend.modelos.alerta_modelo import AlertaRespuesta
from backend.servicios.correo_servicio import CorreoServicio
from backend.utilidades.fecha_utilidad import ahora_local
import os

correo = os.getenv("CORREO_PRUEBA", "prueba@example.com")
a = AlertaRespuesta(id=0,tipo="PRUEBA",titulo="Correo de prueba",mensaje="SecurityAPPCR está conectado",nivel="BAJO",cantidadPersonas=0,fechaHora=ahora_local(),zona="Aula",estado="PENDIENTE",correoEnviado=False,estadoCorreo="PENDIENTE",detalle={})
enviado, estado = CorreoServicio().enviar_alerta(a,[correo])
print(f"Resultado: enviado={enviado}; estado={estado}")
assert enviado or estado.startswith("SIMULADO")
