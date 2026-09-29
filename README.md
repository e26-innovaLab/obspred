# Observatorio Predictivo de Tendencias Socioeconómicas, Laborales y Educativas (`obspred`)

Plataforma analítica e interactiva para la integración, visualización y proyección de indicadores socioeconómicos, laborales y educativos de **Argentina, Uruguay y Chile**, desarrollada en el marco de **innova.lab (Grupo N° 5)**.

---

## 🏛️ Estructura del Proyecto

El repositorio se organiza con separación de responsabilidades:

```text
obspred/
├── backend/            # API REST (FastAPI/Python), Clean Architecture y persistencia
├── frontend/           # SPA React 19 + TypeScript + Vite + Recharts
├── data/               # Scripts de procesamiento, normalización y catálogo de datasets
├── docs/               # Especificaciones técnicas, metodología y contratos
├── AGENTS.md           # Reglas e instrucciones para agentes de desarrollo
├── ROADMAP.md          # Roadmap detallado, matriz de KPIs y entregables semanales
├── BENCHMARK_UX.md     # Benchmark UX/UI, análisis de referentes y flujos de usuario
├── Observatorio_predictivo.md # Brief del producto y requerimientos funcionales
└── README.md           # Descripción general del repositorio
```

---

## ⚙️ Backend y Arquitectura

El backend está desarrollado con **FastAPI** y **Python 3.12+**, implementando **Clean Architecture** (Arquitectura Limpia) y principios **SOLID**:

```text
backend/app/
├── core/               # Configuración, constantes (sin magic strings) y logging
├── domain/             # Reglas de negocio puras, entidades, excepciones e interfaces
├── application/        # Orquestación de casos de uso (use cases) y DTOs
├── infrastructure/     # Conectores externos, base de datos y repositorios
└── api/                # Capa de presentación HTTP / Controllers (FastAPI)
    ├── dependencies.py # Inyección de dependencias
    └── v1/
        ├── router.py   # Enrutador central v1 (agrega todos los controladores)
        ├── endpoints/  # Controladores HTTP / Endpoints (health, indicadores, ocupaciones, etc.)
        └── schemas/    # Esquemas Pydantic de entrada/salida (DTOs de request/response)
```

### ¿Dónde se ubican los Controllers?
En FastAPI con Clean Architecture, los controladores corresponden a los **Endpoints / Routers** HTTP:
* **Directorio de Controllers:** [`backend/app/api/v1/endpoints/`](backend/app/api/v1/endpoints/)
* **Enrutador Central:** [`backend/app/api/v1/router.py`](backend/app/api/v1/router.py)
* **Punto de entrada:** [`backend/app/main.py`](backend/app/main.py)
* **Lógica delegada:** Los controladores delegan la ejecución a los casos de uso en [`backend/app/application/use_cases/`](backend/app/application/use_cases/).

Para más detalles sobre la ejecución local y pruebas del backend, consulta el [`README.md` del Backend](backend/README.md).

---

## 📚 Documentación de Referencia

* [`Observatorio_predictivo.md`](Observatorio_predictivo.md): Brief formal del producto, alcance del MVP y plan de 12 semanas.
* [`ROADMAP.md`](ROADMAP.md): Principios del equipo, catálogo de datos, matriz de KPIs y gestión de riesgos.
* [`BENCHMARK_UX.md`](BENCHMARK_UX.md): Referentes del mercado (SABE, OEDE, INE, O*NET, Lightcast) y arquitectura de vistas.
* [`AGENTS.md`](AGENTS.md): Guía de trabajo, reglas arquitectónicas e instrucciones operativas para agentes y desarrolladores.
