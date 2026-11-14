from pathlib import Path
import os, sys
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
os.environ.setdefault("DB_TIPO", "sqlite")

from backend.modelos.evento_modelo import EventoAnomalo
from backend.servicios.alertas_servicio import AlertasServicio
from backend.servicios.configuracion_servicio import ConfiguracionServicio
from backend.utilidades.fecha_utilidad import ahora_local

evento = EventoAnomalo(idEvento="prueba",tipo="PRUEBA",titulo="Alerta de prueba",mensaje="Prueba automática",nivel="BAJO",fechaHora=ahora_local(),zona="Aula")
alertas = AlertasServicio().procesar([evento], None, None, ConfiguracionServicio().obtener())
assert alertas and alertas[0].id > 0
print(f"OK: alerta guardada con ID {alertas[0].id}; correo={alertas[0].estado_correo}")
