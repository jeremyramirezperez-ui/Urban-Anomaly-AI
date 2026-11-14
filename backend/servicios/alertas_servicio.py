from __future__ import annotations

import json
import numpy as np

from backend.modelos.alerta_modelo import AlertaCrear, AlertaRespuesta
from backend.modelos.configuracion_modelo import ConfiguracionMonitoreo
from backend.modelos.deteccion_modelo import ResultadoDeteccion
from backend.modelos.evento_modelo import EventoAnomalo
from backend.servicios.almacenamiento_servicio import AlmacenamientoServicio
from backend.servicios.capturas_servicio import CapturasServicio
from backend.servicios.correo_servicio import CorreoServicio
from backend.servicios.destinatarios_servicio import DestinatariosServicio
from backend.servicios.tiempo_real_servicio import obtener_tiempo_real


class AlertasServicio:
    def __init__(self) -> None:
        self.almacenamiento = AlmacenamientoServicio()
        self.capturas = CapturasServicio()
        self.correo = CorreoServicio()
        self.destinatarios = DestinatariosServicio()
        self.tiempo_real = obtener_tiempo_real()

    def procesar(
        self,
        eventos: list[EventoAnomalo],
        imagen: np.ndarray | None,
        deteccion: ResultadoDeteccion | None,
        configuracion: ConfiguracionMonitoreo,
    ) -> list[AlertaRespuesta]:
        resultados: list[AlertaRespuesta] = []
        correos = [str(d.correo) for d in self.destinatarios.listar()]
        
        for evento in eventos:
            captura = self.capturas.guardar(imagen, deteccion, configuracion, evento.tipo)
            crear = AlertaCrear(
                tipo=evento.tipo,
                titulo=evento.titulo,
                mensaje=evento.mensaje,
                nivel=evento.nivel,
                cantidadPersonas=evento.cantidad_personas,
                limitePersonas=evento.limite_personas,
                idSeguimiento=evento.id_seguimiento,
                confianzaPromedio=evento.confianza_promedio,
                fechaHora=evento.fecha_hora,
                zona=evento.zona,
                capturaRuta=captura,
                detalle=evento.detalle,
            )
            fila = self.almacenamiento.guardar_alerta(crear)
            alerta = self._mapear(fila)
            enviado, estado_correo = self.correo.enviar_alerta(alerta, correos)
            fila = self.almacenamiento.actualizar_correo(alerta.id, enviado, estado_correo) or fila
            alerta = self._mapear(fila)
            self.tiempo_real.actualizar(alerta=alerta.model_dump(by_alias=True, mode="json"))
            resultados.append(alerta)
        return resultados

    @staticmethod
    def _mapear(fila: dict) -> AlertaRespuesta:
        detalle = fila.get("detalle_json") or "{}"
        if isinstance(detalle, str):
            try:
                detalle = json.loads(detalle)
            except json.JSONDecodeError:
                detalle = {}
        return AlertaRespuesta(
            id=int(fila["id"]), tipo=fila["tipo"], titulo=fila["titulo"],
            mensaje=fila["mensaje"], nivel=fila["nivel"],
            cantidadPersonas=int(fila.get("cantidad_personas") or 0),
            limitePersonas=fila.get("limite_personas"),
            idSeguimiento=fila.get("id_seguimiento"),
            confianzaPromedio=fila.get("confianza_promedio"),
            fechaHora=fila["fecha_hora"], estado=fila["estado"], zona=fila["zona"],
            capturaRuta=fila.get("captura_ruta"),
            correoEnviado=bool(fila.get("correo_enviado")),
            estadoCorreo=fila.get("estado_correo") or "PENDIENTE",
            detalle=detalle,
        )
