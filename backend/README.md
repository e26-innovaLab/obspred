# Backend — Observatorio Predictivo de Tendencias

Este directorio contiene el backend del **Observatorio Predictivo de Tendencias Socioeconómicas, Laborales y Educativas** (Argentina, Uruguay y Chile).

## Arquitectura y Principios de Diseño

El backend se encuentra estructurado bajo los principios de **Clean Architecture** (Arquitectura Limpia) y directrices **SOLID**:

```text
backend/
├── app/
│   ├── core/              # Configuración, constantes (sin magic strings) y logging
│   ├── domain/            # Reglas de negocio puras, entidades, excepciones e interfaces
│   │   ├── entities/      # Entidades de dominio
│   │   ├── exceptions/    # Excepciones de negocio
│   │   ├── interfaces/    # Protocolos / contratos abstractos (puertos)
│   │   └── value_objects/ # Objetos de valor inmutables
│   ├── application/       # Orquestación de casos de uso y DTOs
│   │   ├── dtos/          # Objetos de transferencia de datos
│   │   └── use_cases/     # Lógica de aplicación
│   ├── infrastructure/    # Implementaciones técnicas y detalles externos
│   │   ├── connectors/    # Conectores para APIs oficiales (AR, UY, CL, INT)
│   │   └── persistence/   # Base de datos, modelos ORM y repositorios
│   └── api/               # Capa de presentación HTTP (FastAPI)
│       ├── dependencies.py# Inyección de dependencias
│       └── v1/            # Enrutamiento, esquemas y endpoints versión 1
├── tests/                 # Suite de pruebas unitarias e integración
├── .env.example           # Plantilla de variables de entorno
├── .gitignore             # Exclusiones de Git específicas de Python
├── pyproject.toml         # Configuración del paquete y herramientas de calidad
└── requirements.txt       # Dependencias principales
```

### Reglas de Desarrollo
1. **Separación de responsabilidades:** La lógica de negocio (`domain/`) no depende de librerías externas ni de detalles de persistencia o frameworks web.
2. **Inversión de dependencias (DIP):** Las capas internas dependen de abstracciones (`domain/interfaces/`), mientras que `infrastructure/` y `api/` implementan e inyectan dichas abstracciones.
3. **Ausencia de cadenas mágicas (*magic strings*):** Toda ruta, estado, entorno o parámetro constante se declara mediante enumeraciones (`Enum`) o constantes fuertemente tipadas en `app/core/constants.py` y `app/core/config.py`.
4. **Convención lingüística:** Nombres de variables, funciones, clases y módulos en **inglés**. Documentación, docstrings y explicaciones en **español**.

## Puesta en Marcha Local

### 1. Crear y activar entorno virtual
```bash
python -m venv .venv
# En Windows (PowerShell):
.venv\Scripts\Activate.ps1
# En Linux / macOS:
source .venv/bin/activate
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
```bash
cp .env.example .env
```

### 4. Iniciar el servidor de desarrollo
```bash
uvicorn app.main:app --reload --port 8000
```
La documentación interactiva OpenAPI estará disponible en `http://localhost:8000/docs`.

### 5. Ejecutar suite de pruebas
```bash
pytest
```
