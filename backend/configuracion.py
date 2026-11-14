from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

RAIZ_PROYECTO = Path(__file__).resolve().parents[1]
load_dotenv(RAIZ_PROYECTO / ".env")


class ConfiguracionAplicacion:
    """Configuración central leída desde variables de entorno."""

    NOMBRE = "SecurityAPPCR"
    VERSION = "1.0.0"
    ZONA_HORARIA = os.getenv("ZONA_HORARIA", "America/Costa_Rica")

    FRONTEND_DIR = RAIZ_PROYECTO / "frontend"
    RECURSOS_DIR = RAIZ_PROYECTO / "backend" / "recursos"
    CAPTURAS_DIR = RECURSOS_DIR / "capturas"
    CORREOS_SIMULADOS_DIR = RECURSOS_DIR / "correos_simulados"
    MODELO_DIR = RECURSOS_DIR / "modelo_yolo"
    MODELO_YOLO = MODELO_DIR / "yolo11n.pt"
    MODELO_FUEGO = MODELO_DIR / "best_nano_111.pt"

    # Por defecto usa SQLite para que la demostración funcione sin instalar SQL Server.
    # Cambie DB_TIPO a sqlserver para usar los scripts de la carpeta database/.
    DB_TIPO = os.getenv("DB_TIPO", "sqlite").strip().lower()
    SQLITE_RUTA = Path(os.getenv("SQLITE_RUTA", str(RAIZ_PROYECTO / "securityappcr.db")))

    SQL_SERVER = os.getenv("SQL_SERVER", "localhost")
    SQL_DATABASE = os.getenv("SQL_DATABASE", "BD-SecurityAPPCR")
    SQL_DRIVER = os.getenv("SQL_DRIVER", "ODBC Driver 18 for SQL Server")
    SQL_TRUSTED = os.getenv("SQL_TRUSTED", "true").lower() == "true"
    SQL_USER = os.getenv("SQL_USER", "")
    SQL_PASSWORD = os.getenv("SQL_PASSWORD", "")
    SQL_ENCRYPT = os.getenv("SQL_ENCRYPT", "yes")
    SQL_TRUST_CERTIFICATE = os.getenv("SQL_TRUST_CERTIFICATE", "yes")

    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "SecurityAPPCR")
    SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

    CONFIANZA_MINIMA = float(os.getenv("CONFIANZA_MINIMA", "0.45"))
    TAMANO_MAX_IMAGEN_MB = int(os.getenv("TAMANO_MAX_IMAGEN_MB", "8"))
    INTERVALO_MONITOREO_MS = int(os.getenv("INTERVALO_MONITOREO_MS", "1200"))

    @classmethod
    def preparar_directorios(cls) -> None:
        for carpeta in (
            cls.RECURSOS_DIR,
            cls.CAPTURAS_DIR,
            cls.CORREOS_SIMULADOS_DIR,
            cls.MODELO_DIR,
            cls.SQLITE_RUTA.parent,
        ):
            carpeta.mkdir(parents=True, exist_ok=True)


config = ConfiguracionAplicacion()
config.preparar_directorios()
