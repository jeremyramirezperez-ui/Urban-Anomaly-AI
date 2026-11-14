from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from backend.modelos.alerta_modelo import AlertaRespuesta
from backend.modelos.destinatario_modelo import DestinatarioCrear
from backend.servicios.correo_servicio import CorreoServicio
from backend.servicios.destinatarios_servicio import DestinatariosServicio
from backend.utilidades.fecha_utilidad import ahora_local


router = APIRouter(
    prefix="/api/destinatarios",
    tags=["Destinatarios"],
)

servicio = DestinatariosServicio()
correo_servicio = CorreoServicio()


@router.post("")
def registrar(entrada: DestinatarioCrear):
    destinatario = servicio.registrar(entrada)

    return {
        "ok": True,
        "mensaje": "Correo registrado",
        "destinatario": destinatario.model_dump(
            by_alias=True,
            mode="json",
        ),
    }


@router.get("")
def listar():
    destinatarios = servicio.listar()

    return [
        destinatario.model_dump(
            by_alias=True,
            mode="json",
        )
        for destinatario in destinatarios
    ]


@router.patch("/{destinatario_id}/desvincular")
def desvincular(destinatario_id: int):
    destinatario = servicio.desvincular(destinatario_id)

    if destinatario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El destinatario no existe o ya está desvinculado",
        )

    return {
        "ok": True,
        "mensaje": "Correo desvinculado correctamente",
        "destinatario": destinatario.model_dump(
            by_alias=True,
            mode="json",
        ),
    }


@router.post("/probar-correo")
def probar_correo():
    destinatarios = servicio.listar()

    if not destinatarios:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registre al menos un destinatario activo",
        )

    alerta = AlertaRespuesta(
        id=0,
        tipo="PRUEBA",
        titulo="Correo de prueba",
        mensaje="El envío de alertas está conectado.",
        nivel="BAJO",
        cantidadPersonas=0,
        fechaHora=ahora_local(),
        zona="Prueba",
        estado="PENDIENTE",
        correoEnviado=False,
        estadoCorreo="PENDIENTE",
        detalle={},
    )

    enviado, estado_correo = correo_servicio.enviar_alerta(
        alerta,
        [str(destinatario.correo) for destinatario in destinatarios],
    )

    return {
        "ok": enviado or estado_correo.startswith("SIMULADO"),
        "enviado": enviado,
        "estado": estado_correo,
    }