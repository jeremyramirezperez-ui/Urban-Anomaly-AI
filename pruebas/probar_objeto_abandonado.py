from pathlib import Path
import os, sys
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
os.environ.setdefault("DB_TIPO", "sqlite")

from backend.modelos.configuracion_modelo import ConfiguracionMonitoreo
from backend.modelos.deteccion_modelo import CajaDeteccion, ObjetoDetectado, ResultadoDeteccion
from backend.servicios.objeto_abandonado_servicio import ObjetoAbandonadoServicio

config = ConfiguracionMonitoreo(
    nombreZona="Aula", limitePersonas=10, segundosPermanencia=120,
    zonaRestringidaActiva=False, zonaX1=.1, zonaY1=.1, zonaX2=.9, zonaY2=.9,
    horarioActivo=False, horaInicio="06:00", horaFin="22:00",
    alertasActivas=True, cooldownSegundos=5, confianzaMinima=.4,
    objetoAbandonadoActivo=True, segundosObjetoAbandonado=10,
    distanciaPersonaObjetoPx=150,
)

caja = CajaDeteccion(x1=100, y1=100, x2=160, y2=200)

# Caso 1: objeto recién visto sin nadie cerca (0s) -> NO debe alertar todavía.
objeto_reciente = ObjetoDetectado(
    idSeguimiento=1, tipo="mochila", confianza=.85, caja=caja,
    centroX=130, centroY=150, segundosVisible=1, segundosSinPersonaCerca=1,
)
resultado_sin_alerta = ResultadoDeteccion(
    anchoImagen=640, altoImagen=480, personasDetectadas=0, confianzaPromedio=0,
    motor="PRUEBA", personas=[], objetos=[objeto_reciente],
)
eventos = ObjetoAbandonadoServicio().evaluar(resultado_sin_alerta, config)
assert eventos == [], "No debería alertar antes de cumplir el tiempo configurado"

# Caso 2: objeto lleva más tiempo del configurado sin persona cerca -> SÍ debe alertar.
objeto_abandonado = objeto_reciente.model_copy(update={"segundos_sin_persona_cerca": 15})
resultado_con_alerta = resultado_sin_alerta.model_copy(update={"objetos": [objeto_abandonado]})
eventos = ObjetoAbandonadoServicio().evaluar(resultado_con_alerta, config)
assert len(eventos) == 1
assert eventos[0].tipo == "OBJETO_ABANDONADO"
assert eventos[0].detalle["tipoObjeto"] == "mochila"

# Caso 3: regla desactivada -> nunca debe alertar, aunque se cumpla el tiempo.
config_desactivada = config.model_copy(update={"objeto_abandonado_activo": False})
eventos = ObjetoAbandonadoServicio().evaluar(resultado_con_alerta, config_desactivada)
assert eventos == [], "No debería alertar si la regla está desactivada"

print("OK: objeto abandonado respeta el tiempo configurado y el interruptor de activación")
