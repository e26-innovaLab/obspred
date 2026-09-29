# Backend — Observatorio Predictivo de Tendencias

Este directorio contiene el backend del **Observatorio Predictivo de Tendencias Socioeconómicas, Laborales y Educativas** (Argentina, Uruguay y Chile).

## Arquitectura y Principios de Diseño

El backend se encuentra estructurado bajo los principios de **Clean Architecture** (Arquitectura Limpia) y directrices **SOLID**:

```text
backend/
├── app/
│   ├── core/              # Configuración, constantes (sin magic strings) y logging
│   ├── domain/            # Reglas de negocio puras, entidades, excepciones e interfaces
│   │   ├── entities/      # Entidades de dominio
│   │   ├── exceptions/    # Excepciones de negocio
│   │   ├── interfaces/    # Protocolos / contratos abstractos (puertos)
│   │   └── value_objects/ # Objetos de valor inmutables
│   ├── application/       # Orquestación de casos de uso y DTOs
│   │   ├── dtos/          # Objetos de transferencia de datos
│   │   └── use_cases/     # Lógica de aplicación
│   ├── infrastructure/    # Implementaciones técnicas y detalles externos
│   │   ├── connectors/    # Conectores para APIs oficiales (AR, UY, CL, INT)
│   │   └── persistence/   # Base de datos, modelos ORM y repositorios
│   └── api/               # Capa de presentación HTTP / Controllers (FastAPI)
│       ├── dependencies.py# Inyección de dependencias
│       └── v1/            # Versionado de API v1
│           ├── router.py  # Enrutador central v1 (agrega todos los controladores)
│           ├── endpoints/ # Controladores HTTP / Endpoints (health, indicadores, etc.)
│           └── schemas/   # Esquemas Pydantic de entrada/salida (Request/Response DTOs)
├── tests/                 # Suite de pruebas unitarias e integración
├── .env.example           # Plantilla de variables de entorno
├── .gitignore             # Exclusiones de Git específicas de Python
├── pyproject.toml         # Configuración del paquete y herramientas de calidad
└── requirements.txt       # Dependencias principales
```

### ¿Dónde se ubican los Controllers? (Capa API `app/api/`)
En esta implementación de Clean Architecture con FastAPI, el rol tradicional de los **Controllers** se distribuye de la siguiente manera:
- **Controladores / Endpoints ([`app/api/v1/endpoints/`](app/api/v1/endpoints/)):** Albergan los handlers de rutas (`APIRouter`). Su función exclusiva es recibir las solicitudes HTTP, aplicar validaciones de entrada, coordinar la inyección de dependencias y delegar la lógica de negocio a los casos de uso correspondientes ([`app/application/use_cases/`](app/application/use_cases/)).
- **Enrutador Central ([`app/api/v1/router.py`](app/api/v1/router.py)):** Centraliza y monta todos los submódulos de endpoints bajo la versión de la API correspondiente.
- **Punto de Entrada ([`app/main.py`](app/main.py)):** Inicializa la aplicación FastAPI, registra middlewares (como CORS) e incluye el enrutador central.
- **Modelos de Transferencia / Schemas ([`app/api/v1/schemas/`](app/api/v1/schemas/)):** Definen los contratos estrictos de entrada y salida mediante modelos Pydantic.

### Estándar de Respuestas REST (`ApiResponse[T]`)
Todas las llamadas a la API (tanto exitosas como con errores o excepciones) responden con un envoltorio uniforme bajo el esquema `ApiResponse[T]` ([`app/api/v1/schemas/response_schema.py`](app/api/v1/schemas/response_schema.py)):

```json
{
  "success": true,
  "status_code": 200,
  "message": "Operación ejecutada con éxito.",
  "data": { ... },
  "errors": null,
  "meta": null,
  "timestamp": "2026-09-29T21:24:35.123456Z"
}
```

En caso de error (HTTP 4xx o 5xx):
```json
{
  "success": false,
  "status_code": 404,
  "message": "La entidad 'Occupation' con ID '999' no fue encontrada.",
  "data": null,
  "errors": [
    {
      "code": "ENTITY_NOT_FOUND",
      "detail": "La entidad 'Occupation' con ID '999' no fue encontrada.",
      "field": "Occupation"
    }
  ],
  "meta": null,
  "timestamp": "2026-09-29T21:24:35.123456Z"
}
```

### Reglas de Desarrollo
1. **Separación de responsabilidades:** La lógica de negocio (`domain/`) no depende de librerías externas ni de detalles de persistencia o frameworks web.
2. **Inversión de dependencias (DIP):** Las capas internas dependen de abstracciones (`domain/interfaces/`), mientras que `infrastructure/` y `api/` implementan e inyectan dichas abstracciones.
3. **Ausencia de cadenas mágicas (*magic strings*):** Toda ruta, estado, entorno o parámetro constante se declara mediante enumeraciones (`Enum`) o constantes fuertemente tipadas en `app/core/constants.py` y `app/core/config.py`.
4. **Convención lingüística:** Nombres de variables, funciones, clases y módulos en **inglés**. Documentación, docstrings y explicaciones en **español**.
5. **Estándar unificado de respuesta:** Toda respuesta REST debe encapsularse en `ApiResponse[T]`. Los manejadores globales de excepciones en `app/main.py` garantizan que incluso los errores no controlados respeten este formato.

## Puesta en Marcha Local

### 1. Crear y activar entorno virtual
```bash
python -m venv .venv
# En Windows (PowerShell):
.venv\Scripts\Activate.ps1
# En Linux / macOS:
source .venv/bin/activate
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
```bash
cp .env.example .env
```

### 4. Iniciar el servidor de desarrollo
```bash
uvicorn app.main:app --reload --port 8000
```
La documentación interactiva OpenAPI estará disponible en `http://localhost:8000/docs`.

### 5. Ejecutar suite de pruebas
```bash
pytest
```
