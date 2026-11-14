from backend.servicios.configuracion_servicio import ConfiguracionServicio

def verificar():
    servicio = ConfiguracionServicio()
    config = servicio.obtener()
    print(f"Caida Activa: {config.caida_activa}")
    print(f"Tiempo Riesgo: {config.tiempo_riesgo_caida}")
    print(f"Confianza Minima: {config.confianza_minima}")

if __name__ == "__main__":
    verificar()
