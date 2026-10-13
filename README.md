# Observatorio Predictivo de Tendencias Socioeconómicas, Laborales y Educativas (`obspred`)

Plataforma analítica e interactiva para la integración, normalización, visualización y proyección de indicadores socioeconómicos, laborales y educativos de **Argentina, Uruguay y Chile**, desarrollada en el marco de **innova.lab (Grupo N° 5)**.

---

## 🎯 Alcance del MVP

- **Cobertura geográfica:** Argentina, Uruguay y Chile.
- **Sectores estratégicos:** Tecnología, Salud, Energía, Turismo y Economía del conocimiento.
- **Ocupaciones:** ~20 ocupaciones clave priorizadas.
- **Flujo de datos:** Fuentes oficiales / Carga manual $\rightarrow$ Normalización $\rightarrow$ Cálculo de KPIs $\rightarrow$ API interna $\rightarrow$ Visualización con trazabilidad.

---

## 📂 Estructura del Repositorio

El repositorio se organiza con clara separación de responsabilidades:

```text
obspred/
├── backend/            # API REST (FastAPI/Python), Clean Architecture y persistencia
├── frontend/           # SPA React 19 + TypeScript + Vite + Recharts
├── data/               # Scripts de procesamiento, normalización y catálogo de datasets
├── docs/               # Especificaciones técnicas, metodología y contratos de API
├── docker-compose.yml  # Configuración para entorno local y base de datos
├── AGENTS.md           # Reglas e instrucciones para agentes de desarrollo
├── ROADMAP.md          # Roadmap detallado, matriz de KPIs y entregables semanales
├── BENCHMARK_UX.md     # Benchmark UX/UI, análisis de referentes y flujos de usuario
├── Observatorio_predictivo.md # Brief del producto y requerimientos funcionales
├── .gitignore          # Exclusiones de Git
└── README.md           # Descripción general del repositorio
```

---

## 🚀 Entorno de Desarrollo (Monorepo)

Para ejecutar el Frontend y Backend simultáneamente en modo desarrollo con un solo comando:

### Prerrequisitos
1. **Node.js** (v18+) instalado.
2. **Python** (3.11+) con entorno virtual configurado en la raíz (`.venv/`) o en `backend/` con sus dependencias instaladas (`pip install -r backend/requirements.txt`).
3. Dependencias del frontend instaladas (`cd frontend && npm install`).

### Puesta en marcha en un solo comando
Estando en la raíz del repositorio (`obspred/`):

```bash
# 1. Instalar dependencias del root (solo la primera vez)
npm install

# 2. Levantar Backend y Frontend concurrentemente:
npm run dev
```

Esto ejecutará:
- **Backend (FastAPI):** `http://localhost:8000` (docs en `/docs`) con recarga automática (*hot reload*).
- **Frontend (Vite):** `http://localhost:5173` con HMR activo.

*Alternativa con script de Python (sin depender de `npm` en la raíz):*
```bash
python scripts/dev.py
```

---

## 🧩 Componentes del Sistema
 
 El proyecto se divide en tres componentes principales:
 
- **Backend ([`backend/`](backend/)):** API REST desarrollada con **FastAPI** (Python 3.11+), implementando **Clean Architecture** (Arquitectura Limpia) y principios **SOLID**, persistencia asíncrona (PostgreSQL / SQLite vía SQLAlchemy) y suite de pruebas unitarias. Para consultar la estructura detallada de capas, ubicación de controladores, contratos de respuesta y puesta en marcha local, consulta el [**README del Backend**](backend/README.md).
- **Frontend ([`frontend/`](frontend/)):** Aplicación SPA desarrollada en **React 19**, **TypeScript**, **Vite** y visualización con **Recharts**, diseñada siguiendo la guía de estilos institucionales y benchmark UX.
- **Datos y Modelos ([`data/`](data/)):** Catálogo de fuentes públicas, scripts de procesamiento, armonización semántica de taxonomías y cálculo de indicadores (Índice de Empleabilidad).

---

## 📚 Documentación de Referencia

* [`Observatorio_predictivo.md`](Observatorio_predictivo.md): Brief formal del producto, alcance del MVP y plan de 12 semanas.
* [`ROADMAP.md`](ROADMAP.md): Principios del equipo, catálogo de datos, matriz de KPIs y gestión de riesgos.
* [`BENCHMARK_UX.md`](BENCHMARK_UX.md): Referentes del mercado (SABE, OEDE, INE, O*NET, Lightcast) y arquitectura de vistas.
* [`AGENTS.md`](AGENTS.md): Guía de trabajo, reglas arquitectónicas e instrucciones operativas para agentes y desarrolladores.
