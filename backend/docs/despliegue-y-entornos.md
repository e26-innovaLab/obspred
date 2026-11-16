# Guía de Despliegue y Configuración de Entornos (`backend`)

> **Propósito:** Documentar los requerimientos de infraestructura, variables de entorno y comandos necesarios para desplegar y ejecutar el backend de `obspred` tanto en entornos locales como en servicios cloud compartidos (Render, Railway, Fly.io, AWS, etc.).

---

## 1. Requisitos Previos

- **Python:** 3.11+ (64-bit). Ver detalle y pasos en la [Guía de Instalación de Python](guia-instalacion-python.md).
- **Motor de Base de Datos:**
  - SQLite (incluido por defecto para desarrollo local).
  - PostgreSQL 15+ (recomendado para staging y producción).
- **Herramientas opcionales:** Docker y Docker Compose.

---

## 2. Variables de Entorno (`.env`)

El backend lee su configuración mediante `pydantic-settings`. Un archivo `.env` en la raíz de `backend/` debe contener como mínimo:

```ini
# Configuración del Entorno y API
ENVIRONMENT=development                # development | staging | production
API_V1_STR=/api/v1
PROJECT_NAME="Observatorio Predictivo - Backend"

# Servidor HTTP
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Configuración de Base de Datos
# Opción Local (SQLite):
DATABASE_URL=sqlite+aiosqlite:///./obspred_dev.db

# Opción Staging / Cloud (PostgreSQL):
# DATABASE_URL=postgresql+asyncpg://obspred_user:secreto@db-host:5432/obspred_db

# Almacenamiento Local de Archivos (Ingesta)
STORAGE_LOCAL_BASE_PATH=./storage_data
STORAGE_MAX_FILE_SIZE_BYTES=10485760   # 10 MB

# Conectores Externos
WORLD_BANK_API_BASE_URL=https://api.worldbank.org/v2
WORLD_BANK_TIMEOUT_SECONDS=15.0

# Seguridad y CORS (Orígenes permitidos para Frontend)
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000","https://*.render.com","https://*.vercel.app"]
```

---

## 3. Despliegue en Servicios Cloud PaaS (Render / Railway)

Para disponibilizar una URL pública para Frontend, QA y UX/UI:

### Comando de Build (Build Command)
```bash
pip install -r requirements.txt
```

### Comando de Inicio (Start Command)
```bash
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```
> 💡 **Nota:** Encadenar `alembic upgrade head && ...` asegura que cualquier nueva migración se aplique automáticamente antes de encender el servidor HTTP.

### Healthcheck Path
- Configurar el endpoint de monitoreo en: `/api/v1/health`.

---

## 4. Despliegue con Docker (Opcional)

Si el equipo opta por contenedores:

### `Dockerfile` sugerido para el backend:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```
