from __future__ import annotations

from backend.modelos.deteccion_modelo import CajaDeteccion, ObjetoDetectado, PersonaDetectada, ResultadoDeteccion


class ConteoPersonasServicio:
    def construir_resultado(
        self,
        personas: list[PersonaDetectada],
        ancho: int,
        alto: int,
        motor: str,
        objetos: list[ObjetoDetectado] | None = None,
        fuego_detectado: bool = False,
        fuego_cajas: list[CajaDeteccion] | None = None,
    ) -> ResultadoDeteccion:
        promedio = sum(p.confianza for p in personas) / len(personas) if personas else 0.0
        return ResultadoDeteccion(
            anchoImagen=ancho,
            altoImagen=alto,
            personasDetectadas=len(personas),
            confianzaPromedio=round(promedio, 4),
            motor=motor,
            personas=personas,
            objetos=objetos or [],
            fuegoDetectado=fuego_detectado,
            fuegoCajas=fuego_cajas or [],
        )