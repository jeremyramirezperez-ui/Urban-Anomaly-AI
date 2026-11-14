from __future__ import annotations

from datetime import datetime, time
from zoneinfo import ZoneInfo
from backend.configuracion import config


def ahora_local() -> datetime:
    return datetime.now(ZoneInfo(config.ZONA_HORARIA))


def esta_dentro_del_horario(hora_inicio: str, hora_fin: str, momento: datetime | None = None) -> bool:
    momento = momento or ahora_local()
    inicio = time.fromisoformat(hora_inicio)
    fin = time.fromisoformat(hora_fin)
    actual = momento.timetz().replace(tzinfo=None)
    if inicio <= fin:
        return inicio <= actual <= fin
    return actual >= inicio or actual <= fin


def fecha_para_archivo(momento: datetime | None = None) -> str:
    return (momento or ahora_local()).strftime("%Y%m%d_%H%M%S_%f")
