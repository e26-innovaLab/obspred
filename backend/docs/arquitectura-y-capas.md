# Arquitectura de Capas y Principios de Diseño (`backend`)

> **Propósito:** Definir el modelo arquitectónico de **Clean Architecture** (Arquitectura Limpia) y directrices **SOLID** implementadas en el backend de `obspred`, estableciendo la regla de dependencias unidireccional y las responsabilidades de cada módulo.

---

## 1. La Regla de Dependencia

El principio rector de la arquitectura es: **las dependencias del código solo pueden apuntar hacia adentro**. 

- Los círculos/capas interiores no saben nada de los círculos exteriores.
- Ningún elemento de **Dominio** o **Aplicación** debe importar ni conocer frameworks web (FastAPI), librerías de persistencia (SQLAlchemy), ni clientes HTTP externos (HTTPX).

```mermaid
flowchart TD
    subgraph CapaAPI ["1. Capa API / Presentación (Exterior)"]
        FastAPI["FastAPI APIRouter"]
        Schemas["Pydantic Schemas"]
        Deps["dependencies.py"]
    end

    subgraph CapaInfra ["2. Capa de Infraestructura (Adaptadores)"]
        SQLAlchemy["SQLAlchemy Models & Repos"]
        Connectors["HTTP Connectors (World Bank, etc.)"]
        Storage["LocalFileStorageService"]
    end

    subgraph CapaApp ["3. Capa de Aplicación (Casos de Uso)"]
        Services["Application Services (ExternalSyncService, FileUploadService)"]
        DTOs["Data Transfer Objects (DTO)"]
    end

    subgraph CapaDomain ["4. Capa de Dominio (Núcleo Puro)"]
        Entities["Entidades de Negocio"]
        Interfaces["Puertos / Protocolos (IExternalDataConnector, IIndicadorRepository)"]
        Exceptions["Excepciones de Dominio"]
    end

    CapaAPI --> CapaApp
    CapaAPI --> Deps
    Deps --> CapaInfra
    CapaInfra -.-> CapaDomain
    CapaApp --> CapaDomain
    CapaInfra --> CapaApp
```

---

## 2. Responsabilidad Detallada de Cada Capa

### A. Capa de Dominio (`app/domain/`) — *El Núcleo*
Contiene la lógica y las reglas de negocio esenciales e inmutables del Observatorio.
- **`entities/`:** Modelos de negocio puros (atributos y reglas que no dependen de base de datos).
- **`interfaces/` (Puertos):** Interfaces abstractas o `Protocol` que definen contratos obligatorios para cualquier tecnología externa:
  - `IIndicadorRepository`: Operaciones requeridas de almacenamiento (`upsert_batch`, `get_filtered`).
  - `IExternalDataConnector`: Protocolo para ingesta de APIs externas (`fetch_indicators`, `health_check`).
  - `IFileStorageService`: Protocolo de persistencia de archivos físicos.
  - `IFileValidator`: Protocolo de validación de estructura de datasets.
- **`exceptions/`:** Jerarquía de excepciones de negocio (`DomainException`, `EntityNotFoundException`). No contienen códigos de estado HTTP ni lógica web.

### B. Capa de Aplicación (`app/application/`) — *Los Casos de Uso*
Orquesta el flujo de información entre el dominio y los puertos.
- **`services/`:** Contiene los casos de uso específicos del sistema:
  - `ExternalSyncService`: Coordina la extracción desde un conector y la persistencia en el repositorio.
  - `FileUploadService`: Valida y almacena archivos CSV en el sistema.
  - `IndiceEmpleabilidadService`: Calcula el índice multidimensional y desglosa sus 4 dimensiones.
- **`dtos/`:** Objetos inmutables de transferencia de datos entre capas internas (ej. `ExternalSyncResultDTO`, `FileUploadDTO`).

### C. Capa de Infraestructura (`app/infrastructure/`) — *Los Adaptadores*
Implementa los puertos definidos en el dominio utilizando herramientas tecnológicas concretas:
- **`connectors/`:** Adaptadores HTTP (`httpx`, `asyncio.gather`) para consumir APIs oficiales remotas (ej. `WorldBankConnector`).
- **`persistence/`:** 
  - `models/`: Modelos ORM de SQLAlchemy mapeados a tablas SQL (`IndicadorModel`).
  - `repositories/`: Implementaciones concretas de repositorios (`SqlAlchemyIndicadorRepository`).
  - `database.py`: Motor de base de datos asíncrono y generador de sesiones (`AsyncSession`).
- **`storage/`:** Adaptadores de almacenamiento físico en disco (`LocalFileStorageService`).

### D. Capa de API / Presentación (`app/api/`) — *El Front-facing*
Punto de entrada HTTP expuesto a través de FastAPI:
- **`v1/endpoints/`:** Controladores que reciben requests HTTP, validan parámetros de entrada, invocan dependencias inyectadas y devuelven respuestas.
- **`v1/schemas/`:** Esquemas Pydantic que validan solicitudes entrantes y serializan las respuestas salientes bajo el estándar `ApiResponse[T]`.
- **`dependencies.py`:** Contenedor y cables de conexión que construyen e inyectan las instancias concretas hacia los controladores.

---

## 3. ¿Dónde debe vivir mi código nuevo? (Guía de Decisión)

| Si necesitas... | Pertenece a... | Ubicación |
|---|---|---|
| Definir un nuevo contrato de repositorio o conector | **Domain (Interfaces)** | `app/domain/interfaces/` |
| Lanzar un error por una regla de negocio rota | **Domain (Exceptions)** | `app/domain/exceptions/` |
| Orquestar un nuevo caso de uso o cálculo | **Application (Services)** | `app/application/services/` |
| Consumir una nueva API externa (ej. CEPAL) | **Infrastructure (Connectors)** | `app/infrastructure/connectors/` |
| Crear una nueva tabla o modificar consultas SQL | **Infrastructure (Persistence)** | `app/infrastructure/persistence/` |
| Exponer un nuevo endpoint REST | **API (Endpoints)** | `app/api/v1/endpoints/` |
| Validar la estructura JSON de entrada/salida HTTP | **API (Schemas)** | `app/api/v1/schemas/` |
| Conectar una nueva clase para que FastAPI la inyecte | **API (Dependencies)** | `app/api/dependencies.py` |

---

## 4. Reglas Estrictas de Código

1. **Sin Cadenas Mágicas (*No Magic Strings*):** Toda constante de tiempo, nombre de indicador, clave de filtro o ruta base debe residir en `app/core/constants.py` o `app/core/config.py`.
2. **Convención de Idiomas:**
   - Nombres de clases, métodos, variables, atributos y rutas: **Inglés** (ej. `fetch_indicators`, `sync_service`).
   - Docstrings, mensajes de log, mensajes de error y documentación: **Español**.
3. **Tipado Estricto:** Toda función y método debe declarar tipos completos para argumentos y valor de retorno (`type hinting`).
