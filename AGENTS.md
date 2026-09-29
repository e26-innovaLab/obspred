# Guía de Trabajo para Agentes (AGENTS.md)
# Observatorio Predictivo de Tendencias Socioeconómicas, Laborales y Educativas (`obspred`)

> **Propósito:** Esta guía define las directrices arquitectónicas, principios metodológicos, fuentes de datos, convenciones y flujo de trabajo para agentes de inteligencia artificial y desarrolladores que operan en este repositorio.

---

## 1. Identificación y Contexto del Proyecto

El **Observatorio Predictivo de Tendencias** (`obspred`) es una plataforma web desarrollada en el marco de **innova.lab (Grupo N° 5)** para el análisis, integración y visualización interactiva de indicadores socioeconómicos, laborales y educativos.

- **Alcance Geográfico:** Argentina, Uruguay y Chile.
- **Sectores Estratégicos:** 
  1. Tecnología
  2. Salud
  3. Energía
  4. Turismo
  5. Economía del Conocimiento
- **Ocupaciones:** ~20 ocupaciones clave priorizadas.
- **Audiencia / Usuarios Principales:** Gobiernos, organismos públicos, instituciones educativas, analistas de mercado laboral y equipos de formación y empleo.

---

## 2. Documentos de Referencia y Fuentes de la Verdad

Los archivos fuente originales en formatos `.pdf` y `.docx` constituyen la base de verdad del proyecto. Cada uno cuenta con su correspondiente documento Markdown (`.md`) para trazabilidad, edición y consulta en el repositorio:

| Documento Original | Documento Markdown | Descripción / Alcance |
|---|---|---|
| `Observatorio_predictivo.pdf` | [`Observatorio_predictivo.md`](Observatorio_predictivo.md) | Brief formal del producto, alcance del MVP, funcionalidades, conectores oficiales y plan de trabajo de 12 semanas (Sprints 0 a 6). |
| `roadmap_observatorio.docx` | [`ROADMAP.md`](ROADMAP.md) | Roadmap de trabajo v1.0, Sprint 0. Principios del equipo, catálogo de datos, matriz de KPIs, 5 pasos al MVP y gestión de riesgos. |
| `Semana_0_Observatorio_Predictivo_Benchmark_UX.pdf` | [`BENCHMARK_UX.md`](BENCHMARK_UX.md) | Benchmark de referentes (SABE Chile, OEDE Argentina, INE Uruguay, O*NET, Lightcast), arquitectura de información y 5 vistas del dashboard. |

> **Regla de integridad:** Cualquier cambio en la definición de KPIs, flujos o alcance debe contrastarse y mantenerse en estricta coherencia con estos documentos de referencia.

---

## 3. Los 10 Principios del Equipo (Sprint 0)

Todo agente o colaborador debe respetar rigurosamente estos principios:

1. **Prioridad del dato sobre la vista:** Los KPIs se confirman con el equipo de Data antes de que Frontend o UX construyan sobre ellos. No se diseñan vistas asumiendo datos que no existen.
2. **Contrato de API primero:** El contrato de la API interna (endpoints, modelos Pydantic/TypeScript, tipos y errores) se documenta antes de buildear, no después.
3. **Trazabilidad total:** Cada indicador visible en pantalla debe mostrar su **fuente, fecha de actualización y tipo** (observado / calculado / proyección) mediante componentes dedicados como `FuenteBadge`. Sin excepción.
4. **Honestidad de datos:** Si un dato no está disponible, se muestra explícitamente el estado *"Sin datos"* o *"Datos insuficientes"*. **Nunca** se inventa un valor ni se imputa sin metodología validada.
5. **Criterio riguroso de proyecciones:** Las proyecciones estadísticas requieren **al menos 3 períodos históricos comparables** para poder mostrarse al usuario.
6. **Lenguaje del usuario:** El lenguaje de la interfaz es el del usuario final y tomador de decisiones, no la jerga interna de base de datos o sistema.
7. **Regla de componentes compartidos:** Nada entra a carpetas compartidas (`shared/`, `components/common/`, `hooks/`, etc.) sin que al menos **dos features distintas** lo necesiten. Lo específico de una vista vive en su feature correspondiente.
8. **Enfoque invertido del pipeline:**
   $$\text{Dato disponible} \longrightarrow \text{KPI posible} \longrightarrow \text{Pregunta que responde} \longrightarrow \text{Filtro necesario} \longrightarrow \text{Vista adecuada}$$
9. **Jerarquía estricta de filtros:**
   El filtro de **País** es la raíz ineludible. Luego se encadenan:
   $$\text{País} \longrightarrow \text{Sector} \longrightarrow \text{Ocupación} \longrightarrow \text{Período}$$
10. **Modularidad y escalabilidad:** Conectores desacoplados por país para permitir la incorporación futura de nuevos territorios sin alterar el núcleo del sistema.

---

## 4. Arquitectura y Vistas Principales

El Observatorio se compone de cinco áreas funcionales fundamentales:

1. **Vista 1 — Dashboard General:**
   - Panorama macroeconómico y laboral por país y sector.
   - KPIs clave: Tasa de desempleo, empleo registrado, variación salarial real.
   - Tendencias sectoriales (crecimiento $\uparrow$, estabilidad $\rightarrow$, caída $\downarrow$).
   - Panel de alertas activas según variaciones significativas.
