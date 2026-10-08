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
│   │   ├── exceptions/    # Excepciones de negocio (ej. file_upload)
│   │   ├── interfaces/    # Protocolos / contratos abstractos (puertos: storage, repos)
│   │   └── value_objects/ # Objetos de valor inmutables
│   ├── application/       # Orquestación de casos de uso y DTOs
│   │   ├── dtos/          # Objetos de transferencia de datos (ej. FileUploadDTO)
│   │   ├── services/      # Servicios de aplicación y casos de uso (ej. FileUploadService)
│   │   └── use_cases/     # Casos de uso específicos
│   ├── infrastructure/    # Implementaciones técnicas y detalles externos
│   │   ├── connectors/    # Conectores para APIs oficiales (AR, UY, CL, INT)
│   │   ├── persistence/   # Base de datos, modelos ORM y repositorios
│   │   └── storage/       # Adaptadores de almacenamiento físico (ej. LocalFileStorageService)
│   └── api/               # Capa de presentación HTTP / Controllers (FastAPI)
│       ├── dependencies.py# Inyección de dependencias
│       └── v1/            # Versionado de API v1
│           ├── router.py  # Enrutador central v1 (agrega todos los controladores)
│           ├── endpoints/ # Controladores HTTP (health, ingesta, prueba, etc.)
│           └── schemas/   # Esquemas Pydantic (Request/Response DTOs)
├── tests/                 # Suite de pruebas unitarias e integración
│   ├── unit/              # Pruebas unitarias de servicios y almacenamiento
│   └── integration/       # Pruebas de integración de endpoints HTTP
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

## Módulo de Ingesta — Carga de Archivos (`feature/backend_file_upload`)

El módulo de ingesta permite la recepción, validación y persistencia física de datasets tabulares en disco para su posterior normalización e inserción en base de datos.

### Endpoint: `POST /api/v1/ingesta/upload`

Permite subir archivos multipart (`multipart/form-data`) con las siguientes reglas de negocio:

- **Validación de formato:** Solo admite archivos con extensión `.csv` (case-insensitive).
- **Validación de contenido y estructura:**
  - Rechaza archivos vacíos o compuestos únicamente por espacios en blanco (`EmptyFileException`).
  - Inspección de contenido: detecta y rechaza archivos binarios o ejecutables disfrazados con extensión `.csv` (`InvalidFileContentException`).
  - Límite de tamaño: configurable vía `MAX_UPLOAD_SIZE_BYTES` (por defecto 50 MB), rechazando archivos que excedan la cuota (`FileSizeExceededException`).
- **Prevención de vulnerabilidades y trazabilidad:**
  - Sanitiza el nombre de archivo eliminando secuencias de *Directory / Path Traversal* (`../`).
  - Asigna un prefijo con marca de tiempo UTC (`<timestamp>_<nombre_original>`) para garantizar trazabilidad temporal y evitar sobreescritura accidental.
- **Persistencia física no bloqueante (High-Performance Async):**
  - Implementación en `LocalFileStorageService` utilizando `anyio.to_thread` para delegar operaciones de I/O en disco a un pool de hilos, evitando bloquear el *Event Loop* principal de FastAPI.
  - El directorio de almacenamiento es configurable mediante la variable de entorno `UPLOAD_DIR` (por defecto `data/uploads`).
  - Creación automática de directorios anidados si no existen.
- **Arquitectura Clean & SOLID:**
  - **Dominio:**
    - Entidad inmutable: `UploadedFile` (`app/domain/entities/uploaded_file.py`).
    - Contratos de puertos: `IFileStorageService` y `IFileValidator` (`app/domain/interfaces/`).
    - Excepciones tipadas de dominio: `InvalidFileExtensionException`, `EmptyFileException`, `FileSizeExceededException`, `InvalidFileContentException`, `FileStorageException`.
  - **Aplicación:**
    - Validador especializado desacoplado (SRP & OCP): `CsvFileValidator` (`app/application/validators/csv_file_validator.py`).
    - Orquestador del caso de uso (DIP): `FileUploadService` (`app/application/services/file_upload_service.py`).
    - DTO de salida: `FileUploadDTO` (`app/application/dtos/file_upload_dto.py`).
  - **Infraestructura:**
    - Adaptador de almacenamiento: `LocalFileStorageService` (`app/infrastructure/storage/local_file_storage_service.py`).
  - **Presentación (FastAPI):**
    - Inyección de dependencias tipada con `Annotated` (`app/api/dependencies.py`).
    - Documentación OpenAPI completa con respuestas y modelos tipados (`app/api/v1/endpoints/ingesta.py`).

#### Ejemplo de Petición (`curl`):
```bash
curl -X POST "http://localhost:8000/api/v1/ingesta/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@datos_empleo_2026.csv"
```

