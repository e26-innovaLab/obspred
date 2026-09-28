# obspred
# Observatorio Predictivo de Tendencias (obspred)

Plataforma web de análisis y visualización de datos socioeconómicos, laborales y educativos orientada a identificar tendencias del mercado de trabajo, estimar la evolución de la empleabilidad y detectar brechas entre formación y demanda laboral en Argentina, Uruguay y Chile.

---

## 🎯 Alcance del MVP

- **Cobertura geográfica:** Argentina, Uruguay y Chile.
- **Sectores estratégicos:** Tecnología, Salud, Energía, Turismo y Economía del conocimiento.
- **Ocupaciones:** ~20 ocupaciones clave priorizadas.
- **Flujo de datos:** Fuentes oficiales / Carga manual -> Normalización -> Procesamiento -> Indicadores -> Visualización.

---

## 📂 Estructura del Repositorio

```text
obspred/
├── backend/            # API REST, servicios de ingesta y persistencia
├── frontend/           # Interfaz web, dashboards, visualizaciones y filtros
├── data/               # Scripts de análisis, normalización y plantillas de datasets
├── docs/               # Especificaciones técnicas, metodología y contratos de API
├── docker-compose.yml  # Configuración para entorno local y base de datos
├── .gitignore          # Exclusiones de Git
└── README.md           # Documentación principal del proyecto