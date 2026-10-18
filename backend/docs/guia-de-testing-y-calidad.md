# Guía de Testing y Calidad de Código (`backend`)

> **Propósito:** Definir los estándares, herramientas y comandos para la ejecución de pruebas unitarias, de integración y validación estática de código (linter/formateador) en el backend de `obspred`.

---

## 1. Estrategia de Pruebas

El proyecto implementa la pirámide de testing clásica dividida en dos capas:

```text
backend/tests/
├── conftest.py          # Fixtures globales (cliente asíncrono, sesión SQLite en memoria)
├── unit/                # Pruebas unitarias puras (sin red ni base de datos real)
│   ├── test_csv_file_validator.py
│   ├── test_external_sync_service.py
│   ├── test_file_upload_service.py
│   ├── test_indicador_repository.py
│   ├── test_indice_empleabilidad_service.py
│   └── test_world_bank_connector.py
└── integration/         # Pruebas de integración HTTP (endpoints FastAPI)
    ├── test_health_endpoint.py
    ├── test_indicadores_endpoint.py
    ├── test_indice_empleabilidad_endpoint.py
    ├── test_ingesta_upload.py
    ├── test_sync_endpoint.py
    └── test_tendencias_endpoint.py
```

---

## 2. Reglas de Oro para Tests

1. **Las pruebas unitarias nunca tocan la red real:**
   Cualquier llamada a APIs externas (ej. World Bank) o servicios externos debe ser simulada mediante `unittest.mock.patch`, `AsyncMock` o `respx`.
2. **Aislamiento de Base de Datos:**
   Los tests que requieran persistencia utilizan una sesión SQLite transaccional asíncrona aislada (`aiosqlite`), garantizando que cada prueba comience y termine con un estado limpio.
3. **Mocks mediante Inyección de Dependencias en Integración:**
   En las pruebas de endpoints de FastAPI, los componentes pesados se sustituyen de forma limpia usando `app.dependency_overrides`:
   ```python
   # Ejemplo de sustitución en tests/integration/test_sync_endpoint.py:
   app.dependency_overrides[provide_world_bank_connector] = lambda: mock_connector
   ```

---

## 3. Ejecución de Tests con `pytest`

> 💡 **Nota:** Todos los comandos se ejecutan con el entorno virtual activo (`.venv`) desde el directorio `backend/`.

### Ejecutar toda la suite de pruebas
```powershell
pytest -v
```

### Ejecutar solo pruebas unitarias
```powershell
pytest tests/unit -v
```

### Ejecutar solo pruebas de integración
```powershell
pytest tests/integration -v
```

### Ejecutar un archivo de test específico
```powershell
pytest tests/unit/test_world_bank_connector.py -v
```

### Medir cobertura de código (Coverage)
```powershell
pytest --cov=app --cov-report=term-missing
```

---

## 4. Estándar de Calidad y Formato con `Ruff`

El proyecto utiliza **Ruff** como linter ultrarrápido y formateador estricto (configurado en `backend/pyproject.toml`).

### Reglas Clave:
- Cumplimiento de **PEP 8**.
- Verificación de tipos e importaciones ordenadas (`isort` integrado).
- Docstrings obligatorios en funciones y clases públicas.

### Comandos de Verificación:

#### 1. Inspeccionar errores de estilo e importaciones:
```powershell
ruff check .
```

#### 2. Corregir automáticamente problemas detectados:
```powershell
ruff check --fix .
```

#### 3. Verificar el formateo de código:
```powershell
ruff format --check .
```

#### 4. Formatear automáticamente todos los archivos:
```powershell
ruff format .
```

---

## 5. Checklist de Pre-Commit (Definition of Done para el Dev)

Antes de crear un commit o abrir un Pull Request:
- [ ] `pytest` pasa al 100% (cero tests fallidos o rotos).
- [ ] `ruff check .` no devuelve errores ni advertencias.
- [ ] `ruff format --check .` confirma que todos los archivos están formateados.
- [ ] Todo nuevo endpoint o función cuenta con docstrings explicativos en español.
