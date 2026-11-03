# Guía Técnica: Ingesta y Diagnóstico de SIMEL Chile (`obspred`)

> **Propósito:** Esta guía documenta la integración del **Sistema de Información del Mercado Laboral (SIMEL)** de Chile en la plataforma `obspred`, detallando las restricciones del Web Application Firewall (WAF) de Huawei Cloud, el diseño del conector institucional y el flujo de normalización de exportaciones tabulares (CSV).

---

## 1. Contexto Institucional y Desafío Técnico

### 1.1 ¿Qué es SIMEL?
SIMEL (`https://www.simel.gob.cl`) es la plataforma oficial coordinada por la **Mesa de Estadísticas del Trabajo** de Chile (integrada por el Instituto Nacional de Estadísticas - INE, el Ministerio del Trabajo y Previsión Social y con asistencia técnica de la OIT). Es la fuente primaria más exhaustiva sobre empleo, desocupación, salarios y estructura ocupacional desagregada por ramas de actividad económica (CAENES) y regiones.

### 1.2 La Restricción Perimetral: WAF de Huawei Cloud (HTTP 418)
A diferencia de APIs abiertas como las del Banco Mundial o el Banco Central de Chile, el portal público de SIMEL está alojado bajo el **Web Application Firewall (WAF) de Huawei Cloud** (`Server: CW`).

