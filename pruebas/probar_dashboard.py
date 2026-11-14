from pathlib import Path
import os, sys
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
os.environ.setdefault("DB_TIPO", "sqlite")

from backend.base_datos import obtener_base_datos
from backend.servicios.dashboard_servicio import DashboardServicio
from backend.utilidades.fecha_utilidad import ahora_local

bd = obtener_base_datos()
servicio = DashboardServicio()

antes = servicio.obtener_estadisticas()

fecha = ahora_local()
bd.insertar(
    """
    INSERT INTO Alertas
        (tipo, titulo, mensaje, nivel, cantidad_personas, fecha_hora, estado, zona, correo_enviado, estado_correo)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (
        "PRUEBA",
        "Alerta de prueba dashboard",
        "Prueba automática del dashboard",
        "BAJO",
        0,
        fecha.isoformat(),
        "PENDIENTE",
        "Aula",
        0,
        "PENDIENTE",
    ),
)

despues = servicio.obtener_estadisticas()

assert despues.total == antes.total + 1
assert despues.pendientes == antes.pendientes + 1

tipos = {item.etiqueta: item.cantidad for item in despues.por_tipo}
assert tipos.get("PRUEBA", 0) >= 1

niveles = {item.etiqueta: item.cantidad for item in despues.por_nivel}
assert niveles.get("BAJO", 0) >= 1

estados = {item.etiqueta: item.cantidad for item in despues.por_estado}
assert estados.get("PENDIENTE", 0) >= 1

# El filtro de fechas debe excluir la alerta si el rango queda en el futuro
futuro = servicio.obtener_estadisticas(fecha_desde=fecha.replace(year=fecha.year + 1))
assert all(punto.dia != fecha.date().isoformat() for punto in futuro.evolucion_diaria)

print(
    f"OK: dashboard total={despues.total} pendientes={despues.pendientes} "
    f"tipos={len(despues.por_tipo)} evolucion={len(despues.evolucion_diaria)} dias"
)