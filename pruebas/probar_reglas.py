from pathlib import Path
import os, sys
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
os.environ.setdefault("DB_TIPO", "sqlite")

from backend.modelos.configuracion_modelo import ConfiguracionMonitoreo
from backend.modelos.deteccion_modelo import ResultadoDeteccion, PersonaDetectada, CajaDeteccion
from backend.servicios.reglas_servicio import ReglasServicio

config = ConfiguracionMonitoreo(nombreZona="Aula",limitePersonas=1,segundosPermanencia=2,zonaRestringidaActiva=True,zonaX1=.2,zonaY1=.2,zonaX2=.8,zonaY2=.8,horarioActivo=False,horaInicio="06:00",horaFin="22:00",alertasActivas=True,cooldownSegundos=5,confianzaMinima=.4)
p = PersonaDetectada(idSeguimiento=1,confianza=.9,caja=CajaDeteccion(x1=100,y1=100,x2=200,y2=250),centroX=150,centroY=175,segundosVisible=3)
r = ResultadoDeteccion(anchoImagen=300,altoImagen=300,personasDetectadas=2,confianzaPromedio=.9,motor="PRUEBA",personas=[p,p.model_copy(update={"id_seguimiento":2})])
eventos = ReglasServicio().evaluar(r, config)
tipos = {e.tipo for e in eventos}
assert "AGLOMERACION" in tipos and "PERMANENCIA_PROLONGADA" in tipos and "ZONA_RESTRINGIDA" in tipos
print("OK: reglas de aglomeración, permanencia y zona funcionan")
