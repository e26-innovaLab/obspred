# Especificación y Contratos de API (`backend`)

> **Propósito:** Definir el catálogo canónico de endpoints, parámetros, esquemas de solicitud/respuesta y códigos de estado HTTP para los equipos de Frontend, QA y Datos, en cumplimiento estricto del **Principio #2** (*Contrato de API primero*) y **Principio #9** (*Jerarquía estricta de filtros*).

---

## 1. Estándar de Respuesta Unificado (`ApiResponse[T]`)

Toda petición a la API —sea exitosa (2xx) o con error (4xx, 5xx)— responde bajo el esquema canónico `ApiResponse[T]`, implementando el patrón **Envelope Pattern** (Envoltorio Unificado).

### 1.1 ¿Por qué usamos este patrón? (Justificación Arquitectónica)

1. **Previsibilidad y Contrato Único para el Frontend:**
   - El cliente (React, Axios, Fetch, etc.) nunca tiene que adivinar la forma de la respuesta. La raíz del JSON siempre contiene las mismas claves: `success`, `status_code`, `message`, `data`, `errors`, `meta`, `timestamp`.
   - Si `success === true`, la carga útil de negocio se encuentra garantizada en `data`.
   - Si `success === false`, la información diagnóstica detallada se encuentra garantizada en `errors`.
2. **Separación Limpia de Datos de Negocio y Metadatos:**
   - La información de paginación (`page`, `per_page`, `total`) y el contexto de ejecución o filtros aplicados (`extra`) viajan en `meta`, evitando contaminar los esquemas de entidades o listas dentro de `data`.
3. **Auditoría y Trazabilidad Temporal:**
   - Cada respuesta incorpora `timestamp` en formato ISO 8601 UTC, permitiendo rastrear la vigencia exacta de las respuestas en memoria caché o logs de cliente.
4. **Resiliencia ante Errores:**
   - Permite devolver errores estructurados a nivel de campo (`field`) para validaciones de formularios en UI, junto con un código máquina (`code`) legible para internacionalización o manejo lógico de excepciones.

---

### 1.2 Anatomía del Contrato (TypeScript / JSON)

```typescript
interface ApiResponse<T> {
  success: boolean;            // true en 2xx, false en 4xx/5xx
  status_code: number;        // Código HTTP numérico redundante (ej. 200, 201, 400, 404, 500)
  message: string;            // Mensaje legible y descriptivo orientado al usuario
  data: T | null;             // Payload con la información tipada de negocio (null en error)
  errors: ApiError[] | null;  // Detalle de errores cuando success === false (null en éxito)
  meta: ApiMeta | null;       // Paginación o metadatos contextuales (filtros aplicados)
  timestamp: string;          // Estampa temporal ISO 8601 UTC (ej. "2026-10-13T22:40:00.123Z")
}

interface ApiError {
  code: string;               // Código máquina (ej. "VALIDATION_ERROR", "NOT_FOUND", "CSV_TOO_LARGE")
  detail: string;             // Explicación técnica o de negocio orientada al cliente
  field: string | null;       // Campo o parámetro causante (si aplica, ej. "pais", "archivo")
}

interface ApiMeta {
  page?: number | null;       // Número de página actual en listados
  per_page?: number | null;   // Registros por página
  total?: number | null;      // Total absoluto de registros existentes
  extra?: Record<string, unknown> | null; // Metadatos de contexto (ej. filtros aplicados)
}
```

---

### 1.3 ¿Cómo usar `ApiResponse[T]` en el Backend? (Python / FastAPI)

