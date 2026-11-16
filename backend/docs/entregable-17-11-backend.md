# Requerimientos y Plan de Acción Backend · Entregable 17/11 (Sprint 3)
# Observatorio Predictivo de Tendencias Socioeconómicas, Laborales y Educativas (`obspred`)

> **Destinatarios:** Equipo de Backend (Nicolás Snider, Colby Vertilus, Georgina Gisela Bosque), Instructora (María del Valle Bustos) y Jurado / Evaluadores de Innova Lab (Grupo N° 5).  
> **Fecha del Entregable:** Martes 17 de noviembre de 2026 (18:30 – 20:30 h).  
> **Rama Base:** `develop` (actualizada con PRs #54, #58 y #73 consolidados).  
> **Alcance Exclusivo:** Arquitectura, persistencia, ingesta, endpoints y base de datos del **Backend**.

---

## 1. Estado de Partida en `develop`

El backend llega al entregable del 17/11 en un estado técnico maduro y validado:
- **Calidad de Código:** 100% de reglas cumplidas con `ruff check backend` (0 advertencias, 0 errores) y formateo verificado con `ruff format`.
- **Cobertura de Pruebas:** **116 tests unitarios y de integración pasando** de forma consistente (`pytest backend`).
- **Control de Versiones y Migraciones:** 
  - PR #54 integrado (*Brechas domain persistence*).
  - PR #58 integrado (*ESCO taxonomías e indicadores enriquecidos*).
  - PR #73 integrado (*Migraciones defensivas e idempotentes*).
  - Cadena Alembic unificada en un único head: `f25a85840a80`.
- **Compatibilidad con Frontend:** Los contratos de las 5 vistas requeridas por la interfaz están desplegados operativamente bajo el prefijo `/api/v1/*` con envoltorio canónico `ApiResponse[T]`.

---

## 2. Objetivos Comprometidos del Backend (Sprint 3)

| # | Objetivo Comprometido | Estado | Evidencia en Repositorio |
|---|---|:---:|---|
| **1** | **Persistencia de Indicadores en DB** | ✅ Completado | Modelos relacionales `IndicadorModel`, `FuenteModel` y `HabilidadBrechaModel` persistiendo registros normalizados en PostgreSQL/SQLite. |
| **2** | **Endpoints de Series Temporales y Proyecciones** | ✅ Completado | `/api/v1/metricas/series` (series históricas multi-país ordenadas) y `/api/v1/metricas/proyecciones` (intervalos de confianza $\ge 3$ períodos). |
| **3** | **Módulo de Brechas de Habilidades y Oferta Formativa** | ✅ Completado | `/api/v1/brechas` y `/api/v1/brechas/{ocupacion}` mapeando demanda laboral vs oferta formativa y habilidades emergentes. |
| **4** | **Taxonomías Estandarizadas y Conector ESCO** | ✅ Completado | Conector `EscoConnector`, servicio `EscoSyncService` y soporte para enriquecimiento de metadatos en JSON (`detalles`) y `trimestre`. |
| **5** | **Trazabilidad y Fichas Metodológicas** | ✅ Completado | `/api/v1/fuentes` con auditoría de frescura (`activa`, `desactualizada`, `no_disponible`) y badges de origen (`observado`, `calculado`, `proyeccion`). |

---

## 3. Checklist Técnico Obligatorio para la Demo del 17/11

Para asegurar una presentación impecable sin sorpresas técnicas durante la demo en vivo, el equipo de backend debe ejecutar los siguientes pasos en orden estricto:

### Paso 1: Verificación de Esquema y Migraciones en Base de Datos

En el entorno donde se ejecute la demostración (base compartida en Supabase o PostgreSQL local):

```bash
# 1. Asegurar entorno virtual activo
cd backend
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 2. Aplicar migraciones hasta el último head
alembic -c alembic.ini upgrade head

# 3. Confirmar que el head activo coincida con el repositorio
alembic -c alembic.ini current
# Debe responder: f25a85840a80 (head)
```

**Validación de tablas requeridas en base de datos:**
- `indicadores`: debe incluir las columnas `trimestre` (VARCHAR) y `detalles` (JSON).
- `fuentes`: catálogo de organismos con constraint único en `nombre`.
- `habilidades_brechas`: tabla relacional con columnas `ocupacion`, `habilidad`, `demanda`, `oferta_formativa`, `emergente` y sus índices.
- `alembic_version`: debe registrar la versión `f25a85840a80`.

---

### Paso 2: Sembrado e Ingesta Inicial de Datos (Data Seeding)

Una base de datos vacía provocará que la interfaz muestre el estado *"Sin datos"* en todas las pantallas. Antes de iniciar la reunión de presentación, se deben disparar las ingestas iniciales:

#### A. Sincronización de Fuentes Externas (APIs Oficiales)
Ejecutar las siguientes peticiones HTTP vía cURL, Postman o Swagger (`http://localhost:8000/docs`):

1. **Banco Mundial (Indicadores Macroeconómicos Regionales):**
   ```http
   POST /api/v1/ingesta/sync/world-bank
   ```
   *Puebla tasa de desempleo e inflación para Argentina (ARG), Uruguay (URY) y Chile (CHL).*

2. **Datos Argentina (Series de Tiempo Oficiales):**
   ```http
   POST /api/v1/ingesta/sync/datos-argentina
   ```
   *Puebla series oficiales de empleo registrado por sector.*

3. **Taxonomías ESCO (Clasificación de Habilidades y Competencias):**
   ```http
   POST /api/v1/ingesta/sync/esco
   ```
   *Puebla la base semántica y taxonomías ocupacionales armonizadas.*

#### B. Carga Manual de Datasets Estructurados
1. **SIMEL Chile (Muestra Oficial de Trabajo Decente):**
   ```http
   POST /api/v1/ingesta/upload/simel
   Content-Type: multipart/form-data
   file: data/examples/simel_chile_sample.csv
   ```
   *Valida y persiste las observaciones de empleo por sector y región en Chile.*

2. **Verificación de Catálogo de Brechas:**
   Consultar:
   ```http
   GET /api/v1/brechas
   GET /api/v1/brechas/dev-software
   ```
   *Debe responder 200 OK con la lista de habilidades técnicas y blandas ponderadas por ocupación.*

---

### Paso 3: Health Check de Endpoints Esenciales (Smoke Test)

Verificar que las siguientes URLs respondan con código `200 OK` y la estructura canónica `ApiResponse`:

```json
{
  "success": true,
  "status_code": 200,
  "message": "Operación completada exitosamente",
  "data": { ... },
  "errors": null,
  "meta": { ... },
  "timestamp": "2026-11-17T..."
}
```

| Vista Frontend Dependiente | Endpoint Backend a Verificar | Parámetros Sugeridos para Demo |
|---|---|---|
| **Salud del Sistema** | `GET /api/v1/health` | — |
| **Filtros Globales** | `GET /api/v1/catalogo` | — |
| **Vista 1: Inicio (KPIs)** | `GET /api/v1/metricas/kpis` | `pais=ARG&sector=tecnologia` |
| **Vista 1: Evolución Demanda** | `GET /api/v1/metricas/series` | `indicador=puestos_demandados&pais=ARG,URY,CHL` |
| **Vista 1: Rankings** | `GET /api/v1/metricas/ranking` | `dimension=sector&orden=desc` |
| **Vista 2: Ocupaciones** | `GET /api/v1/indice-empleabilidad/ranking` | `pais=ARG` |
| **Vista 2: Ficha Técnica Ocupación** | `GET /api/v1/indice-empleabilidad/dev-software` | `pais=ARG` |
| **Vista 3: Series Temporales** | `GET /api/v1/metricas/series` | `indicador=tasa_desempleo&pais=ARG,CHL` |
| **Vista 3: Proyecciones** | `GET /api/v1/metricas/proyecciones` | `indicador=tasa_desempleo&pais=ARG` |
| **Vista 3: Comparador Países** | `GET /api/v1/metricas/comparativa` | `indicador=tasa_desempleo&paises=ARG,URY,CHL` |
| **Vista 3: Mapa de Calor** | `GET /api/v1/metricas/mapa-calor` | `indicador=puestos_demandados` |
| **Vista 4: Brechas de Habilidades** | `GET /api/v1/brechas` | `sector=tecnologia` |
| **Vista 4: Detalle Ocupación** | `GET /api/v1/brechas/dev-software` | — |
| **Vista 5: Trazabilidad y Fuentes** | `GET /api/v1/fuentes` | — |
| **Panel de Alertas** | `GET /api/v1/alertas` | — |

---

### Paso 4: Configuración de Ejecución y CORS del Servidor

Para que el frontend de los compañeros pueda consumir la API sin bloqueos de navegador:

1. **Levantar el servicio:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
2. **Orígenes CORS habilitados:**
   Verificar que `app/core/config.py` o `.env` incluya los orígenes de desarrollo de Vite:
   - `http://localhost:5173`
   - `http://127.0.0.1:5173`
   - `http://localhost:3000`

---

### Paso 5: Plan de Contingencia Técnico durante la Presentación

Si durante la demo en vivo ocurre alguna eventualidad técnica, backend debe contar con las siguientes soluciones inmediatas:

1. **Caída de conectividad a una API oficial externa (ej. Datos Argentina o Banco Mundial):**
   - **Solución:** Los endpoints de consulta (`/metricas/*`, `/indicadores`, `/fuentes`) consumen datos ya persistidos en la base relacional local/PostgreSQL. No dependen de la disponibilidad en tiempo real de la API externa para renderizar gráficos.
2. **Falla en el entorno Frontend:**
   - **Solución:** Mostrar la API en vivo a través de Swagger UI (`http://localhost:8000/docs`) o mediante la colección oficial de Postman en [backend/docs/obspred.postman_collection.json](obspred.postman_collection.json).
3. **Consulta de período o combinación sin registros:**
   - **Solución:** Demostrar cómo se cumple el **Principio 4 (Honestidad del dato)**: la API devuelve HTTP 200 con payload canónico y `"valor": null` o lista vacía, sin romper la aplicación con errores 500 y sin inventar valores ficticios.

---

## 4. Defensa Técnica: Los 10 Principios del Equipo en Backend

Ante preguntas de la instructora María del Valle Bustos o del equipo evaluador, el backend defiende su implementación bajo los siguientes principios de arquitectura:

1. **Clean Architecture & SOLID:** Separación estricta entre Dominio (`app/domain`), Aplicación/Servicios (`app/application`), Infraestructura/Conectores/Repositorios (`app/infrastructure`) y Controladores API (`app/api`).
2. **Inversión de Dependencias:** Inyección desacoplada mediante dependencias de FastAPI (`app/api/dependencies.py`).
3. **Trazabilidad Total (Principio 3):** Cada indicador expuesto adjunta su objeto `fuente` con nombre oficial, fecha de corte, estado (`activa`/`desactualizada`) y tipo metodológico (`observado`/`calculado`/`proyeccion`).
4. **Honestidad de Datos (Principio 4):** Prohibición absoluta de magic numbers, imputaciones arbitrarias o datos simulados sin validación.
5. **Criterio Riguroso de Proyecciones (Principio 5):** Ninguna proyección lineal o tendencial se calcula con menos de 3 períodos históricos comparables.
6. **Jerarquía Estricta de Filtros (Principio 9):** Los endpoints validan la cascada `País` $\longrightarrow$ `Sector` $\longrightarrow$ `Ocupación` $\longrightarrow$ `Período`.

---

## 5. Resumen de Comandos Rápidos de Verificación

```bash
# Correr linter Ruff
python -m ruff check backend

# Correr pruebas unitarias con resumen
python -m pytest backend -v

# Verificar estado de revisiones Alembic
alembic -c backend/alembic.ini heads
alembic -c backend/alembic.ini current

# Iniciar backend
uvicorn app.main:app --app-dir backend --reload --port 8000
```
