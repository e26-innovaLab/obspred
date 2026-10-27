# Contrato de API para gráficos y filtros (Frontend → Backend)

**Proyecto:** Observatorio predictivo (`obspred`) · innova.lab, Grupo 5
**Equipo:** Frontend · **Fecha:** 8 de octubre de 2026 · **Estado:** propuesta para acordar con Backend y Data

> Principio 02 (AGENTS.md): el contrato se acuerda antes de buildear. Este documento dice qué necesita
> cada pantalla del Figma (Inicio, Explorar, Comparar, Tendencias, Fuentes) y con qué forma JSON.
> Frontend ya consume `/metricas/series` y `/metricas/proyecciones` desde un mock con esta misma forma
> (`frontend/src/services/mock/tendencias.ts`); el día que Backend responda, se cambia `VITE_USE_MOCKS=false`.

---

## 1. Reglas generales

| Tema | Acuerdo propuesto |
|---|---|
| Prefijo | `/api/v1` (ya definido en `backend/app/core/constants.py`). |
| Envoltorio | Toda respuesta usa el `ApiResponse` existente: `success`, `status_code`, `message`, `data`, `errors`, `meta`, `timestamp`. Incluye los 422 de validación de FastAPI (hoy salen con el formato por defecto `{"detail": [...]}`). |
| Nombres | `snake_case` en JSON. Frontend convierte a camelCase en `services/api/`. |
| País | ISO 3166-1 alfa-3: `ARG`, `URY`, `CHL`. Varios países separados por coma: `pais=ARG,URY`. |
| Sector | Slug fijo: `tecnologia`, `salud`, `energia`, `turismo`, `economia-conocimiento`. |
| Ocupación | Slug del catálogo (`dev-software`, `enfermeria`…). Lista definitiva: Data. |
| Período | `YYYY` (anual), `YYYY-Qn` (trimestral) o `YYYY-MM` (mensual). Siempre ordenado ascendente. |
| Valores | Número crudo (`6.9`, no `"6,9 %"`). El formato lo hace Frontend con la `unidad`. |
| Dato faltante | `"valor": null`. **No omitir el período ni imputar** (principio 04): el gráfico deja un hueco. |
| Trazabilidad | Cada serie, punto de comparativa o ranking trae `fuente`, `fecha_actualizacion`, `estado_fuente` y `tipo` (principio 03). |
| `tipo` | `observado` \| `calculado` \| `proyeccion`. |
| Fechas | `fecha_actualizacion` en `YYYY-MM-DD`; `timestamp` en ISO 8601 UTC. |

### Objeto `fuente` (se repite en todo el contrato)

```json
{
  "fuente": "ILOSTAT",
  "fecha_actualizacion": "2026-09-30",
  "estado_fuente": "activa",
  "tipo": "observado",
  "metodologia_url": null
}
```

| Campo | Tipo | Notas |
|---|---|---|
| `fuente` | string | Nombre legible del organismo. |
| `fecha_actualizacion` | string (date) | Última ingesta de ese dato. |
| `estado_fuente` | `activa` \| `desactualizada` \| `no_disponible` | Lo usa `FuenteBadge` para el color. |
| `tipo` | `observado` \| `calculado` \| `proyeccion` | |
| `metodologia_url` | string \| null | Opcional; enlace a la ficha metodológica. |

### Query params comunes

| Param | Tipo | Obligatorio | Ejemplo | Notas |
|---|---|---|---|---|
| `pais` | CSV de ISO3 | sí | `ARG,CHL` | Raíz de la jerarquía (principio 09). |
| `sector` | slug | no | `tecnologia` | |
| `ocupacion` | slug | no | `dev-software` | Requiere `sector` coherente; si no, 400. |
| `desde` / `hasta` | período | no | `2024-Q1` / `2026-Q2` | Sin `desde`: últimos 12 períodos. |

### Errores

| HTTP | `errors[].code` | Cuándo | Qué muestra Frontend |
|---|---|---|---|
| 400 | `VALIDATION_ERROR` | Param inválido (país desconocido, rango invertido). `field` indica cuál. | Mensaje + botón Reintentar |
| 404 | `NOT_FOUND` | Indicador u ocupación inexistente. | Mensaje |
| 200 | — | Consulta válida pero sin datos. **No usar 404 para esto.** | "Sin datos" |
| 503 | `FUENTE_NO_DISPONIBLE` | La fuente externa no responde y no hay caché. | Mensaje + Reintentar |

---

## 2. Qué pide cada pantalla del Figma

