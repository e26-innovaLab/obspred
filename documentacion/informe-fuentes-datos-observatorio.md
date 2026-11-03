# Informe: Fuentes de datos y APIs candidatas

**Proyecto:** Observatorio predictivo de tendencias socioeconómicas, laborales y educativas (innova.lab, Grupo 5)  
**Fecha:** 6 de octubre de 2026 (Actualizado: Noviembre de 2026)

> **Nota de verificación técnica (Fuente de la Verdad):** Las URLs, códigos de indicadores, parámetros y esquemas relacionales fueron verificados técnicamente en vivo. Este documento constituye la **fuente de la verdad** oficial para la arquitectura de ingesta, conectores del backend (`app/infrastructure/connectors/`), contratos de API y catálogo de datos del Observatorio.

---

## 1. Objetivo

Identificar de dónde puede obtener datos el Observatorio para Argentina, Uruguay y Chile, qué endpoints se pueden consumir y qué huecos hay que cubrir con datasets descargables, para cumplir el flujo mínimo del MVP: consumir fuente oficial, actualizar, normalizar, calcular indicadores, visualizar e identificar fuente y fecha.

## 2. Conclusiones principales

- Tres fuentes con API cubren los tres países con la misma estructura: **World Bank, ILOSTAT y CEPALSTAT**. Son la base común para comparar.
- Argentina tiene una API nacional cómoda (Series de Tiempo), Chile tiene SIMEL (.Stat Suite SDMX oficial) y Banco Central, y Uruguay no tiene API laboral nacional, por lo que depende de las fuentes internacionales y de datasets.
- Las ocupaciones (~20) y las habilidades son el punto más sensible. Las APIs internacionales brindan ocupación solo a nivel amplio (ISCO 1 a 2 dígitos), mientras que las brechas de habilidades se complementan mediante fuentes como SABE (Chile), ESCO y O*NET.
- Todo lo que dependa de microdatos (EPH, ECH, ENE) o de listados (SABE, SIES) entra por descarga programada e ingesta de contingencia (CSV), no por API interactiva.

## 3. Fuentes con cobertura para los tres países

### 3.1 World Bank Indicators API (sin clave, 100% verificada)

```
https://api.worldbank.org/v2/country/ARG;URY;CHL/indicator/SL.UEM.TOTL.ZS?format=json&date=2010:2024&per_page=1000
```

| Indicador | Qué mide | Estado Verificado |
|---|---|---|
| `SL.UEM.TOTL.ZS` | Desempleo | Activo, datos anuales para ARG, URY, CHL |
| `SL.TLF.CACT.ZS` | Participación laboral | Activo |
| `SL.EMP.TOTL.SP.ZS` | Empleo sobre población | Activo |
| `SL.SRV.EMPL.ZS` | Empleo en servicios | Activo |
| `SL.IND.EMPL.ZS` | Empleo en industria | Activo |
| `NY.GDP.PCAP.CD` | PIB per cápita | Activo |
| `SE.TER.ENRR` | Matrícula terciaria | Activo |
| `IT.NET.USER.ZS` | Usuarios de internet | Activo |

**Uso:** contexto macro y comparación entre países. Datos anuales (campo `trimestre: null`) y con rezago.

### 3.2 ILOSTAT (OIT)

- **Vía recomendada para ingesta (CSV directo vía rplumber):**
  ```
  https://rplumber.ilo.org/data/indicator/?id=<INDICADOR>&ref_area=ARG+URY+CHL&format=.csv
  ```
  *(Nota técnica: Requiere enviar cabecera `User-Agent` de navegador para evitar bloqueo de Cloudflare).*
- **Catálogo y API SDMX:**
  - Catálogo SDMX: `https://sdmx.ilo.org/rest/dataflow/ILO`
  - *(Advertencia técnica: `sdmx.ilo.org` cuenta con protección activa de Cloudflare que puede rechazar clientes sin headers de navegador o peticiones concurrentes).*

**Indicadores verificados:**
- Desempleo: `UNE_DEAP_SEX_AGE_RT_A`
- Empleo por ocupación (ISCO): `EMP_TEMP_SEX_OCU_NB_A` (familia `EMP_TEMP_SEX_OCU_...`)
- Empleo por actividad económica (ISIC): `EMP_TEMP_SEX_ECO_NB_A` (familia `EMP_TEMP_SEX_ECO_...`)
- Salarios medios mensuales nominales: `EAR_4MTH_SEX_ECO_CUR_NB_A` (familia `EAR_...`)

**Uso:** fuente principal para sectores y ocupaciones, porque usa clasificaciones internacionales iguales en los tres países.  
**Limitación:** ISCO suele venir a 1 o 2 dígitos e ISIC por sección, no a nivel de ocupación puntual ni de subsector.

