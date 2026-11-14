from backend.servicios.caida_servicio import CaidaServicio
from backend.servicios.alertas_servicio import AlertasServicio
from backend.servicios.destinatarios_servicio import DestinatariosServicio
from backend.modelos.configuracion_modelo import ConfiguracionMonitoreo
from backend.modelos.deteccion_modelo import ResultadoDeteccion, PersonaDetectada, CajaDeteccion
from backend.modelos.destinatario_modelo import DestinatarioCrear
import time

def probar():
    # 1. Crear configuración
    config = ConfiguracionMonitoreo(
        nombreZona="Zona Prueba",
        limitePersonas=10,
        segundosPermanencia=5,
        zonaRestringidaActiva=False,
        zonaX1=0.0, zonaY1=0.0, zonaX2=1.0, zonaY2=1.0,
        horarioActivo=False,
        horaInicio="08:00", horaFin="18:00",
        alertasActivas=True,
        cooldownSegundos=5,
        confianzaMinima=0.5,
        caidaActiva=True,
        tiempoRiesgoCaida=2
    )

    servicio = CaidaServicio()
    alertas_servicio = AlertasServicio()
    destinatarios_servicio = DestinatariosServicio()

    # Asegurar que hay al menos un destinatario
    if not destinatarios_servicio.listar():
        print("Registrando destinatario de prueba...")
        destinatarios_servicio.registrar(DestinatarioCrear(nombre="Test", correo="test@ejemplo.com"))

    # 2. Simular persona cayendo (ancho > alto * 1.2)
    # Persona cayendo: (100, 100, 300, 200) -> Ancho 200, Alto 100. Ratio 2.0 > 1.2
    p1 = PersonaDetectada(
        idSeguimiento=1,
        confianza=0.9,
        caja=CajaDeteccion(x1=100, y1=100, x2=300, y2=200),
        centroX=200, centroY=150,
        segundosVisible=10.0
    )
    
    deteccion = ResultadoDeteccion(
        anchoImagen=640,
        altoImagen=480,
        personasDetectadas=1,
        confianzaPromedio=0.9,
        motor="prueba",
        personas=[p1]
    )

    print("Evaluando caída...")
    # Primera evaluación, debería iniciar temporizador
    eventos = servicio.evaluar(deteccion, config)
    print(f"Eventos detectados preliminarmente: {len(eventos)}")

    # Esperar un poco
    time.sleep(2.5)

    # Segunda evaluación, debería detectar caída
    eventos = servicio.evaluar(deteccion, config)
    print(f"Eventos detectados tras tiempo de espera: {len(eventos)}")
    
    if len(eventos) > 0:
        print(f"Evento generado: {eventos[0].tipo} - {eventos[0].mensaje}")
        print("Procesando alerta y enviando correo...")
        alertas = alertas_servicio.procesar(eventos, None, deteccion, config)
        if alertas:
            print(f"Alerta procesada. ¿Correo enviado?: {alertas[0].correo_enviado}. Estado: {alertas[0].estado_correo}")
        else:
            print("No se pudo procesar la alerta.")
    else:
        print("No se detectó evento.")

if __name__ == "__main__":
    probar()
