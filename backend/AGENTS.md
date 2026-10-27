# Guía de Trabajo para Agentes en Backend (`backend/AGENTS.md`)
# Observatorio Predictivo de Tendencias (`obspred`)

> **Propósito:** Esta guía define las directrices arquitectónicas, estándares de desarrollo, convenciones de tipado, manejo de excepciones, testing y flujo de trabajo para agentes de inteligencia artificial y desarrolladores que operan exclusivamente en el **Backend**.

---

## 1. Principios Fundamentales del Backend

Todo agente que opere en el directorio `backend/` debe cumplir estrictamente:

1. **Clean Architecture & SOLID:**
   - La lógica de negocio reside en `domain/` y es 100% pura (sin dependencias de frameworks, ORMs ni librerías HTTP).
   - Los casos de uso residen en `application/` (`services/`, `dtos/`).
   - Las conexiones externas (bases de datos, APIs de organismos, storage de archivos) residen en `infrastructure/`.
   - La capa de presentación y controladores HTTP reside en `api/` (FastAPI).
   - Inversión de Dependencias (DIP): La capa de aplicación consume interfaces definidas en `domain/interfaces/`. La implementación concreta vive en `infrastructure/persistence/` o `infrastructure/connectors/`.
2. **Contrato de API Primero (`ApiResponse[T]`):**
   - Toda respuesta HTTP (2xx, 4xx, 5xx) debe responder bajo el envoltorio canónico `ApiResponse[T]` definido en [`app/api/v1/schemas/response_schema.py`](app/api/v1/schemas/response_schema.py).
   - Nunca retornar diccionarios crudos ni modelos ORM directamente.
3. **Ausencia Absoluta de Cadenas Mágicas (*No Magic Strings*):**
   - Rutas, tags de OpenAPI, códigos de error, nombres de indicadores, estados y taxonomías deben declararse como `StrEnum` o `Final[str]` en [`app/core/constants.py`](app/core/constants.py).
4. **Honestidad de Datos (Principio 4):**
   - Si no hay observaciones para un período o país, responder `"valor": null`. **Nunca inventar datos ni omitir períodos.**
5. **Trazabilidad Total (Principio 3):**
   - Toda observación, serie o ranking debe incluir su objeto `fuente`: `fuente`, `fecha_actualizacion`, `estado_fuente` y `tipo` (`observado` | `calculado` | `proyeccion`).
6. **Regla de Proyecciones (Principio 5):**
   - Exigir **al menos 3 períodos históricos observados** para proyectar. De lo contrario, retornar `proyectable: false` con un mensaje claro en `motivo_no_proyectable`.
7. **Control Estricto de Git:**
   - **NUNCA ejecutar `git push`.** Las subidas y sincronizaciones remotas son potestad exclusiva de los desarrolladores humanos.

---

## 2. Convenciones de Código y Documentación

### 2.1 Idiomas
* **Nombres de identificadores:** Variables, funciones, clases, métodos y nombres de archivo en **español** o **inglés** según el módulo preexistente (mantener coherencia con la carpeta).
* **Documentación:** Docstrings, comentarios y mensajes de error al usuario en **español**.

### 2.2 Docstrings en Formato Google Estricto
Toda función, método, clase y módulo debe contar con docstring descriptivo:
```python
async def get_serie_historica(
    indicador: str,
    pais: str,
    desde: str | None = None,
) -> MetricasSeriesResponseSchema:
    """Procesa la obtención de series históricas ordenadas cronológicamente.

    Args:
        indicador: Slug o identificador del indicador solicitado.
        pais: Código ISO 3166-1 alpha-3 del país (ej. 'ARG').
        desde: Período inicial de corte opcional (inclusive).

    Returns:
        MetricasSeriesResponseSchema: Envoltorio ApiResponse con la serie temporal
            y los metadatos de trazabilidad de fuentes.

    Raises:
        EntityNotFoundException: Si no existen registros para los filtros dados.
    """
```

