from __future__ import annotations

import sqlite3
import struct
from datetime import datetime, timedelta, timezone
from contextlib import contextmanager
from pathlib import Path
from threading import RLock
from typing import Any, Iterable

from backend.configuracion import config

def convertir_datetimeoffset(valor: bytes) -> datetime:
    """
    Convierte DATETIMEOFFSET de SQL Server a datetime de Python.
    El tipo ODBC utilizado por SQL Server es -155.
    """
    (
        anio,
        mes,
        dia,
        hora,
        minuto,
        segundo,
        fraccion,
        desplazamiento_horas,
        desplazamiento_minutos,
    ) = struct.unpack("<6hI2h", valor)

    zona = timezone(
        timedelta(
            hours=desplazamiento_horas,
            minutes=desplazamiento_minutos,
        )
    )

    return datetime(
        anio,
        mes,
        dia,
        hora,
        minuto,
        segundo,
        fraccion // 1000,
        tzinfo=zona,
    )

class BaseDatos:
    """Acceso pequeño y común para SQLite o SQL Server."""

    def __init__(self) -> None:
        self.tipo = config.DB_TIPO
        self._lock = RLock()
        if self.tipo == "sqlite":
            self._inicializar_sqlite()

    @contextmanager
    def conexion(self):
        if self.tipo == "sqlserver":
            try:
                import pyodbc
            except ImportError as exc:
                raise RuntimeError(
                    "Falta pyodbc. Ejecute: pip install -r requirements.txt"
                ) from exc

            partes = [
                f"DRIVER={{{config.SQL_DRIVER}}}",
                f"SERVER={config.SQL_SERVER}",
                f"DATABASE={config.SQL_DATABASE}",
                f"Encrypt={config.SQL_ENCRYPT}",
                f"TrustServerCertificate={config.SQL_TRUST_CERTIFICATE}",
            ]
            if config.SQL_TRUSTED:
                partes.append("Trusted_Connection=yes")
            else:
                partes.extend([f"UID={config.SQL_USER}", f"PWD={config.SQL_PASSWORD}"])
            cn = pyodbc.connect(";".join(partes), timeout=8)

            # SQL Server DATETIMEOFFSET / SQL_SS_TIMESTAMPOFFSET
            cn.add_output_converter(-155, convertir_datetimeoffset)
        else:
            cn = sqlite3.connect(config.SQLITE_RUTA, check_same_thread=False)
            cn.row_factory = sqlite3.Row
            cn.execute("PRAGMA foreign_keys = ON")

        try:
            yield cn
            cn.commit()
        except Exception:
            cn.rollback()
            raise
        finally:
            cn.close()

    def probar_conexion(self) -> bool:
        with self.conexion() as cn:
            cursor = cn.cursor()
            cursor.execute("SELECT 1")
            return cursor.fetchone()[0] == 1

    def consultar_uno(self, sql: str, parametros: Iterable[Any] = ()) -> dict[str, Any] | None:
        with self._lock, self.conexion() as cn:
            cursor = cn.cursor()
            cursor.execute(sql, tuple(parametros))
            fila = cursor.fetchone()
            if fila is None:
                return None
            columnas = [c[0] for c in cursor.description]
            return dict(zip(columnas, fila))

    def consultar_todos(self, sql: str, parametros: Iterable[Any] = ()) -> list[dict[str, Any]]:
        with self._lock, self.conexion() as cn:
            cursor = cn.cursor()
            cursor.execute(sql, tuple(parametros))
            filas = cursor.fetchall()
            columnas = [c[0] for c in cursor.description]
            return [dict(zip(columnas, fila)) for fila in filas]

    def ejecutar(self, sql: str, parametros: Iterable[Any] = ()) -> int:
        with self._lock, self.conexion() as cn:
            cursor = cn.cursor()
            cursor.execute(sql, tuple(parametros))
            return cursor.rowcount

    def insertar(self, sql: str, parametros: Iterable[Any] = ()) -> int:
        with self._lock, self.conexion() as cn:
            cursor = cn.cursor()

            if self.tipo == "sqlserver":
                sql_limpio = sql.strip().rstrip(";")

                cursor.execute(
                    f"""
                    {sql_limpio};
                    SELECT CAST(SCOPE_IDENTITY() AS INT) AS id;
                    """,
                    tuple(parametros),
                )

                while cursor.description is None:
                    if not cursor.nextset():
                        raise RuntimeError(
                            "SQL Server no devolvió el identificador creado"
                        )

                fila = cursor.fetchone()

                if fila is None or fila[0] is None:
                    raise RuntimeError(
                        "SQL Server devolvió un identificador vacío"
                    )

                return int(fila[0])

            cursor.execute(sql, tuple(parametros))
            return int(cursor.lastrowid)

    def _inicializar_sqlite(self) -> None:
        Path(config.SQLITE_RUTA).parent.mkdir(parents=True, exist_ok=True)
        esquema = """
        CREATE TABLE IF NOT EXISTS Configuracion (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            nombre_zona TEXT NOT NULL,
            limite_personas INTEGER NOT NULL,
            segundos_permanencia INTEGER NOT NULL,
            zona_restringida_activa INTEGER NOT NULL,
            zona_x1 REAL NOT NULL,
            zona_y1 REAL NOT NULL,
            zona_x2 REAL NOT NULL,
            zona_y2 REAL NOT NULL,
            horario_activo INTEGER NOT NULL,
            hora_inicio TEXT NOT NULL,
            hora_fin TEXT NOT NULL,
            alertas_activas INTEGER NOT NULL,
            cooldown_segundos INTEGER NOT NULL,
            confianza_minima REAL NOT NULL,
            actualizado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS Destinatarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT NOT NULL UNIQUE,
            activo INTEGER NOT NULL DEFAULT 1,
            creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS Alertas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            titulo TEXT NOT NULL,
            mensaje TEXT NOT NULL,
            nivel TEXT NOT NULL,
            cantidad_personas INTEGER NOT NULL DEFAULT 0,
            limite_personas INTEGER,
            id_seguimiento INTEGER,
            confianza_promedio REAL,
            fecha_hora TEXT NOT NULL,
            estado TEXT NOT NULL DEFAULT 'PENDIENTE',
            zona TEXT NOT NULL,
            captura_ruta TEXT,
            correo_enviado INTEGER NOT NULL DEFAULT 0,
            estado_correo TEXT NOT NULL DEFAULT 'PENDIENTE',
            detalle_json TEXT
        );

        CREATE TABLE IF NOT EXISTS Capturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alerta_id INTEGER NOT NULL,
            ruta TEXT NOT NULL,
            fecha_hora TEXT NOT NULL,
            FOREIGN KEY (alerta_id) REFERENCES Alertas(id) ON DELETE CASCADE
        );
        """
        with sqlite3.connect(config.SQLITE_RUTA) as cn:
            cn.executescript(esquema)
            cn.execute(
                """
                INSERT OR IGNORE INTO Configuracion (
                    id, nombre_zona, limite_personas, segundos_permanencia,
                    zona_restringida_activa, zona_x1, zona_y1, zona_x2, zona_y2,
                    horario_activo, hora_inicio, hora_fin, alertas_activas,
                    cooldown_segundos, confianza_minima
                ) VALUES (1, 'Aula de demostración', 2, 8, 0, 0.35, 0.20, 0.65, 0.85,
                          0, '06:00', '22:00', 1, 20, 0.45)
                """
            )
            cn.commit()


_instancia: BaseDatos | None = None


def obtener_base_datos() -> BaseDatos:
    global _instancia
    if _instancia is None:
        _instancia = BaseDatos()
    return _instancia
