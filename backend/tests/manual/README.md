# Pruebas Manuales y Scripts de Diagnóstico (`backend/tests/manual/`)

Este directorio contiene scripts interactivos para verificar la conectividad en vivo, la autenticación y la respuesta de APIs externas de organismos oficiales.

> **Nota:** A diferencia de las pruebas automatizadas en `tests/unit/` y `tests/integration/`, estos scripts realizan peticiones de red reales contra servidores externos y están diseñados para ejecución manual o diagnóstico en desarrollo. No forman parte de la suite de CI/CD offline.

## Scripts disponibles

### 1. `test_conexion_chile.py`
Comprueba la conectividad y extracción con el servicio web REST SIETE del Banco Central de Chile.
- **Uso:**
  ```bash
  python backend/tests/manual/test_conexion_chile.py
  ```
- **Requisitos:** Requiere conexión a internet y credenciales configuradas en `.env` (`BCENTRAL_CHILE_USER`, `BCENTRAL_CHILE_PASS`).

### 2. `test_conexion_simel.py`
Diagnostica la conexión contra la API oficial SDMX de SIMEL (.Stat Suite del INE Chile) y verifica el parseo de muestras locales CSV.
- **Uso:**
  ```bash
  python backend/tests/manual/test_conexion_simel.py
  ```
- **Requisitos:** Requiere conexión a internet (para la etapa SDMX en vivo).

### 3. `test_datos_argentina.py`
Verifica el estado de salud, búsqueda y descarga de series temporales de la API de Datos Argentina (`apis.datos.gob.ar`).
- **Uso:**
  ```bash
  python backend/tests/manual/test_datos_argentina.py
  ```
- **Requisitos:** Requiere conexión a internet.