#### Ejemplo de Respuesta Exitosa (`HTTP 201 Created`):
```json
{
  "success": true,
  "status_code": 201,
  "message": "Archivo CSV subido y persistido con éxito.",
  "data": {
    "filename": "1791391414_datos_empleo_2026.csv",
    "original_filename": "datos_empleo_2026.csv",
    "file_path": "data/uploads/1791391414_datos_empleo_2026.csv",
    "size_bytes": 1024,
    "content_type": "text/csv"
  },
  "errors": null,
  "meta": null,
  "timestamp": "2026-10-07T16:40:00.000000Z"
}
```

#### Ejemplo de Respuesta de Error de Validación (`HTTP 400 Bad Request`):
```json
{
  "success": false,
  "status_code": 400,
  "message": "El archivo 'reporte.xlsx' no es válido. Solo se admiten archivos con extensión '.csv'.",
  "data": null,
  "errors": [
    {
      "code": "DOMAIN_RULE_VIOLATION",
      "detail": "El archivo 'reporte.xlsx' no es válido. Solo se admiten archivos con extensión '.csv'.",
      "field": null
    }
  ],
  "meta": null,
  "timestamp": "2026-10-07T16:40:00.000000Z"
}
```

## Módulo de Indicadores (`feature/bckend_indicadores`)

Expone el catálogo analítico de indicadores socioeconómicos, laborales y educativos bajo filtros jerárquicos.

### Endpoint: `GET /api/v1/indicadores`

Permite consultar series temporales de indicadores aplicando filtros de segmentación con las siguientes directrices arquitectónicas:

- **Query Model y Buenas Prácticas FastAPI:** Los parámetros se agrupan en el modelo Pydantic `IndicadoresFilterSchema` inyectado mediante `Annotated[IndicadoresFilterSchema, Query()]`.
- **Filtros Soportados:**
  - `pais`: Código o nombre del país (raíz ineludible de la jerarquía, ej. `ARG`, `URY`, `CHL`).
  - `sector`: Sector productivo o rama de actividad económica (ej. `Tecnología`, `Salud`).
  - `ocupacion`: Ocupación clave analizada.
  - `desde`: Período inicial del rango (ej. `2024-Q1`, `2023`).
  - `hasta`: Período final del rango (ej. `2024-Q4`, `2024`).
- **Sanitización y Validación Automática:** Pydantic elimina espacios en blanco periféricos (`str_strip_whitespace=True`) y convierte parámetros vacíos (`?pais=&sector=...`) a `None` de forma declarativa.
- **Respuesta Estándar:** Encapsulada bajo `ApiResponse[List[IndicadorItemSchema]]` incluyendo el detalle de filtros aplicados en el campo `meta.extra.filtros`.

#### Ejemplo de Petición (`curl`):
```bash
curl -X GET "http://localhost:8000/api/v1/indicadores?pais=ARG&sector=Tecnolog%C3%ADa&desde=2024-Q1&hasta=2024-Q4" \
  -H "accept: application/json"
```

#### Ejemplo de Respuesta Exitosa (`HTTP 200 OK`):
```json
{
  "success": true,
  "status_code": 200,
  "message": "Consulta de indicadores ejecutada con éxito.",
  "data": [],
  "errors": null,
  "meta": {
    "page": null,
    "per_page": null,
    "total": 0,
    "extra": {
      "filtros": {
        "pais": "ARG",
        "sector": "Tecnología",
        "ocupacion": null,
        "desde": "2024-Q1",
        "hasta": "2024-Q4"
      }
    }
  },
  "timestamp": "2026-10-07T18:55:00.000000Z"
}
```

## Persistencia y Migraciones de Base de Datos (SQLAlchemy + Alembic)

El Observatorio utiliza SQLAlchemy 2.0 (modo asíncrono) junto con Alembic para la gestión reproducible del esquema de base de datos.

### 1. Modelo Relacional: `IndicadorModel` (`app/infrastructure/persistence/models/indicador.py`)

La tabla `indicadores` almacena las series históricas y proyecciones garantizando trazabilidad completa:

| Columna | Tipo | Restricción | Descripción |
|---|---|---|---|
| `id` | `Integer` | PK, Autoincremental | Identificador único del registro |
| `pais` | `String(10)` | Not Null, Index | Código o sigla de país (`ARG`, `URY`, `CHL`) |
| `sector` | `String(100)` | Nullable, Index | Sector económico armonizado |
| `ocupacion` | `String(150)` | Nullable, Index | Ocupación clave analizada |
| `indicador` | `String(100)` | Not Null, Index | Identificador del indicador (ej. `tasa_desempleo`) |
| `periodo` | `String(20)` | Not Null, Index | Período temporal (ej. `2024-Q1`, `2024-01`) |
| `valor` | `Float` | Not Null | Valor numérico del indicador |
| `tipo` | `String(20)` | Not Null | Metodología: `observado`, `calculado`, `proyeccion` |
| `fuente` | `String(100)` | Not Null | Organismo fuente (ej. `ILOSTAT`, `INDEC`, `SENCE`) |
| `fecha_actualizacion` | `Date` | Not Null | Fecha de actualización del dato (`YYYY-MM-DD`) |
| `created_at` | `DateTime` | Not Null, Server Default | Marca de tiempo UTC de inserción |
| `updated_at` | `DateTime` | Nullable | Marca de tiempo UTC de última modificación |