| Pantalla | Bloque | Endpoint |
|---|---|---|
| Inicio | Filtros País / Período | `GET /catalogo` |
| Inicio | 4 tarjetas "Indicadores principales" (valor + variación + mini línea) **(ya consumido con mock)** | `GET /metricas/kpis` |
| Inicio | Evolución de la demanda (línea) **(ya consumido con mock)** | `GET /metricas/series?indicador=puestos_demandados` |
| Inicio | Sectores con mayor demanda / Ocupaciones destacadas / Habilidades más solicitadas **(ya consumido con mock)** | `GET /metricas/ranking` (3 llamadas, `dimension` distinta) |
| Explorar | Filtros (país múltiple, sector, ocupación, período, habilidad) | `GET /catalogo` |
| Explorar / Comparar | Indicadores comparativos (tarjetas con valor por país) | `GET /metricas/comparativa` |
| Comparar países | Indicadores comparativos **(ya consumido con mock)** | `GET /metricas/comparativa` |
| Comparar países | Comparación de indicadores (una línea por país) **(ya consumido con mock)** | `GET /metricas/series` con `pais=ARG,URY,CHL` |
| Comparar países | Mapa de calor sector × país **(ya consumido con mock)** | `GET /metricas/mapa-calor` |
| Tendencias | Indicadores (3 tarjetas) | `GET /metricas/kpis` |
| Tendencias | Evolución de indicadores + "Seleccionar indicador" | `GET /metricas/series` **(ya consumido con mock)** |
| Tendencias | Proyección (histórico vs proyección) | `GET /metricas/proyecciones` **(ya consumido con mock)** |
| Tendencias | Tendencias destacadas | `GET /metricas/ranking?orden=variacion` |
| Tendencias | Cambios significativos marcados con "!" sobre la serie **(ya consumido con mock)** | `GET /alertas?tipo=variacion_significativa` |
| Fuentes y metodología | Fuentes, metodología, actualización | `GET /fuentes` |

---

## 3. Endpoints

### 3.1 `GET /api/v1/catalogo`

Llena los filtros. Reemplaza las listas fijas de `services/mock/catalogo.ts`.

```json
{
  "paises": [{ "id": "ARG", "nombre": "Argentina" }],
  "sectores": [{ "id": "tecnologia", "nombre": "Tecnología", "isic": ["J"] }],
  "ocupaciones": [{ "id": "dev-software", "nombre": "Desarrollador/a de software", "sector": "tecnologia", "isco": "2512" }],
  "indicadores": [
    {
      "id": "tasa_desempleo",
      "nombre": "Tasa de desempleo",
      "unidad": "%",
      "frecuencias": ["anual", "trimestral"],
      "desagregaciones": ["pais", "sector"],
      "descripcion": "Porcentaje de la población activa que busca trabajo y no lo encuentra."
    }
  ],
  "periodos": { "min": "2015-Q1", "max": "2026-Q2" }
}
```

`desagregaciones` le dice al Frontend qué filtros habilitar por indicador (por ejemplo, ocultar Ocupación
si el indicador solo existe a nivel país).

### 3.2 `GET /api/v1/metricas/series` — en uso por Tendencias

Una serie temporal por país. Alimenta los gráficos de línea.

| Param | Tipo | Obligatorio | Ejemplo |
|---|---|---|---|
| `indicador` | string | sí | `puestos_demandados` |
| `pais`, `sector`, `ocupacion`, `desde`, `hasta` | — | ver §1 | |
| `frecuencia` | `anual` \| `trimestral` \| `mensual` | no | Si se pide más agregada que la nativa, Backend agrega. |

```json
{
  "series": [
    {
      "pais": "ARG",
      "indicador": "puestos_demandados",
      "nombre": "Puestos demandados",
      "unidad": "avisos",
      "frecuencia": "trimestral",
      "puntos": [
        { "periodo": "2025-Q4", "valor": 1874, "tipo": "observado" },
        { "periodo": "2026-Q1", "valor": 1822, "tipo": "observado" },
        { "periodo": "2026-Q2", "valor": 1938, "tipo": "observado" }
      ],
      "fuentes": [
        { "fuente": "Datos Argentina — Series de Tiempo", "fecha_actualizacion": "2026-09-30", "estado_fuente": "activa", "tipo": "observado", "metodologia_url": null }
      ]
    },
    {
      "pais": "URY",
      "indicador": "puestos_demandados",
      "nombre": "Puestos demandados",
      "unidad": "avisos",
      "frecuencia": "trimestral",
      "puntos": [
        { "periodo": "2025-Q4", "valor": 612, "tipo": "observado" },
        { "periodo": "2026-Q1", "valor": null, "tipo": "observado" },
        { "periodo": "2026-Q2", "valor": 640, "tipo": "observado" }
      ],
      "fuentes": [
        { "fuente": "INE Uruguay — ECH", "fecha_actualizacion": "2026-08-15", "estado_fuente": "activa", "tipo": "observado", "metodologia_url": null }
      ]
    }
  ]
}
```

