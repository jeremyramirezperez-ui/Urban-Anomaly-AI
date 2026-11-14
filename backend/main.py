from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from backend.base_datos import obtener_base_datos
from backend.configuracion import config
from backend.servicios.fuego_servicio import obtener_fuego
from backend.rutas import (
    alertas_rutas,
    camara_rutas,
    configuracion_rutas,
    dashboard_rutas,
    destinatarios_rutas,
    deteccion_rutas,
    estado_rutas,
    historial_rutas,
    monitoreo_rutas,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    config.preparar_directorios()
    obtener_base_datos().probar_conexion()
    obtener_fuego()._cargar_modelo()

    yield


app = FastAPI(
    title="SecurityAPPCR API",
    version=config.VERSION,
    description=(
        "Detección de personas y alertas urbanas "
        "para demostración académica."
    ),
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# RUTAS DE LA API
# ============================================================

for modulo in (
    estado_rutas,
    deteccion_rutas,
    camara_rutas,
    configuracion_rutas,
    dashboard_rutas,
    alertas_rutas,
    destinatarios_rutas,
    historial_rutas,
    monitoreo_rutas,
):
    app.include_router(modulo.router)


# ============================================================
# ARCHIVOS ESTÁTICOS Y PLANTILLAS
# ============================================================

app.mount(
    "/static",
    StaticFiles(directory=config.FRONTEND_DIR),
    name="static",
)

app.mount(
    "/capturas",
    StaticFiles(directory=config.CAPTURAS_DIR),
    name="capturas",
)


templates = Jinja2Templates(
    directory=str(config.FRONTEND_DIR / "templates")
)


# ============================================================
# MANEJO GENERAL DE ERRORES
# ============================================================

@app.exception_handler(Exception)
async def error_no_controlado(
    request: Request,
    exc: Exception,
):
    return JSONResponse(
        status_code=500,
        content={
            "ok": False,
            "detalle": str(exc),
        },
    )


# ============================================================
# FUNCIÓN PARA RENDERIZAR PÁGINAS
# ============================================================

def pagina(
    request: Request,
    nombre: str,
):
    return templates.TemplateResponse(
        request=request,
        name=nombre,
        context={
            "request": request,
        },
    )


# ============================================================
# RUTAS DE LAS PÁGINAS
# ============================================================

@app.get("/", include_in_schema=False)
def inicio(request: Request):
    return pagina(
        request=request,
        nombre="index.html",
    )


@app.get("/monitoreo", include_in_schema=False)
def monitoreo(request: Request):
    return pagina(
        request=request,
        nombre="monitoreo.html",
    )


@app.get("/configuracion", include_in_schema=False)
def configuracion(request: Request):
    return pagina(
        request=request,
        nombre="configuracion.html",
    )


@app.get("/destinatarios", include_in_schema=False)
def destinatarios(request: Request):
    return pagina(
        request=request,
        nombre="destinatarios.html",
    )


@app.get("/historial", include_in_schema=False)
def historial(request: Request):
    return pagina(
        request=request,
        nombre="historial.html",
    )


@app.get("/dashboard", include_in_schema=False)
def dashboard(request: Request):
    return pagina(
        request=request,
        nombre="dashboard.html",
    )