**Índices Compuestos de Rendimiento:**
- `ix_indicadores_pais_sector_ocupacion`: Optimiza la búsqueda por jerarquía territorial y ocupacional.
- `ix_indicadores_busqueda_temporal`: Optimiza consultas de series de tiempo por país e indicador.

### 2. Comandos de Migración con Alembic

Alembic está configurado en modo asíncrono y toma dinámicamente la URL de conexión desde `settings.database_url` (compatible con PostgreSQL vía `asyncpg` y SQLite local vía `aiosqlite`).

Estando dentro del directorio `backend/`:
```bash
# Aplicar todas las migraciones pendientes hasta la última versión:
alembic upgrade head

# Revertir la última migración aplicada:
alembic downgrade -1

# Ver la revisión actual aplicada en la base de datos:
alembic current

# Generar una nueva migración automáticamente tras modificar modelos ORM:
alembic revision --autogenerate -m "descripcion_del_cambio"
```

> **Nota:** Si se ejecutan los comandos desde la raíz del repositorio, indicar la ruta del archivo de configuración con el flag `-c`: `alembic -c backend/alembic.ini upgrade head`.

## Fuentes de Datos y Conectores (Fuente de la Verdad)

La arquitectura de ingesta, el diseño de conectores externos (`app/infrastructure/connectors/`), los parámetros oficiales de APIs y el catálogo de datasets se rigen estrictamente por el siguiente documento de referencia:

> 📖 **Fuente de la Verdad:** [`documentacion/informe-fuentes-datos-observatorio.md`](../documentacion/informe-fuentes-datos-observatorio.md)

Este informe técnico documenta y valida:
- **Fuentes comparables regionales:**
  - **World Bank API:** Indicadores macroeconómicos y contexto regional (desempleo, participación laboral, matrícula terciaria, PIB per cápita).
  - **ILOSTAT (OIT):** Series de empleo por actividad económica (ISIC) y ocupación (ISCO), con ingesta recomendada vía CSV directo (`rplumber.ilo.org`).
  - **CEPALSTAT:** Árbol temático (`thematic-tree`) e indicadores socioeconómicos y educativos regionales.
- **Fuentes oficiales por país:**
  - **Argentina:** API Datos Argentina Series de Tiempo (`apis.datos.gob.ar/series/api/`), portal CKAN y microdatos EPH / Secretaría de Trabajo.
  - **Uruguay:** Catálogo Nacional CKAN (`catalogodatos.gub.uy`) y Datastore API; series complementarias ILOSTAT / CEPALSTAT y microdatos ECH.
  - **Chile:** Web Services Banco Central de Chile, portal CKAN, y datasets descargables de SIMEL (`simel.gob.cl`) y SENCE SABE.
- **Taxonomías y clasificaciones:** Mapeo de sectores a ISIC Rev. 4 y ocupaciones a ISCO-08 / ESCO.
- **Trazabilidad y contrato de datos:** Todo registro procesado e insertado debe cumplir el esquema estándar que incluye `fuente`, `fecha_actualizacion` y `tipo` (`observado`, `calculado`, `proyeccion`).

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

### 4. Ejecutar migraciones de base de datos
```bash
alembic upgrade head
```

### 5. Iniciar el servidor de desarrollo
```bash
uvicorn app.main:app --reload --port 8000
```
La documentación interactiva OpenAPI estará disponible en `http://localhost:8000/docs`.

### 6. Ejecutar suite de pruebas y calidad de código

Para ejecutar las pruebas, asegúrate de haber activado el entorno virtual (`.venv`) o invocar directamente el intérprete del entorno.

#### A. Ejecutar todas las pruebas

**Estando dentro del directorio `backend/`:**
```bash
# Con entorno virtual activo:
pytest -v

# Alternativa directa con el intérprete de Python:
python -m pytest -v
```

**Estando desde la raíz del repositorio (`obspred/`):**
```bash
# En Windows (PowerShell):
backend\.venv\Scripts\python -m pytest backend/tests -v

# En Linux / macOS:
backend/.venv/bin/python -m pytest backend/tests -v
```

#### B. Ejecutar pruebas por tipo / capa

```bash
# Solo pruebas unitarias (servicios de aplicación, validadores, persistencia física):
pytest tests/unit -v

# Solo pruebas de integración (endpoints FastAPI y contratos ApiResponse):
pytest tests/integration -v

# Ejecutar un archivo específico (ejemplo: validadores CSV):
pytest tests/unit/test_csv_file_validator.py -v

# Ejecutar pruebas del módulo de ingesta y almacenamiento:
pytest tests/unit/test_file_upload_service.py tests/integration/test_ingesta_upload.py -v
```

#### C. Verificación de linter y formato (Ruff)

El proyecto utiliza **Ruff** como linter y formateador estricto para garantizar el cumplimiento de PEP 8 y buenas prácticas:

```bash
# Verificar reglas de estilo e importaciones:
ruff check .

# Verificar y aplicar correcciones automáticas:
ruff check --fix .

# Verificar formato de código:
ruff format --check .
```