| Campo | Tipo | Notas |
|---|---|---|
| `series[]` | array | Una por país pedido, **aunque no tenga datos** (todos los `valor` en `null`). |
| `puntos[].valor` | number \| null | |
| `fuentes[]` | array de `fuente` | Puede haber más de una si la serie combina fuentes. |

Frontend pivotea a `[{ periodo, AR, UY, CL }]` para Recharts (`features/tendencias/utils/series.ts`),
así que el formato "largo" sirve igual si mañana cambiamos de librería.

### 3.3 `GET /api/v1/metricas/proyecciones` — en uso por Tendencias

| Param | Tipo | Obligatorio | Ejemplo |
|---|---|---|---|
| `indicador` | string | sí | `tasa_desempleo` |
| `pais` | ISO3 (uno solo) | sí | `ARG` |
| `sector`, `ocupacion` | slug | no | |
| `horizonte` | int | no (def. 2) | Períodos a proyectar. 2 trimestres = 6 meses. |

```json
{
  "pais": "ARG",
  "indicador": "puestos_demandados",
  "unidad": "avisos",
  "historico": [
    { "periodo": "2026-Q1", "valor": 1822, "tipo": "observado" },
    { "periodo": "2026-Q2", "valor": 1938, "tipo": "observado" }
  ],
  "proyeccion": [
    { "periodo": "2026-Q3", "valor": 1924.6, "limite_inferior": 1869.3, "limite_superior": 1979.9 },
    { "periodo": "2026-Q4", "valor": 1943.1, "limite_inferior": 1864.9, "limite_superior": 2021.3 }
  ],
  "proyectable": true,
  "motivo_no_proyectable": null,
  "metodo": "Regresión lineal sobre la serie trimestral observada",
  "nivel_confianza": 0.8,
  "periodos_historicos": 12,
  "fuentes": [
    { "fuente": "Datos Argentina — Series de Tiempo", "fecha_actualizacion": "2026-09-30", "estado_fuente": "activa", "tipo": "observado", "metodologia_url": null },
    { "fuente": "Observatorio (cálculo propio)", "fecha_actualizacion": "2026-10-01", "estado_fuente": "activa", "tipo": "proyeccion", "metodologia_url": "/fuentes#proyecciones" }
  ]
}
```

**Regla de las 3 series (principio 05):** si hay menos de 3 períodos observados comparables, Backend responde
**200** con `proyectable: false`, `proyeccion: []` y un `motivo_no_proyectable` legible
(ej. *"Hay 2 períodos con datos y se necesitan al menos 3 comparables."*). Frontend muestra ese texto.
Frontend también valida la regla por su cuenta, por si acaso.

`limite_inferior` / `limite_superior` dibujan la banda de confianza. El método (regresión, ARIMA, Holt…) lo
define Data; el contrato no cambia.

### 3.4 `GET /api/v1/metricas/kpis`

Tarjetas "Nombre del indicador / Valor / Variación · Tendencia" de Inicio y Tendencias.

| Param | Tipo | Obligatorio | Ejemplo |
|---|---|---|---|
| `indicadores` | CSV | sí | `tasa_desempleo,tasa_empleo,salario_real_indice,puestos_demandados` |
| `pais` | ISO3 (uno) | sí | `ARG` |
| `sector`, `ocupacion` | slug | no | |
| `periodo` | período | no | Sin valor: el último disponible por indicador. |

```json
{
  "kpis": [
    {
      "indicador": "tasa_desempleo",
      "nombre": "Tasa de desempleo",
      "unidad": "%",
      "periodo": "2026-Q2",
      "valor": 7.6,
      "periodo_anterior": "2026-Q1",
      "valor_anterior": 7.9,
      "variacion_abs": -0.3,
      "variacion_pct": -3.8,
      "tendencia": "caida",
      "sentido_positivo": "baja",
      "sparkline": [8.4, 8.2, null, 8.0, 7.9, 7.9, 7.6],
      "fuente": { "fuente": "INDEC — EPH", "fecha_actualizacion": "2026-09-24", "estado_fuente": "activa", "tipo": "observado", "metodologia_url": null }
    }
  ]
}
```