### 2.3 Estándar de Linter y Formato (Ruff)
* Longitud máxima de línea: **88 caracteres**.
* Reglas activas: `E` (pycodestyle), `F` (Pyflakes), `W` (warnings), `I` (isort), `B` (flake8-bugbear), `UP` (pyupgrade).
* Uso de sintaxis moderna de tipado: usar `T | None` en lugar de `Optional[T]`, y `StrEnum` en lugar de `(str, Enum)`.
* Comando de verificación obligatoria:
  ```bash
  .venv/Scripts/ruff check backend
  .venv/Scripts/ruff format backend
  ```

---

## 3. Inyección de Dependencias en FastAPI

Todas las dependencias de repositorio y servicios se resuelven mediante FastAPI `Depends` y tipado `Annotated`:
```python
from typing import Annotated
from fastapi import APIRouter, Depends, status
from app.api.dependencies import provide_indicador_repository
from app.domain.interfaces.indicador_repository import IIndicadorRepository


@router.get("", response_model=IndicadoresResponseSchema)
async def list_indicadores(
    repository: Annotated[IIndicadorRepository, Depends(provide_indicador_repository)],
) -> IndicadoresResponseSchema: ...
```

---

## 4. Manejo de Errores y Excepciones de Dominio

Todo error de negocio debe heredar de `DomainException` o `EntityNotFoundException` ([`app/domain/exceptions/base.py`](app/domain/exceptions/base.py)) y ser capturado por los manejadores globales en [`app/main.py`](app/main.py):

* **404 Not Found:** Lanzar `EntityNotFoundException(entity_name="Indicador", entity_id=slug)`.
* **400 Bad Request:** Lanzar una subclase específica de `DomainException` con mensaje claro.
* **422 Unprocessable Entity:** Validación automática vía schemas de Pydantic v2.
* **Códigos de error estándar:** Utilizar siempre el enum `ApiErrorCode` de [`app/core/constants.py`](app/core/constants.py).

---

## 5. Estándares para Agentes de IA en Pruebas Automatizadas

1. **Ubicación de Tests:**
   - Pruebas unitarias de servicios o lógica pura en `tests/unit/`.
   - Pruebas de integración de endpoints HTTP y contratos en `tests/integration/`.
2. **Estructura de las pruebas de endpoints:**
   - Usar `httpx.AsyncClient` o `starlette.testclient.TestClient`.
   - Validar tanto el código de estado HTTP (`200 OK`, `404 Not Found`, etc.) como la estructura del envoltorio `ApiResponse` (`success`, `data`, `errors`).
   - Validar que los campos de trazabilidad (`fuente`, `fecha_actualizacion`, `tipo`) estén presentes en la respuesta.
3. **Comando de ejecución de tests:**
   ```bash
   .venv/Scripts/pytest backend
   ```

---

## 6. Guía para Resolver comentarios `# TODO (Backend):`

Cuando un agente o desarrollador deba conectar un endpoint mockeado con datos reales:

1. **Crear o actualizar la interfaz en Dominio:**  
   Declarar el contrato abstracto en [`app/domain/interfaces/`](app/domain/interfaces/).
2. **Implementar el caso de uso en Aplicación:**  
   Crear el servicio en [`app/application/services/`](app/application/services/) y sus DTOs correspondientes en [`app/application/dtos/`](app/application/dtos/).
3. **Implementar el repositorio en Infraestructura:**  
   Escribir las consultas SQLAlchemy en [`app/infrastructure/persistence/repositories/`](app/infrastructure/persistence/repositories/).
4. **Proveer la dependencia:**  
   Registrar el provider en [`app/api/dependencies.py`](app/api/dependencies.py).
5. **Inyectar en el Endpoint:**  
   Reemplazar la simulación de datos en el controlador por la llamada al servicio inyectado.
6. **No romper el contrato:**  
   El `response_model` del endpoint debe permanecer idéntico para no afectar al frontend.

---

## 7. Protocolo de Verificación Pre-Entrega

Antes de dar por concluida cualquier interacción o cambio en backend, el agente debe ejecutar obligatoriamente:
```bash
# 1. Formateo automático de código
.venv/Scripts/ruff format backend

# 2. Análisis estático y linter
.venv/Scripts/ruff check backend

# 3. Suite completa de pruebas automatizadas
.venv/Scripts/pytest backend
```
Ningún cambio puede darse por concluido si existen advertencias de linter o pruebas fallidas.
