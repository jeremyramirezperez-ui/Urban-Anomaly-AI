from pathlib import Path
import shutil

DESTINO = Path(__file__).with_name("yolo11n.pt")
try:
    from ultralytics import YOLO
except ImportError as exc:
    raise SystemExit("Instale las dependencias: pip install -r requirements.txt") from exc

YOLO("yolo11n.pt")
origen = Path("yolo11n.pt")
if not origen.exists():
    raise SystemExit("Ultralytics no creó yolo11n.pt")
shutil.copy2(origen, DESTINO)
print(f"Modelo guardado en: {DESTINO}")