| Campo | Tipo | Notas |
|---|---|---|
| `tendencia` | `crecimiento` \| `estabilidad` \| `caida` \| null | Umbral de "estabilidad" lo define Data. |
| `sentido_positivo` | `sube` \| `baja` | Para pintar verde/rojo bien: que baje el desempleo es bueno. |
| `valor_anterior`, `variacion_*` | number \| null | `null` si no hay período anterior comparable. |
| `sparkline` | array de number \| null | Últimos 6–8 períodos, para la mini línea de la tarjeta. **En uso por Inicio.** |

### 3.5 `GET /api/v1/metricas/ranking`

Listas "Sectores con mayor demanda", "Ocupaciones destacadas", "Habilidades más solicitadas" y "Tendencias destacadas".

| Param | Tipo | Obligatorio | Ejemplo |
|---|---|---|---|
| `dimension` | `sector` \| `ocupacion` \| `habilidad` | sí | `sector` |
| `indicador` | string | sí | `puestos_demandados` |
| `pais` | ISO3 (uno) | sí | `CHL` |
| `sector` | slug | no | Filtra ocupaciones/habilidades de ese sector. |
| `periodo` | período | no | Último disponible. |
| `orden` | `valor` \| `variacion` | no (def. `valor`) | `variacion` para "Tendencias destacadas". |
| `limite` | int 1–20 | no (def. 5) | |

```json
{
  "dimension": "sector",
  "indicador": "puestos_demandados",
  "unidad": "avisos",
  "periodo": "2026-Q2",
  "items": [
    { "id": "tecnologia", "nombre": "Tecnología", "valor": 3120, "variacion_pct": 8.4, "tendencia": "crecimiento" },
    { "id": "salud", "nombre": "Salud", "valor": 2875, "variacion_pct": 1.1, "tendencia": "estabilidad" }
  ],
  "fuentes": [
    { "fuente": "SENCE — SABE", "fecha_actualizacion": "2026-09-01", "estado_fuente": "activa", "tipo": "observado", "metodologia_url": null }
  ]
}
```

> `dimension=habilidad` hoy solo tiene fuente oficial en Chile (SABE). Para ARG y URY Backend responde
> `items: []` y Frontend muestra "Sin datos" (ver informe de fuentes, §6).

### 3.6 `GET /api/v1/metricas/comparativa`

Tarjetas "Indicadores comparativos" de Explorar/Comparar: un indicador, un valor por país.

| Param | Tipo | Obligatorio | Ejemplo |
|---|---|---|---|
| `indicadores` | CSV | sí | `tasa_desempleo,tasa_empleo,salario_real_indice` |
| `pais` | CSV ISO3 | sí | `ARG,URY,CHL` |
| `sector`, `ocupacion` | slug | no | |
| `periodo` | período | no | Si un país no tiene ese período, se devuelve su último anterior con su propio `periodo`. |

```json
{
  "indicadores": [
    {
      "indicador": "tasa_desempleo",
      "nombre": "Tasa de desempleo",
      "unidad": "%",
      "valores": [
        { "pais": "ARG", "valor": 7.6, "periodo": "2026-Q2", "fuente": { "fuente": "INDEC — EPH", "fecha_actualizacion": "2026-09-24", "estado_fuente": "activa", "tipo": "observado", "metodologia_url": null } },
        { "pais": "URY", "valor": 7.9, "periodo": "2025", "fuente": { "fuente": "ILOSTAT", "fecha_actualizacion": "2026-07-10", "estado_fuente": "activa", "tipo": "observado", "metodologia_url": null } },
        { "pais": "CHL", "valor": null, "periodo": null, "fuente": null }
      ]
    }
  ]
}
```

El `periodo` por país es clave: Uruguay suele venir anual y Chile/Argentina trimestral. Frontend lo muestra
para no comparar períodos distintos sin avisar.

### 3.7 `GET /api/v1/metricas/mapa-calor` — en uso por Comparar países

Matriz de un indicador por sector (filas) y país (columnas). Frontend la dibuja con una tabla y CSS,
sin librería: cada celda muestra el número y el color agrupa en 5 pasos de la escala de marca.

| Param | Tipo | Obligatorio | Ejemplo |
|---|---|---|---|
| `indicador` | string | sí | `tasa_desempleo` |
| `pais` | CSV ISO3 | sí | `ARG,URY,CHL` |
| `filas` | `sector` | no (def. `sector`) | Dejamos abierto `ocupacion` para más adelante. |
| `periodo` | período | no | Último disponible. |

