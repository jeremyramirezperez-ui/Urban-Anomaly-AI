from backend.servicios.configuracion_servicio import ConfiguracionServicio

def verificar():
    servicio = ConfiguracionServicio()
    config = servicio.obtener()
    print(f"Cooldown: {config.cooldown_segundos}")

if __name__ == "__main__":
    verificar()
