from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.modelos.respuesta_modelo import RespuestaAnalisis
from backend.servicios.alertas_servicio import AlertasServicio
from backend.servicios.camara_servicio import CamaraServicio
from backend.servicios.configuracion_servicio import ConfiguracionServicio
from backend.servicios.conteo_personas_servicio import ConteoPersonasServicio
from backend.servicios.deteccion_personas_servicio import obtener_detector_personas
from backend.servicios.fuego_servicio import obtener_fuego
from backend.servicios.reglas_servicio import obtener_reglas
from backend.servicios.seguimiento_objetos_servicio import obtener_seguimiento_objetos
from backend.servicios.tiempo_real_servicio import obtener_tiempo_real


router = APIRouter(prefix="/api/deteccion", tags=["Detección"])

camara_servicio = CamaraServicio()
detector_personas = obtener_detector_personas()
seguimiento_objetos = obtener_seguimiento_objetos()
conteo_servicio = ConteoPersonasServicio()
fuego_servicio = obtener_fuego()
configuracion_servicio = ConfiguracionServicio()
reglas_servicio = obtener_reglas()
alertas_servicio = AlertasServicio()
tiempo_real = obtener_tiempo_real()


@router.post("/analizar")
async def analizar_imagen(imagen: UploadFile = File(...)):
    if imagen.content_type not in {
        "image/jpeg",
        "image/png",
        "image/webp",
    }:
        raise HTTPException(
            status_code=400,
            detail="Envíe una imagen JPG, PNG o WEBP",
        )

    try:
        datos = await imagen.read()

        cuadro = camara_servicio.preparar_imagen(datos)

        configuracion = configuracion_servicio.obtener()

        # -------------------------------------------------
        # Detección de personas
        # -------------------------------------------------
        personas = detector_personas.analizar(
            cuadro,
            configuracion.confianza_minima,
        )

        # -------------------------------------------------
        # Detección de objetos abandonados
        # -------------------------------------------------
        # Solo se ejecuta YOLO para mochila, bolso y maleta
        # cuando esta función está activada en configuración.
        if configuracion.objeto_abandonado_activo:
            objetos = seguimiento_objetos.analizar(
                cuadro,
                personas,
                configuracion.confianza_minima,
                configuracion.distancia_persona_objeto_px,
            )
        else:
            objetos = []

        # -------------------------------------------------
        # Dimensiones de la imagen
        # -------------------------------------------------
        alto, ancho = cuadro.shape[:2]

        # -------------------------------------------------
        # Detección de fuego
        # -------------------------------------------------
        # Se conserva exactamente la lógica existente:
        # el modelo solo se ejecuta si fuego está activo.
        fuego_cajas = (
            fuego_servicio.detectar(cuadro)
            if configuracion.fuego_activo
            else []
        )

        fuego_detectado = bool(fuego_cajas)

        # -------------------------------------------------
        # Construcción del resultado de detección
        # -------------------------------------------------
        deteccion = conteo_servicio.construir_resultado(
            personas,
            ancho,
            alto,
            detector_personas.motor,
            objetos=objetos,
            fuego_detectado=fuego_detectado,
            fuego_cajas=fuego_cajas,
        )

        # -------------------------------------------------
        # Evaluación de reglas
        # -------------------------------------------------
        eventos = reglas_servicio.evaluar(
            deteccion,
            configuracion,
        )

        # -------------------------------------------------
        # Generación de alertas
        # -------------------------------------------------
        alertas = alertas_servicio.procesar(
            eventos,
            cuadro,
            deteccion,
            configuracion,
        )

        # -------------------------------------------------
        # Actualización en tiempo real
        # -------------------------------------------------
        tiempo_real.actualizar(
            camara="ACTIVA",
            deteccion=deteccion.model_dump(
                by_alias=True,
                mode="json",
            ),
            alerta=(
                alertas[-1].model_dump(
                    by_alias=True,
                    mode="json",
                )
                if alertas
                else None
            ),
        )

        await tiempo_real.publicar()

        respuesta = RespuestaAnalisis(
            mensaje="Imagen analizada correctamente",
            deteccion=deteccion,
            eventos=eventos,
            alertas=alertas,
        )

        return respuesta.model_dump(
            by_alias=True,
            mode="json",
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"No se pudo analizar la imagen: {exc}",
        ) from exc