Toda la definición reside en [`backend/app/api/v1/schemas/response_schema.py`](file:///c:/repos/obspred/backend/app/api/v1/schemas/response_schema.py).

#### A. Definición del Esquema en Endpoints (`response_model`)
Al definir una ruta en FastAPI, siempre se declara `ApiResponse[T]` especificando el tipo genérico `T`:

```python
from fastapi import APIRouter, status
from app.api.v1.schemas.response_schema import ApiResponse, create_success_response
from app.api.v1.schemas.mi_entidad_schema import MiEntidadSchema

router = APIRouter()


# 1. Endpoint que devuelve un solo objeto:
@router.get(
    "/{id}",
    response_model=ApiResponse[MiEntidadSchema],
    status_code=status.HTTP_200_OK,
)
async def get_item(id: int) -> ApiResponse[MiEntidadSchema]:
    item = await service.get_by_id(id)
    return create_success_response(
        data=MiEntidadSchema.model_validate(item),
        message="Item obtenido exitosamente.",
    )


# 2. Endpoint que devuelve una lista con metadatos:
@router.get(
    "",
    response_model=ApiResponse[list[MiEntidadSchema]],
    status_code=status.HTTP_200_OK,
)
async def list_items() -> ApiResponse[list[MiEntidadSchema]]:
    items = await service.list_all()
    return create_success_response(
        data=[MiEntidadSchema.model_validate(i) for i in items],
        message="Listado obtenido con éxito.",
        meta=ResponseMeta(total=len(items)),
    )
```

#### B. Uso de las Funciones Constructoras (`create_success_response` vs `create_error_response`)

El módulo provee funciones constructoras fuertemente tipadas diseñadas para resolver inferencias de tipos con **Pylance** y **mypy**:

- **Para Respuestas Exitosas:**  
  Usa `create_success_response(data=..., message=..., status_code=..., meta=...)`.  
  *Beneficio:* Infiere automáticamente `T` a partir del argumento `data`, evitando advertencias de tipos genéricos invariantes.

- **Para Respuestas de Error:**  
  Usa `create_error_response(message=..., status_code=..., errors=..., meta=...)`.  
  *Beneficio:* Retorna estrictamente `ApiResponse[None]` con `data=None` y `success=False`.  
  *(Nota: En la arquitectura del proyecto, la mayoría de los errores se manejan automáticamente mediante los manejadores globales en `app/main.py` al lanzar una `DomainException`)*.

---

### 1.4 ¿Cómo consumir `ApiResponse<T>` en el Frontend? (React / TypeScript)

En el frontend, los servicios consumen el envoltorio y extraen el payload de manera segura:

```typescript
// Ejemplo de servicio en React / TypeScript
import axios from 'axios';

interface MiEntidad {
  id: number;
  nombre: string;
}

export async function fetchMiEntidad(id: number): Promise<MiEntidad> {
  const response = await axios.get<ApiResponse<MiEntidad>>(`/api/v1/mi-recurso/${id}`);
  
  // Verificación del contrato
  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.message || 'Error al obtener la entidad');
  }

  return response.data.data;
}
```


---

## 2. Convenciones Globales y Jerarquía de Filtros

1. **Jerarquía obligatoria de filtros:**
   $$\text{País} \longrightarrow \text{Sector} \longrightarrow \text{Ocupación} \longrightarrow \text{Período}$$
2. **Códigos de país canónicos (ISO alpha-3):**
   - `ARG` (Argentina)
   - `URY` (Uruguay)
   - `CHL` (Chile)
3. **Sectores estratégicos canónicos:**
   - `tecnologia`
   - `salud`
   - `energia`
   - `turismo`
   - `economia-conocimiento`
4. **Trazabilidad en cada registro:**
   Todo dato devuelto incluye `fuente`, `fecha_actualizacion` y `tipo` (`observado` | `calculado` | `proyeccion`).

---

## 3. Catálogo de Endpoints

### 3.1. Estado del Servicio (Health)

#### `GET /api/v1/health`
- **Descripción:** Comprueba operatividad del backend y componentes base.
- **Respuesta 200 OK:**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Servicio operando correctamente.",
  "data": {
    "status": "healthy",
    "environment": "development",
    "version": "1.0.0"
  },
  "errors": null,
  "meta": null,
  "timestamp": "2026-10-12T19:00:00.000000Z"
}
```

---

### 3.2. Indicadores Socioeconómicos

#### `GET /api/v1/indicadores`
- **Descripción:** Consulta series históricas y agregados de indicadores filtrados por taxonomía canónica.
- **Parámetros de Query:**
  | Parámetro | Tipo | Requerido | Descripción | Ejemplo |
  |---|---|---|---|---|
  | `pais` | string | No (Recomendado) | Código de 3 letras (`ARG`, `URY`, `CHL`) | `ARG` |
  | `sector` | string | No | Sector estratégico | `Tecnología` |
  | `ocupacion` | string | No | Ocupación específica | `Desarrollador de software` |
  | `indicador` | string | No | Nombre del indicador | `tasa_desempleo` |
  | `fuente` | string | No | Fuente de origen | `Banco Mundial` |
  | `desde` | string | No | Período inicial (inclusive) | `2020` |
  | `hasta` | string | No | Período final (inclusive) | `2024` |

- **Respuesta 200 OK:**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Indicadores recuperados exitosamente.",
  "data": [
    {
      "id": 1,
      "pais": "ARG",
      "sector": null,
      "ocupacion": null,
      "indicador": "tasa_desempleo",
      "periodo": "2024",
      "valor": 6.8,
      "tipo": "observado",
      "fuente": "Banco Mundial",
      "fecha_actualizacion": "2024-12-31"
    }
  ],
  "errors": null,
  "meta": {
    "page": null,
    "per_page": null,
    "total": 1,
    "extra": {
      "filtros": {
        "pais": "ARG",
        "sector": null,
        "ocupacion": null,
        "indicador": "tasa_desempleo",
        "fuente": "Banco Mundial",
        "desde": "2020",
        "hasta": "2024"
      }
    }
  },
  "timestamp": "2026-10-12T19:00:00.000000Z"
}
```

