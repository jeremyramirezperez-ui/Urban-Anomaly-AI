from backend.servicios.configuracion_servicio import ConfiguracionServicio

def verificar():
    servicio = ConfiguracionServicio()
    config = servicio.obtener()
    print(config)

if __name__ == "__main__":
    verificar()
