# Guía de Base de Datos y Migraciones (`backend`)

> **Propósito:** Documentar el modelo de datos relacional, la estrategia de persistencia idempotente (Upsert) y los procedimientos para gestionar cambios de esquema mediante Alembic.

---

## 1. Motores Soportados y Conexión

El backend está configurado con **SQLAlchemy 2.0 (async)**:
- **Desarrollo local rápido:** SQLite con driver asíncrono `aiosqlite` (`sqlite+aiosqlite:///./obspred_dev.db`).
- **Entornos compartidos / Producción:** PostgreSQL con driver `asyncpg` (`postgresql+asyncpg://usuario:password@host:5432/db_name`).

La cadena de conexión se configura a través de la variable `DATABASE_URL` en el archivo `.env`.

---

## 2. Modelo Relacional Actual: Tabla `indicadores`

La tabla principal de persistencia de series normalizadas es `public.indicadores`:

```sql
CREATE TABLE indicadores (
    id SERIAL PRIMARY KEY,
    pais VARCHAR(10) NOT NULL,
    sector VARCHAR(100) NULL,
    ocupacion VARCHAR(150) NULL,
    indicador VARCHAR(100) NOT NULL,
    periodo VARCHAR(20) NOT NULL,
    valor DOUBLE PRECISION NOT NULL,
    tipo VARCHAR(20) NOT NULL,
    fuente VARCHAR(100) NOT NULL,
    fecha_actualizacion DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
```

### Índices de Rendimiento
- `ix_indicadores_id`: Índice primario.
- `ix_indicadores_busqueda_temporal`: Índice compuesto sobre `(pais, indicador, periodo)`.
- `ix_indicadores_pais`: Filtro raíz de jerarquía.
- `ix_indicadores_sector`: Filtro por sector estratégico.
- `ix_indicadores_ocupacion`: Filtro por ocupación priorizada.
- `ix_indicadores_indicador`: Búsqueda por métrica canónica.

---

## 3. Clave Lógica de Unicidad y Estrategia de Upsert

Para evitar registros duplicados al ejecutar sincronizaciones repetidas (idempotencia), el repositorio aplica un **Upsert lógico**:

$$\text{Clave Lógica} = (\text{pais}, \text{sector}, \text{ocupacion}, \text{indicador}, \text{periodo}, \text{fuente})$$

### Reglas de Actualización:
- Si ya existe un registro con la misma clave lógica:
  - Se actualizan `valor`, `tipo`, `fecha_actualizacion` y `updated_at`.
- Si no existe:
  - Se inserta un nuevo registro.
- **Tratamiento de Nulos:** Los campos `sector` y `ocupacion` son opcionales (datos macro o agregados nacionales). La búsqueda evalúa explícitamente `IS NULL` para evitar colisiones.

---

## 4. Gestión de Migraciones con Alembic

Todas las modificaciones de tablas, columnas o índices deben quedar registradas en un archivo de migración versionado en `backend/migrations/versions/`.

### Historial de Revisiones
| ID | Descripción | Fecha |
|---|---|---|
| `41855ddca8c9` | `001_create_indicadores_table` | 2026-10-07 |
| `48ad14f9fe02` | `002_add_updated_at_to_indicadores` | 2026-10-08 |

### Comandos de Uso Frecuente

> 💡 **Nota:** Ejecutar estos comandos desde el directorio `backend/` con el entorno virtual activo.

#### 1. Aplicar todas las migraciones pendientes:
```powershell
alembic upgrade head
```

#### 2. Revertir la última migración (Rollback):
```powershell
alembic downgrade -1
```

#### 3. Ver historial y estado actual:
```powershell
alembic current
alembic history --verbose
```

#### 4. Crear una nueva migración automática tras cambiar modelos ORM:
```powershell
alembic revision --autogenerate -m "descripcion_del_cambio"
```

> ⚠️ **Importante:** Siempre inspeccionar manualmente el archivo generado en `backend/migrations/versions/` antes de comitear para verificar que las sentencias `upgrade()` y `downgrade()` sean exactas e inocuas para los datos existentes.

---

## 5. Documentación Relacionada

- 📖 [Patrón Repositorio y Persistencia en Base de Datos (`patron-repositorio-y-persistencia.md`)](file:///c:/repos/obspred/backend/docs/patron-repositorio-y-persistencia.md)
- 📖 [Arquitectura de Capas y Principios de Diseño (`arquitectura-y-capas.md`)](file:///c:/repos/obspred/backend/docs/arquitectura-y-capas.md)
- 📖 [Inyección de Dependencias (`inyeccion-de-dependencias.md`)](file:///c:/repos/obspred/backend/docs/inyeccion-de-dependencias.md)
