# Scripts de Utilidad y Mantenimiento (`/scripts`)

Este directorio contiene scripts personalizados para tareas de diagnóstico, verificación y mantenimiento de datos del Observatorio.

## Scripts disponibles

### `verificar_trimestre.py`
Inspecciona la base de datos para diagnosticar, limpiar y corregir la consistencia de los campos `periodo` (año canónico) y `trimestre` (Q1..Q4) en la tabla `indicadores`.

**Modo diagnóstico:**
```bash
python scripts/verificar_trimestre.py
```

**Modo corrección y limpieza automática:**
```bash
python scripts/verificar_trimestre.py --corregir
```

### `poblar_datos_faltantes.py`
Puebla de manera idempotente los registros faltantes para la demo y desarrollo del Observatorio:
- Catálogo de fuentes oficiales de trazabilidad (`fuentes`).
- Catálogo de brechas de habilidades por ocupación (`habilidades_brechas`).
- Indicadores oficiales de Datos Argentina (series de empleo registrado y EPH).
- Taxonomías ocupacionales de ESCO.
- Dataset de muestra oficial de SIMEL Chile (INE).
- Series de indicadores macroeconómicos y laborales del Banco Mundial.
```bash
python scripts/poblar_datos_faltantes.py
```
