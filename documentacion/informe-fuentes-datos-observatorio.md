# Informe: Fuentes de datos y APIs candidatas

**Proyecto:** Observatorio predictivo de tendencias socioeconómicas, laborales y educativas (innova.lab, Grupo 5)
**Fecha:** 6 de octubre de 2026

> **Nota de verificación técnica (Fuente de la Verdad):** Las URLs, códigos de indicadores y parámetros fueron verificados técnicamente en vivo (octubre de 2026). Este documento constituye la **fuente de la verdad** oficial para la arquitectura de ingesta, conectores del backend (`app/infrastructure/connectors/`) y catálogo de datos del Observatorio.

---

## 1. Objetivo

Identificar de dónde puede obtener datos el Observatorio para Argentina, Uruguay y Chile, qué endpoints se pueden consumir y qué huecos hay que cubrir con datasets descargables, para cumplir el flujo mínimo del MVP: consumir fuente oficial, actualizar, normalizar, calcular indicadores, visualizar e identificar fuente y fecha.

## 2. Conclusiones principales

- Tres fuentes con API cubren los tres países con la misma estructura: **World Bank, ILOSTAT y CEPALSTAT**. Son la base común para comparar.
- Argentina tiene una API nacional cómoda (Series de Tiempo), Chile tiene SIMEL y Banco Central, y Uruguay no tiene API laboral nacional, así que depende de las fuentes internacionales y de datasets.
- Las ocupaciones (unas 20) y las habilidades son el punto más débil. Las APIs internacionales dan ocupación solo a nivel amplio, y las brechas de habilidades requieren fuentes que el brief todavía no resuelve.
- Todo lo que dependa de microdatos (EPH, ECH, ENE) o de listados (SABE, SIES) entra por descarga programada e ingesta, no por API.

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

**Uso:** contexto macro y comparación entre países. Datos anuales y con rezago.

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

- **SIMEL (Sistema de Información del Mercado Laboral - `https://www.simel.gob.cl`):** plataforma oficial (Mesa de Estadísticas del Trabajo, INE y OIT). La consulta se realiza desde su explorador interactivo.  
  *(Nota técnica para backend: El dominio cuenta con WAF activo de Huawei Cloud que bloquea peticiones HTTP desatendidas estándar con código 418. La ingesta debe realizarse mediante descarga programada de archivos exportados o scripts con sesión de navegador, no mediante endpoints REST simples).*
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

**Problemas a resolver con Data:** Tecnología y Economía del conocimiento se solapan en J, y Turismo y Energía no se capturan limpiamente con secciones. Hay que definir y documentar el criterio de cada sector.

## 6. Habilidades y ocupaciones

El brief no define fuente para esto, y las fuentes oficiales de los tres países son limitadas:

- **SABE (Chile):** única fuente oficial con habilidades y requisitos de avisos, solo para Chile y por descarga.
- **ESCO (Comisión Europea):** `https://ec.europa.eu/esco/api/search?text=desarrollador&type=occupation&language=es`. Taxonomía de ocupaciones y habilidades, con equivalencia a ISCO.
- **O\*NET (EE.UU.):** similar, requiere clave gratuita.

ESCO y O\*NET no son fuentes oficiales de los tres países, así que habría que justificarlas en la metodología como taxonomía de referencia, no como dato observado.

## 7. Puntos a decidir en equipo

- **Las 20 ocupaciones:** las APIs dan ocupación amplia (ISCO 1 a 2 dígitos). Para ocupaciones puntuales (por ejemplo desarrollador de software, ISCO 2512, o enfermería) hay que usar microdatos EPH, ECH y ENE, o SABE. Esto afecta el alcance del Índice de Empleabilidad.
- **Frecuencia:** World Bank e ILOSTAT son sobre todo anuales, mientras Series de Tiempo y SIMEL tienen series mensuales o trimestrales. Las tendencias y alertas tendrán frecuencias distintas según el país.
- **Uruguay** tendrá menos granularidad que los otros dos. Conviene documentarlo como limitación del MVP en lugar de ocultarlo.

## 8. Estructura común sugerida

Un registro por dato:

```json
{
  "pais": "ARG",
  "sector": "Tecnología",
  "ocupacion": "Desarrollador/a de software",
  "indicador": "tasa_desempleo",
  "periodo": "2024-Q1",
  "valor": 6.9,
  "tipo": "observado",
  "fuente": "ILOSTAT",
  "fecha_actualizacion": "2026-09-30"
}
```

El campo `tipo` toma `observado`, `calculado` o `proyeccion`, y junto con `fuente` y `fecha_actualizacion` cubre los requisitos de trazabilidad del brief.

## 9. Endpoints internos probables (Backend FastAPI)

- `GET /indicadores?pais=&sector=&ocupacion=&desde=&hasta=`
- `GET /indice-empleabilidad/{ocupacion}`
- `GET /tendencias/{indicador}`
- `GET /brechas/{ocupacion}`
- `GET /alertas`
- `GET /fuentes` (estado y última actualización)
- `POST /datasets/upload` (carga manual de CSV o XLSX)

Las APIs externas las consume el backend, no el navegador, por CORS, claves y rendimiento. Frontend trabaja contra estos endpoints internos.

## 10. Próximos pasos

1. Probar en Postman World Bank, Series de Tiempo e ILOSTAT, y guardar las respuestas como JSON de ejemplo.
2. Confirmar con Data el mapeo sector a ISIC y la lista de 20 ocupaciones.
3. Acordar con Backend la estructura común y los endpoints de la sección 9.
4. Armar mocks en `/mocks/*.json` con esa estructura para desarrollar el dashboard mientras tanto.
5. Documentar limitaciones (Uruguay, granularidad de ocupaciones, habilidades) para la presentación del Demo Day.