- **Comportamiento en vivo:** Cualquier cliente HTTP desatendido automatizado (scripts Python, `curl`, herramientas de scraping o cron jobs) recibe una respuesta de bloqueo inmediata con código **HTTP 418** (*I'm a teapot*) o desafíos anti-bot mediante cookies propietarias (`HWWAFSESID`, `HWWAFSESTIME`) y encabezados de intercepción (`block-event-id`).
- **Consecuencia de diseño:** No es metodológicamente viable ni confiable mantener un conector de sincronización REST automática en tiempo real sin una sesión interactiva de navegador.

---

## 2. Estrategia Arquitectónica de Ingesta

Para garantizar la honestidad de datos (Principio 4) y la trazabilidad (Principio 3), `obspred` adopta una **estrategia dual**:

```mermaid
flowchart TD
    subgraph Origen ["Portal Oficial SIMEL (Chile)"]
        A["simel.gob.cl<br/>(Huawei Cloud WAF)"]
    end

    subgraph Flujo1 ["Flujo A: Monitoreo & Sincronización REST"]
        B["POST /api/v1/ingesta/sync/simel-chile"]
        C["SimelChileConnector.check_health()"]
        D{"¿WAF Activo / 418?"}
        E["HTTP 502 Bad Gateway<br/>(Mensaje descriptivo y diagnóstico)"]
        F["RawIndicatorRecord (si WAF permite)"]
    end

    subgraph Flujo2 ["Flujo B: Carga de Exportación Tabular (Oficial)"]
        G["Explorador Interactivo SIMEL<br/>(Descarga CSV)"]
        H["POST /api/v1/ingesta/upload/simel"]
        I["FileUploadService<br/>(Validación y guardado local)"]
        J["SimelChileConnector.parse_simel_csv()"]
        K["IIndicadorRepository.upsert_batch()"]
        L[("Base de Datos<br/>indicadores (CHL)")]
    end

    A -.->|Petición desatendida| C
    B --> C
    C --> D
    D -->|Sí (418 / WAF)| E
    D -->|No| F

    A -->|Exportación manual/programada| G
    G --> H
    H --> I
    I --> J
    J --> K
    K --> L
```

---

## 3. Especificación del Conector: `SimelChileConnector`

El conector reside en [`backend/app/infrastructure/connectors/simel_chile_connector.py`](../app/infrastructure/connectors/simel_chile_connector.py) e implementa la interfaz canónica [`IExternalDataConnector`](../app/domain/interfaces/external_connector.py).

### 3.1 Monitoreo de Salud (`check_health`)
Evalúa la respuesta remota de `https://www.simel.gob.cl`. Si detecta el código `418`, la cookie `HWWAFSESID` o el encabezado `block-event-id`, registra un log de advertencia y retorna `False`, informando que la API no admite consultas desatendidas.

### 3.2 Mapeo de Sectores a Sectores Estratégicos
El motor de normalización traduce las ramas de actividad económica (CAENES) reportadas por SIMEL a los 5 sectores estratégicos del Observatorio:

| Rama SIMEL / CAENES | Sector Estratégico en `obspred` |
|---|---|
| Información y comunicaciones | `tecnologia` |
| Actividades de atención de la salud humana y de asistencia social | `salud` |
| Suministro de electricidad, gas, vapor / Minería | `energia` |
| Actividades de alojamiento y de servicio de comidas | `turismo` |
| Actividades profesionales, científicas y técnicas | `economia-conocimiento` |
| Total / Nacional | `None` *(macro / nacional general)* |

### 3.3 Normalización de Períodos y Formatos Numéricos
- **Períodos:** SIMEL expresa trimestres móviles textualmente (ej. `Ene - Mar 2024`, `Abr - Jun 2024`). El conector los traduce a notación ISO canónica (`2024-Q1`, `2024-Q2`, etc.).
- **Números:** Gestiona comas decimales típicas de las estadísticas oficiales chilenas (ej. `"8,5"` $\to$ `8.5`, `"1.250,5"` $\to$ `1250.5`).

---

## 4. Endpoints de la API

### 4.1 Intento de Sincronización REST
- **Ruta:** `POST /api/v1/ingesta/sync/simel-chile`
- **Comportamiento ante WAF activo:** Devuelve `HTTP 502 Bad Gateway` con el error:
  ```json
  {
    "success": false,
    "data": null,
    "message": "Fallo en la sincronización de 'SIMEL - INE Chile'.",
    "errors": [
      {
        "code": "EXTERNAL_SERVICE_ERROR",
        "detail": "La plataforma oficial de SIMEL Chile (www.simel.gob.cl) se encuentra protegida por el WAF de Huawei Cloud (HTTP 418 / desafío anti-bot)...",
        "field": "source"
      }
    ]
  }
  ```

### 4.2 Carga y Procesamiento de Exportación CSV
- **Ruta:** `POST /api/v1/ingesta/upload/simel`
- **Content-Type:** `multipart/form-data`
- **Parámetro:** `file` (archivo `.csv` descargado de SIMEL)
- **Respuesta exitosa (`HTTP 201 Created`):**
  ```json
  {
    "success": true,
    "data": {
      "source": "SIMEL - INE Chile",
      "status": "success",
      "total_fetched": 27,
      "total_persisted": 27,
      "execution_time_seconds": 0.045,
      "countries_synced": ["CHL"],
      "indicators_synced": [
        "empleo_total",
        "tasa_desempleo",
        "tasa_ocupacion",
        "tasa_participacion"
      ],
      "error_message": null
    },
    "message": "Exportación de SIMEL Chile procesada con éxito. 27 observaciones persistidas.",
    "errors": []
  }
  ```

---

## 5. Pruebas y Recursos de Ejemplo

1. **Dataset de prueba:**  
   [`data/examples/simel_chile_sample.csv`](../../data/examples/simel_chile_sample.csv) con 27 observaciones reales organizadas por sectores, ocupaciones y trimestres móviles.
2. **Script de diagnóstico interactivo:**  
   Ejecutar desde la raíz del backend:
   ```bash
   .venv/Scripts/python backend/test_conexion_simel.py
   ```
3. **Pruebas automatizadas:**
   - Pruebas unitarias del conector y parser:
     ```bash
     .venv/Scripts/pytest backend/tests/unit/test_simel_connector.py
     ```
   - Pruebas de integración de los endpoints:
     ```bash
     .venv/Scripts/pytest backend/tests/integration/test_simel_endpoint.py
     ```
