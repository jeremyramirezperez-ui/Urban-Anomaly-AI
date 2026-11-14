# Endpoints de SecurityAPPCR

| Método | Endpoint | Uso |
|---|---|---|
| GET | `/api/estado` | Comprueba API, base de datos, detector y correo. |
| POST | `/api/deteccion/analizar` | Recibe `multipart/form-data` con campo `imagen`. Devuelve detección, eventos y alertas. |
| POST | `/api/camara/estado` | JSON: `estado`, `motivo`, `camaraId`. |
| GET | `/api/configuracion` | Consulta límites, zona y horario. |
| PUT | `/api/configuracion` | Guarda la configuración completa. |
| POST | `/api/destinatarios` | JSON: `nombre`, `correo`. |
| GET | `/api/destinatarios` | Lista correos activos. |
| POST | `/api/destinatarios/probar-correo` | Envía una prueba o crea un `.eml` si SMTP no está configurado. |
| GET | `/api/alertas` | Historial con filtros opcionales `estado`, `tipo`, `limite`. |
| PATCH | `/api/alertas/{id}/estado` | JSON: `estado` (`PENDIENTE`, `REVISADA`, `DESCARTADA`). |
| GET | `/api/historial` | Lista alternativa del historial. |
| GET | `/api/historial/resumen` | Totales para el dashboard. |
| GET | `/api/monitoreo/ultimo` | Último estado de cámara, conteo y alerta. |
| WS | `/api/monitoreo/ws` | Actualizaciones en tiempo real. |

## Respuesta principal de detección

```json
{
  "ok": true,
  "mensaje": "Imagen analizada correctamente",
  "deteccion": {
    "anchoImagen": 1280,
    "altoImagen": 720,
    "personasDetectadas": 3,
    "confianzaPromedio": 0.91,
    "motor": "YOLO11n",
    "personas": []
  },
  "eventos": [],
  "alertas": []
}
```