---

### 3.3. Índice de Empleabilidad

#### `GET /api/v1/indice-empleabilidad/{ocupacion}`
- **Descripción:** Obtiene el score integral de empleabilidad (0–100) y el desglose de sus 4 dimensiones metodológicas para una ocupación dada.
- **Parámetros de Path:**
  - `ocupacion`: Slug o identificador (ej. `dev-software`, `enfermeria`).
- **Parámetros de Query:**
  - `pais` (opcional): `ARG`, `URY`, `CHL`.
  - `sector` (opcional): Sector prioritario.
  - `periodo` (opcional): Período de cálculo (ej. `2026-Q1`).

- **Respuesta 200 OK:**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Índice de empleabilidad calculado exitosamente.",
  "data": {
    "ocupacion": "dev-software",
    "nombre": "Desarrollador de software",
    "pais": "ARG",
    "sector": "tecnologia",
    "periodo": "2026-Q1",
    "score_total": 84.5,
    "dimensiones": {
      "demanda_puestos": { "score": 90.0, "peso": 0.35 },
      "estabilidad_salarial": { "score": 82.0, "peso": 0.25 },
      "cobertura_formativa": { "score": 78.0, "peso": 0.20 },
      "crecimiento_reciente": { "score": 88.0, "peso": 0.20 }
    },
    "fuente": "innova.lab / Índices Armonizados",
    "tipo": "calculado",
    "fecha_actualizacion": "2026-10-01"
  },
  "errors": null,
  "meta": null,
  "timestamp": "2026-10-12T19:00:00.000000Z"
}
```

---

### 3.4. Tendencias y Proyecciones

#### `GET /api/v1/tendencias`
- **Descripción:** Series históricas y proyecciones a futuro con intervalos de confianza (requiere mínimo 3 períodos históricos comparables).
- **Parámetros de Query:**
  - `pais` (obligatorio para proyecciones): `ARG`, `URY`, `CHL`.
  - `indicador` (obligatorio): Nombre del indicador (ej. `empleo_registrado`, `salario_real`).
  - `sector` (opcional).
  - `ocupacion` (opcional).
  - `incluir_proyeccion` (bool, default `true`).

---

### 3.5. Módulo de Ingesta

#### A. Carga de Archivos Tabulares
- **Endpoint:** `POST /api/v1/ingesta/upload`
- **Content-Type:** `multipart/form-data`
- **Body:** `file`: Archivo con extensión `.csv`.
- **Validaciones:** Rechaza archivos vacíos o archivos binarios enmascarados como texto.

#### B. Sincronización Externa (Conectores Oficiales)
- **Endpoint:** `POST /api/v1/ingesta/sync/world-bank`
- **Content-Type:** `application/json`
- **Body (opcional):**
```json
{
  "paises": ["ARG", "URY", "CHL"],
  "indicadores": ["tasa_desempleo", "pib_per_capita"],
  "periodo_desde": "2018",
  "periodo_hasta": "2024"
}
```
- **Respuesta 200 OK:**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Sincronización de 'Banco Mundial' ejecutada exitosamente.",
  "data": {
    "source_name": "Banco Mundial",
    "status": "success",
    "records_fetched": 21,
    "records_persisted": 21,
    "duration_seconds": 1.45,
    "error_message": null
  },
  "errors": null,
  "meta": null,
  "timestamp": "2026-10-12T19:00:00.000000Z"
}
```
- **Respuesta ante falla (502 Bad Gateway):**
```json
{
  "success": false,
  "status_code": 502,
  "message": "Error de comunicación con el servicio externo 'Banco Mundial'.",
  "data": null,
  "errors": [
    {
      "code": "EXTERNAL_CONNECTOR_ERROR",
      "detail": "Timeout al conectar con api.worldbank.org",
      "field": null
    }
  ],
  "meta": null,
  "timestamp": "2026-10-12T19:00:00.000000Z"
}
```