2. **Vista 2 — Ocupaciones e Índice de Empleabilidad:**
   - Ranking de ocupaciones por puestos demandados.
   - **Índice de Empleabilidad (score 0–100)** con visualización desglosada de sus dimensiones y ponderaciones.
   - Evolución y comparador entre países.
3. **Vista 3 — Tendencias y Evolución Histórica:**
   - Series temporales de empleo y salarios.
   - Proyecciones a 6 meses con intervalos de confianza (solo con serie suficiente).
   - Comparador temporal entre períodos seleccionados.
4. **Vista 4 — Brechas de Habilidades:**
   - Comparación de demanda laboral (extraída de avisos/bolsas de empleo) frente a oferta formativa (egresados/titulaciones).
   - Detección de habilidades emergentes y brechas formativas.
5. **Vista 5 — Trazabilidad y Fuentes:**
   - Auditoría y estado de frescura de las fuentes (activa, desactualizada, no disponible).
   - Metadatos de ingesta y documentación de la metodología del Índice de Empleabilidad.

---

## 5. Fuentes de Datos y Conectores

### Argentina
- **APIs:** Datos Argentina Series de Tiempo (`apis.datos.gob.ar/series/api/`).
- **Datasets:** INDEC — Encuesta Permanente de Hogares (EPH), Secretaría de Trabajo (empleo registrado y salarios), Secretaría de Educación (matrículas y titulaciones).

### Chile
- **APIs:** SIMEL — INE Chile (indicadores de trabajo decente), Banco Central de Chile (series económicas y empleo).
- **Datasets:** SENCE — Sistema de Análisis de Bolsas de Empleo (SABE), INE — Encuesta Nacional de Empleo (ENE), SIES / Mi Futuro (educación superior y titulaciones).

### Uruguay
- **APIs / Datasets:** INE Uruguay — Encuesta Continua de Hogares (ECH), ANEP — Observatorio de la Educación / DGETP-UTU, Catálogo Nacional de Datos Abiertos (`datos.gub.uy`).

### Fuentes Comparables Regionales
- **APIs:** CEPALSTAT (CEPAL), ILOSTAT (OIT / ILO), World Bank Open Data.

---

## 6. Organización del Repositorio y Ramas

### Estructura del Proyecto
```text
obspred/
├── backend/            # API REST (FastAPI/Python), arquitectura limpia, ingesta y persistencia
├── frontend/           # SPA React 19 + TypeScript + Vite + Recharts
├── data/               # Scripts de procesamiento, normalización y catálogo de datasets
├── docs/               # Especificaciones técnicas, metodología y contratos
├── AGENTS.md           # Reglas e instrucciones para agentes de desarrollo
├── ROADMAP.md          # Roadmap detallado, matriz de KPIs y entregables semanales
├── BENCHMARK_UX.md     # Benchmark UX/UI, análisis de referentes y flujos de usuario
├── Observatorio_predictivo.md # Brief del producto y requerimientos funcionales
└── README.md           # Descripción general del repositorio
```

### Estrategia de Ramas (Git Flow)
- `main`: Código estable y documentación consolidada.
- `develop`: Rama base de integración técnica (`backend`, `frontend`, `data`).
- `frontend` / `origin/frontend`: Desarrollo de interfaces, vistas y componentes visuales.
- Ramas de feature: `feature/<nombre>`, `fix/<nombre>`, `develop/<nombre>`.

---

## 7. Instrucciones Operativas para Agentes

1. **Verificación de Tipos y Linter:** Al generar o modificar código en TypeScript o Python, garantizar que cumpla con los linters configurados (ESLint / Ruff) y no contenga errores de tipado estricto.
2. **Uso de Mocks:** En ausencia de endpoints activos del backend, el frontend debe consumir la capa de servicios mock determinística (`services/mock/`), manteniendo la misma firma que la futura API.
3. **No romper enlaces de documentación:** Todos los enlaces relativos entre archivos Markdown (`Observatorio_predictivo.md`, `ROADMAP.md`, `BENCHMARK_UX.md`, `AGENTS.md`) deben mantenerse funcionales.
4. **Respeto a la identidad institucional:** Para el frontend, seguir la paleta definida en el manual institucional (`#1D3343`, `#035C80`, `#FFCD02`, `#FCFCFC`) y la tipografía `Archivo`.
5. **Control de Git y Push Remoto:** Los agentes **NUNCA** deben ejecutar `git push`. Las subidas y sincronizaciones hacia los repositorios remotos están a cargo exclusivo de los usuarios y desarrolladores del equipo.
6. **Diseño Clean Architecture & SOLID en Backend:** Separación explícita de capas (`domain`, `application`, `infrastructure`, `api`, `core`), inversión de dependencias mediante interfaces/protocolos y cobertura de pruebas unitarias.
7. **Documentación con Docstrings:** Todo módulo, clase, método y función en Python debe contar con docstrings descriptivos en formato Google/NumPy/Sphinx que documenten propósito, parámetros y retorno.