```json
{
  "indicador": "tasa_desempleo",
  "nombre": "Tasa de desempleo",
  "unidad": "%",
  "periodo": "2026-Q2",
  "filas": [{ "id": "tecnologia", "nombre": "Tecnología" }, { "id": "energia", "nombre": "Energía" }],
  "columnas": ["ARG", "URY", "CHL"],
  "celdas": [
    { "fila": "tecnologia", "columna": "ARG", "valor": 6.2, "variacion_pct": 5.8 },
    { "fila": "energia", "columna": "URY", "valor": null, "variacion_pct": null }
  ],
  "fuentes": [
    { "fuente": "ILOSTAT", "fecha_actualizacion": "2026-09-30", "estado_fuente": "activa", "tipo": "observado", "metodologia_url": null }
  ]
}
```

| Campo | Tipo | Notas |
|---|---|---|
| `celdas[]` | array | Una por cada combinación fila × columna, **también las vacías** (`valor: null`). |
| `variacion_pct` | number \| null | Contra el período anterior comparable. |

### 3.8 `GET /api/v1/fuentes`

Pantalla "Fuentes y metodología".

```json
{
  "fuentes": [
    {
      "id": "ilostat",
      "nombre": "ILOSTAT (OIT)",
      "descripcion": "Indicadores laborales armonizados por país.",
      "paises": ["ARG", "URY", "CHL"],
      "tipo_acceso": "api",
      "frecuencia": "anual",
      "ultima_actualizacion": "2026-09-30",
      "proxima_actualizacion": "2026-12-31",
      "estado_fuente": "activa",
      "url": "https://ilostat.ilo.org"
    }
  ],
  "metodologias": [
    { "id": "proyecciones", "titulo": "Proyecciones", "resumen": "Texto breve…", "url": null }
  ]
}
```

### 3.9 `GET /api/v1/indicadores` (ya existe) — ajustes pedidos

1. Aceptar `pais` múltiple (`ARG,URY,CHL`) además de uno.
2. Agregar `indicador` (CSV) como filtro.
3. Paginación en `meta` (`page`, `per_page`, `total`) si la lista supera ~1000 registros.

Lo usaríamos para tablas de detalle y descarga, no para los gráficos (para eso están los `/metricas/*`).

### 3.10 `GET /api/v1/alertas?tipo=variacion_significativa` — en uso por Tendencias

Cambios significativos de un indicador, para marcarlos sobre la línea. Cumple el requisito del MVP
"detección de al menos un tipo de cambio significativo".

| Param | Tipo | Obligatorio | Ejemplo |
|---|---|---|---|
| `tipo` | `variacion_significativa` | sí | Otros tipos posibles a futuro: `cambio_indice`, `nueva_brecha`, `fuente_desactualizada`. |
| `indicador` | string | sí | `puestos_demandados` |
| `pais` | ISO3 | sí | `ARG` |
| `sector`, `ocupacion`, `desde`, `hasta` | — | no | |

```json
{
  "alertas": [
    {
      "id": "puestos_demandados-ARG-2023-Q4",
      "pais": "ARG",
      "indicador": "puestos_demandados",
      "periodo": "2023-Q4",
      "variacion_pct": 8.0,
      "nivel": "alto",
      "titulo": "Puestos demandados: suba de 8 %",
      "descripcion": "Variación respecto del período anterior (T3 2023)."
    }
  ]
}
```

`periodo` tiene que coincidir con un período de `/metricas/series` para que el marcador caiga sobre la línea.
El umbral lo define Data; el mock usa 5 % (`medio`) y 8 % (`alto`). Si no hay cambios, `alertas: []`.

---

## 4. Decisiones pendientes

| # | Tema | Quién | Propuesta Frontend |
|---|---|---|---|
| 1 | Lista final de indicadores y sus `id` | Data | Los 5 del mock: `puestos_demandados`, `tasa_desempleo`, `tasa_empleo`, `salario_real_indice`, `empleo_registrado`. |
| 2 | Lista de 20 ocupaciones y slugs | Data | La de `services/mock/catalogo.ts`. |
| 3 | Método de proyección y nivel de confianza | Data | Empezar con regresión lineal al 80 %; el contrato no cambia si se reemplaza. |
| 4 | Umbral de "estabilidad" en `tendencia` | Data | ±2 % de variación. |
| 7 | Umbral de cambio significativo | Data | 5 % = medio, 8 % = alto, entre períodos consecutivos. |
| 5 | Formato de error en 422 | Backend | Envolver en `ApiResponse` con `VALIDATION_ERROR`. |
| 6 | CORS en desarrollo | Backend / Frontend | Proxy de Vite (`/api` → `localhost:8000`) para no depender de CORS. |
