# 🛡️ SecurityAPPCR

Sistema inteligente de monitoreo que utiliza **visión artificial con YOLO11n** para detectar personas, evaluar anomalías y generar alertas automáticas.

Proyecto académico **Urban Anomaly AI**, desarrollado para el curso **BD-141 Big Data** del **Colegio Universitario de Cartago**.

---

## 👥 Proyecto en equipo y mi aporte

Proyecto desarrollado en equipo para el curso **BD-141 Big Data** del CUC.
Repositorio original del equipo: [andreyac1397/SecurityAppCR_Bigdata](https://github.com/andreyac1397/SecurityAppCR_Bigdata).

**Mi aporte (Jeremy Ramírez Pérez):**
- Entrené y ajusté modelos de detección con **YOLO**.
- Desarrollé la detección de **objetos abandonados**: el sistema genera una alerta cuando un objeto permanece en cámara más del tiempo configurado y cumple los criterios de visión definidos.

---

## 🚨 Funciones principales

- Detección y conteo de personas.
- Detección de aglomeraciones.
- Permanencia prolongada.
- Ingreso a zonas restringidas.
- Presencia fuera del horario permitido.
- Control del estado de la cámara.
- Capturas de evidencia.
- Alertas automáticas por correo.
- Historial de alertas.
- Administración de destinatarios.

---

## 🧰 Tecnologías

- Python 3.13
- FastAPI
- YOLO11n
- OpenCV
- SQL Server
- Jinja2
- HTML
- CSS
- JavaScript

---

## 📁 Estructura principal

```text
SecurityAPPCR/
│
├── backend/
│   ├── main.py
│   ├── configuracion.py
│   ├── base_datos.py
│   │
│   ├── modelos/
│   ├── rutas/
│   ├── servicios/
│   ├── repositorios/
│   ├── utilidades/
│   │
│   └── recursos/
│       ├── capturas/
│       ├── correos_simulados/
│       └── modelo_yolo/
│
├── database/
│   ├── 01_crear_base_datos.sql
│   ├── 02_crear_tablas.sql
│   ├── 03_crear_procedimientos.sql
│   └── 04_insertar_datos_iniciales.sql
│
├── frontend/
│   ├── templates/
│   ├── css/
│   ├── js/
│   └── imagenes/
│
├── documentacion/
├── pruebas/
│
├── .env.example
├── requirements.txt
└── README.md
```

### Partes principales

| Carpeta | Función |
|---|---|
| `backend/modelos` | Define y valida los datos utilizados por la aplicación. |
| `backend/rutas` | Contiene los endpoints de la API. |
| `backend/servicios` | Ejecuta la detección, reglas, alertas y envío de correos. |
| `backend/repositorios` | Gestiona las consultas y operaciones con la base de datos. |
| `backend/recursos` | Guarda el modelo YOLO, capturas y correos simulados. |
| `database` | Contiene los scripts para preparar SQL Server. |
| `frontend/templates` | Contiene las páginas y el layout compartido de Jinja2. |
| `frontend/js` | Controla la cámara, API, historial y destinatarios. |
| `frontend/css` | Contiene los estilos generales y del monitoreo. |
| `pruebas` | Contiene pruebas de detección, reglas, correo e integración. |

---

# ▶️ Ejecución del sistema

## Fase 1 — Clonar el repositorio

```bash
git clone https://github.com/andreyac1397/SecurityAppCR_Bigdata.git
```

```bash
cd SecurityAppCR_Bigdata
```

## Fase 2 — Crear el entorno virtual

```bash
py -3.13 -m venv venv
```

### Activar en CMD

```cmd
venv\Scripts\activate
```

### Activar en PowerShell

```powershell
.\venv\Scripts\Activate.ps1
```

## Fase 3 — Instalar dependencias

```bash
python -m pip install --upgrade pip
```

```bash
python -m pip install -r requirements.txt
```

## Fase 4 — Preparar SQL Server

Ejecutar en SQL Server Management Studio, respetando este orden:

```text
database/01_crear_base_datos.sql
database/02_crear_tablas.sql
database/03_crear_procedimientos.sql
database/04_insertar_datos_iniciales.sql
```

## Fase 5 — Configurar variables de entorno

Crear el archivo `.env` desde el ejemplo:

```cmd
copy .env.example .env
```

Completar en `.env` la conexión de SQL Server y la configuración del correo.

> El archivo `.env` contiene información privada y no debe subirse a GitHub.

## Fase 6 — Descargar el modelo

Si `yolo11n.pt` no está disponible:

```bash
python backend/recursos/modelo_yolo/descargar_modelo.py
```

## Fase 7 — Ejecutar la aplicación

```bash
python -m uvicorn backend.main:app --reload
```

Abrir en el navegador:

```text
http://127.0.0.1:8000
```
