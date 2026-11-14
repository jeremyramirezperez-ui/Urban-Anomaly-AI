from backend.servicios.deteccion_personas_servicio import obtener_detector_personas

def verificar():
    detector = obtener_detector_personas()
    print(f"Motor de detección: {detector.motor}")

if __name__ == "__main__":
    verificar()
