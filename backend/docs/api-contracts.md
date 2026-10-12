# Especificación y Contratos de API (`backend`)

> **Propósito:** Definir el catálogo canónico de endpoints, parámetros, esquemas de solicitud/respuesta y códigos de estado HTTP para los equipos de Frontend, QA y Datos, en cumplimiento estricto del **Principio #2** (*Contrato de API primero*) y **Principio #9** (*Jerarquía estricta de filtros*).

---

## 1. Estándar de Respuesta Unificado (`ApiResponse[T]`)

Toda petición a la API —exitosa o con error— responde bajo el esquema canónico `ApiResponse[T]`.

### Estructura General

```typescript
interface ApiResponse<T> {
  success: boolean;            // true en 2xx, false en 4xx/5xx
  status_code: number;        // Código HTTP numérico (ej. 200, 404, 502)
  message: string;            // Mensaje legible para el cliente
  data: T | null;             // Carga útil de negocio
  errors: ApiError[] | null;  // Lista de errores detallados si success === false
  meta: ApiMeta | null;       // Paginación o metadatos de filtros aplicados
  timestamp: string;          // ISO 8601 UTC
}

interface ApiError {
  code: string;               // Código máquina (ej. "NOT_FOUND", "VALIDATION_ERROR")
  detail: string;             // Explicación técnica o de negocio
  field: string | null;       // Campo o parámetro causante (si aplica)
}

interface ApiMeta {
  page?: number | null;
  per_page?: number | null;
  total?: number | null;
  extra?: Record<string, unknown> | null;
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