### 3.3 CEPALSTAT

- **Explorador y árbol de indicadores (Catálogo):**
  ```
  https://api-cepalstat.cepal.org/cepalstat/api/v1/thematic-tree?lang=es&format=json
  ```
- **Datos por indicador:**
  ```
  https://api-cepalstat.cepal.org/cepalstat/api/v1/indicator/{indicator_id}/data?lang=es&format=json
  ```

**Uso:** indicadores socioeconómicos y educativos comparables a nivel regional. Se consulta el árbol temático (`thematic-tree`), se extraen los IDs de indicadores deseados y se consumen sus datos directamente.

## 4. Fuentes por país

### Argentina

- **API Datos Argentina, Series de Tiempo**
  - Búsqueda: `https://apis.datos.gob.ar/series/api/search?q=desocupacion`
  - Consulta: `https://apis.datos.gob.ar/series/api/series?ids=<ID>&start_date=2015-01&format=json`
  - Parámetros: `ids` (varios separados por coma), `start_date`, `end_date`, `collapse` (year, quarter, month), `representation_mode` (value, change, percent_change), `limit`.
- **Portal CKAN:** `https://datos.gob.ar/api/3/action/package_search?q=empleo`
- **Descarga e ingesta:** INDEC EPH (microdatos), Secretaría de Trabajo (trabajo registrado, salarios y empleo por sector), datos abiertos de Educación (matrícula).

### Uruguay

- Sin API laboral nacional (lo reconoce el propio brief).
- **Catálogo Nacional (CKAN):** `https://catalogodatos.gub.uy/api/3/action/package_search?q=empleo`. Los recursos se pueden bajar como CSV o consultar con `datastore_search?resource_id=...`
- **Descarga e ingesta:** INE (ECH) y ANEP Observatorio de la Educación.
- En la práctica, Uruguay se sostiene sobre World Bank, ILOSTAT y CEPALSTAT.

### Chile

