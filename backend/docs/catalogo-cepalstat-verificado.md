# Catálogo Verificado de Indicadores CEPALSTAT (`obspred`)

> **Propósito:** Documento de referencia técnica del catálogo de indicadores oficiales verificados de la API REST de CEPALSTAT (Comisión Económica para América Latina y el Caribe), contrastados en vivo contra el endpoint `https://api-cepalstat.cepal.org/cepalstat/api/v1/indicator/{id}/data`.

---

## 1. Tabla de Indicadores Verificados

| Slug Canónico | ID CEPALSTAT | Nombre Oficial | Unidad | Frecuencia | Dimensiones Clave Resueltas | Países Verificados | Fecha de Verificación |
|---|:---:|---|---|:---:|---|:---:|:---:|
| `tasa_desempleo` | **127** | Tasa de desocupación por sexo | Tasa anual media (%) | Anual | Sexo (`144`: 146=Ambos sexos), Año (`29117`), País (`208`: 216=ARG, 224=CHL, 258=URY) | ARG, CHL, URY | Noviembre 2026 |
| `tasa_desempleo_trimestral` | **2182** | Tasa de desocupación trimestral | Porcentaje (%) | Trimestral | País (`208`), Trimestre (`26677`: T1, T2, T3, T4 $\rightarrow$ Q1–Q4), Año (`29117`) | ARG, CHL, URY | Noviembre 2026 |
| `participacion_laboral` | **2470** | Tasa de participación en la fuerza de trabajo, por sexo | Porcentaje (%) | Anual | Sexo (`144`: 146=Ambos sexos), Año (`29117`), País (`208`) | ARG, CHL, URY | Noviembre 2026 |
| `pib_per_capita` | **2205** | Producto interno bruto (PIB) total anual por habitante a precios corrientes en dólares | Dólares corrientes por habitante (US$) | Anual | País (`208`: 216=ARG, 224=CHL, 258=URY), Año (`29117`) | ARG, CHL, URY | Noviembre 2026 |
| `matricula_terciaria` | **99** | Tasa bruta de matrícula de nivel terciario, por sexo | Porcentaje (%) | Anual | Sexo (`144`: 146=Ambos sexos), Nivel (`1401`), Año (`29117`), País (`208`) | ARG, CHL, URY | Noviembre 2026 |

---

## 2. Aclaración de Códigos Descartados / No Válidos

| Código / ID Descartado | Motivo del Descarte | Significado Real en CEPALSTAT |
|---|---|---|
| `SL_TLF_UEM` | Código alfanumérico genérico no soportado (devuelve HTTP 404). | — |
| `NY_GDP_PCAP_CD` | Código alfanumérico del Banco Mundial, no existe en CEPALSTAT (HTTP 404). | — |
| `SE_ENR_TERT` | Código alfanumérico no reconocido por CEPALSTAT (HTTP 404). | — |
| `2222` | Identificador numérico que **no corresponde a desempleo**. | *Tasa de crecimiento del PIB total anual por habitante a precios constantes*. |
| `2221` | Identificador numérico que **no corresponde a participación laboral**. | *PIB anual por habitante por actividad económica a precios constantes en dólares*. |
| `2200` | ID inexistente o ambiguo descartado. | — |
| `2250` | ID inexistente o ambiguo descartado. | — |

---

## 3. Especificación del Esquema Real de Datos de CEPALSTAT

A diferencia de modelos hipotéticos, la API de CEPALSTAT retorna observaciones en `body.data` con el siguiente contrato verificado:

```json
{
  "value": "6.65",
  "source_id": 36,
  "notes_ids": "15084,15090,15092",
  "iso3": "ARG",
  "dim_208": 216,
  "dim_144": 146,
  "dim_29117": 29180
}
```

### Reglas de Normalización del Conector (`CepalstatConnector`):
1. **Valor (`value`):** Extraído directamente del campo `value`. Cadenas con `"-"`, `"..."`, valores `null` o vacíos se descartan limpiamente (Principio 4: Honestidad del dato).
2. **País:** Si `iso3` está presente en la observación, se normaliza directamente a ISO 3166-1 alpha-3. Si `iso3` es nulo, se busca el identificador en `dim_208` contra los miembros de la dimensión País (`País__ESTANDAR`) resolviendo el nombre (`"Argentina" -> ARG`, `"Uruguay" -> URY`, `"Chile" -> CHL`).
3. **Filtro de Desglose por Sexo:** Para indicadores agregados nacionales (como 127, 2470 y 99), se filtra la dimensión Sexo (`dim_144`) seleccionando el miembro `"Ambos sexos"` (ID `146`) para evitar triplicar registros por año con las series desagregadas de hombres y mujeres.
4. **Período y Trimestre:** Para indicadores trimestrales (como 2182), la dimensión Trimestre (`dim_26677`) mapea miembros `T1`, `T2`, `T3`, `T4` a `Q1`, `Q2`, `Q3`, `Q4`, construyendo el período normalizado `YYYY-QX`. Para indicadores anuales, se utiliza directamente el año de `dim_29117`.
5. **Fecha Real de Actualización:** Extraída desde `body.metadata.last_update` (ej. `"Dec 19 2025  1:14PM"` $\rightarrow$ `date(2025, 12, 19)`), garantizando trazabilidad institucional estricta (Principio 3).