- **SIMEL (Sistema de Información del Mercado Laboral - `https://www.simel.gob.cl`):** plataforma oficial (Mesa de Estadísticas del Trabajo, INE y OIT).
  - **Referencia técnica oficial:** [Guía de uso de SIMEL - INE Chile](https://www.ine.gob.cl/simel/guia-de-uso).
  - **Arquitectura de la fuente y dos vías de ingesta:**
    1. **API SDMX Oficial (.Stat Suite del INE Chile):** La guía técnica oficial de uso documenta el acceso vía API RESTful bajo el estándar Dotstatsuite/SDMX en `https://sdmx.ine.gob.cl/rest/data/` (Agencia `CL01`). Este endpoint **no está bloqueado por el WAF**, responde en vivo y permite consultar series oficiales filtrando por dimensiones (`startPeriod`, rama CAENES, sexo y región) para flujos como `DF_TDES_SEXO` (desempleo), `DF_TOCU_SEXO` (ocupación), `DF_TP_SEXO` (participación) y `DF_OCURAMA_RAMA_SEXO` (empleo por actividad económica).
    2. **Portal Web Interactivo (`www.simel.gob.cl`):** Frontend de consulta gráfica para usuarios finales. Cuenta con WAF de Huawei Cloud (`Server: CW`, `HWWAFSESID`) que restringe clientes automatizados con `HTTP 418`.
  - **Conector implementado (`SimelChileConnector`):**
    - Sincroniza indicadores en tiempo real mediante `POST /api/v1/ingesta/sync/simel-chile` consumiendo los flujos SDMX oficiales de `sdmx.ine.gob.cl`.
    - Normaliza períodos (trimestres móviles como `2024-03-01/P3M` a `2024-Q1`).
    - Extrae e infiere automáticamente el campo opcional `trimestre` (`Q1`, `Q2`, `Q3`, `Q4`) para facilitar filtros analíticos sin romper el eje temporal de Recharts.
    - Ofrece soporte dual de contingencia para subir archivos CSV exportados desde el explorador web mediante `POST /api/v1/ingesta/upload/simel-csv`.
    - Pruebas y diagnóstico interactivo en `backend/test_conexion_simel.py` y dataset en `data/examples/simel_chile_sample.csv`.
- **Banco Central, Web Services** (requiere registro gratuito):
  `https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx?user=USUARIO&pass=CLAVE&firstdate=2020-01-01&timeseries=<CODIGO_SERIE>&function=GetSeries`
- **Datos abiertos (CKAN):** `https://datos.gob.cl/api/3/action/package_search?q=empleo`
- **Descarga e ingesta:** INE Encuesta Nacional de Empleo (ENE), SENCE SABE (avisos y habilidades, mensual), SIES y Mi Futuro de MINEDUC (matrícula y titulados).

## 5. Mapeo de sectores a clasificación (ISIC Rev.4, nivel sección)

| Sector | Sección ISIC |
|---|---|
| Tecnología | J (información y comunicaciones) |
| Salud | Q (salud humana y asistencia social) |
| Energía | D (electricidad y gas), posiblemente B (minas y petróleo) |
| Turismo | I (alojamiento y servicios de comida), aproximación |
| Economía del conocimiento | J y M (actividades profesionales y científicas) |

**Criterios de mapeo en conectores:**
- `DF_OCURAMA_RAMA_SEXO` (Chile): Mapea las ramas CAENES `J` -> Tecnología, `Q` -> Salud, `D` -> Energía, `I` -> Turismo, `M` -> Economía del Conocimiento.

## 6. Habilidades y ocupaciones

El brief no define fuente para esto, y las fuentes oficiales de los tres países son limitadas:

- **SABE (Chile):** única fuente oficial con habilidades y requisitos de avisos, solo para Chile y por descarga.
- **ESCO (Comisión Europea):** `https://ec.europa.eu/esco/api/search?text=desarrollador&type=occupation&language=es`. Taxonomía de ocupaciones y habilidades, con equivalencia a ISCO.
- **O\*NET (EE.UU.):** similar, requiere clave gratuita.

ESCO y O\*NET se adoptan como taxonomías normalizadas de referencia metodológica.

## 7. Puntos metodológicos consolidados

- **Las 20 ocupaciones:** las APIs dan ocupación amplia (ISCO 1 a 2 dígitos). Para ocupaciones puntuales (por ejemplo desarrollador de software, ISCO 2512, o enfermería) se utilizan microdatos y taxonomías ESCO/O*NET.
- **Frecuencia temporal:** Las fuentes anuales (Banco Mundial) guardan `trimestre: null` y `periodo: "YYYY"`. Las fuentes trimestrales (SIMEL Chile, ENE) guardan `trimestre: "QX"` y `periodo: "YYYY-QX"`.
- **Estrategia UPSERT:** La persistencia se realiza bajo clave lógica única `[pais, sector, ocupacion, indicador, periodo, fuente]`, previniendo duplicaciones e implementando actualización idempotente.

## 8. Estructura común del dato (Contrato de Entidad)

Un registro normalizado en base de datos (`indicadores`) y API:

```json
{
  "pais": "CHL",
  "sector": "Tecnología",
  "ocupacion": null,
  "indicador": "tasa_desempleo",
  "periodo": "2024-Q1",
  "trimestre": "Q1",
  "valor": 8.31,
  "tipo": "observado",
  "fuente": "SIMEL - INE Chile",
  "fecha_actualizacion": "2026-11-03"
}
```

* **`periodo`**: Clave temporal unificada para el eje X en gráficos (ej. `"2024-Q1"`, `"2024"`).
* **`trimestre`**: Campo auxiliar opcional (`"Q1"`, `"Q2"`, `"Q3"`, `"Q4"` o `null` si es serie anual).
* **`tipo`**: `observado`, `calculado` o `proyeccion`.
* **`fuente` y `fecha_actualizacion`**: Trazabilidad institucional para componentes `FuenteBadge`.

## 9. Endpoints disponibles en la API interna (FastAPI)

- `GET /api/v1/indicadores?pais=&sector=&ocupacion=&desde=&hasta=&trimestre=` (consulta con filtrado jerárquico).
- `GET /api/v1/fuentes` (auditoría de fuentes, estado activo y fecha de actualización).
- `POST /api/v1/ingesta/sync/simel-chile` (sincronización directa vía SDMX de INE Chile).
- `POST /api/v1/ingesta/upload/simel-csv` (carga manual de contingencia CSV de SIMEL).
- `POST /api/v1/ingesta/sync/world-bank` (sincronización con World Bank Indicators API).
- `POST /api/v1/ingesta/sync/ilostat` (sincronización con ILOSTAT).
- `POST /api/v1/ingesta/sync/bcentral-chile` (sincronización con Banco Central de Chile).

Frontend trabaja exclusivamente contra estos endpoints internos para evitar problemas de CORS, autenticación y estabilidad de conectores.

## 10. Estado actual de ejecución

1. **SIMEL Chile:** Conector implementado con extracción SDMX unificada, fallback CSV, tests unitarios (100% pasando) y migración Alembic `2cedef4ea4e2_add_trimestre_to_indicadores` aplicada.
2. **Postman:** Colección actualizada en `backend/docs/obspred.postman_collection.json` con llamadas de sincronización, carga y ejemplos 200 OK para Argentina, Uruguay y Chile.
3. **Scripts de Mantenimiento:** Herramientas de diagnóstico en [`/scripts`](../scripts/), incluyendo `verificar_trimestre.py`.
