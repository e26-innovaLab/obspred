# Observatorio Predictivo de Tendencias Socioeconómicas, Laborales y Educativas

## 1. Resumen Ejecutivo (Orientado a Gestión y Políticas Públicas)

En un contexto de constante transformación económica, productiva y tecnológica, la toma de decisiones estratégicas en materia de formación y empleo se ve obstaculizada por la fragmentación y dispersión de la información oficial entre múltiples organismos e indicadores no estandarizados.

El **Observatorio Predictivo de Tendencias Socioeconómicas, Laborales y Educativas** es una plataforma web analítica concebida para centralizar, normalizar y traducir grandes volúmenes de datos públicos en indicadores accionables y comparables. En su fase inicial (MVP), el sistema abarca **Argentina, Uruguay y Chile**, focalizándose en **5 sectores estratégicos** (Tecnología, Salud, Energía, Turismo y Economía del Conocimiento) y una selección de **20 ocupaciones clave**.

A través de un circuito integral de ingesta automatizada (APIs oficiales) y carga estructurada de datasets validados, la plataforma proporciona:
1. Un **Índice de Empleabilidad** multidimensional y transparente por ocupación (0–100).
2. Análisis de **tendencias y series históricas** para anticipar trayectorias del mercado de trabajo.
3. Detección temprana de **brechas de habilidades** y capacidades emergentes frente a la oferta formativa vigente.
4. Un sistema de **alertas inteligentes** ante fluctuaciones anómalas en el mercado.
5. **Trazabilidad estricta y metadatos de frescura** sobre el origen oficial, vigencia y tipología metodológica de cada dato.

La experiencia de usuario se articula en **5 vistas funcionales** (*Dashboard General*, *Ocupaciones*, *Tendencias*, *Brechas de Habilidades* y *Trazabilidad de Fuentes*) sustentadas por un pipeline riguroso de 5 etapas (*Ingesta*, *Normalización*, *Cálculo*, *API Interna* y *Visualización*). Siguiendo el principio rector de partir exclusivamente del dato oficial confirmado, se garantiza que ningún indicador sea proyectado sin un mínimo de $\ge$ 3 períodos históricos comparables ni existan valores imputados o arbitrarios.

La solución dota a gobiernos, organismos públicos e instituciones académicas de una herramienta orientativa basada en evidencia para diseñar políticas públicas y programas formativos alineados con las demandas reales del mercado laboral regional.

---

## 2. Resumen Técnico y Metodológico (Orientado a Arquitectura y Datos)

Este proyecto aborda la heterogeneidad y fragmentación de fuentes estadísticas regionales mediante el diseño e implementación de un observatorio web de analítica predictiva de empleo y educación. El sistema implementa una arquitectura desacoplada y escalable (FastAPI en Python 3.11+, PostgreSQL/Supabase y Next.js/TypeScript) orientada a la ingesta continua de APIs oficiales (ILOSTAT, CEPALSTAT, World Bank, Datos Argentina, SIMEL Chile) combinada con módulos de validación y carga programada de datasets estructurados (INDEC EPH, INE Uruguay ECH, SABE SENCE, SIES, ANEP).

El núcleo analítico ejecuta algoritmos de normalización y armonización semántica entre taxonomías ocupacionales y formativas de Argentina, Uruguay y Chile. Sobre esta base común, la solución formula un **Índice de Empleabilidad** ponderado y auditable, modelos de detección tendencial y un motor de contraste oferta-demanda para cuantificar desajustes de cualificación y habilidades emergentes. Un pilar no negociable del diseño es la estricta trazabilidad metodológica, distinguiendo explícitamente en contratos de datos e interfaces entre datos primarios *observados*, indicadores sintéticos *calculados* y proyecciones estadísticas *proyectadas*, asegurando máxima reproducibilidad y rigor metodológico para la toma de decisiones.

---

## 3. Executive Abstract (English Version)

Amid rapid economic, technological, and productive shifts, evidence-based decision-making in vocational training and employment policies is frequently hindered by fragmented and siloed public statistical data.

The **Predictive Observatory of Socioeconomic, Labor, and Educational Trends** is an interactive web analytics platform developed to ingest, standardize, and transform dispersed public records into actionable and comparable labor market intelligence. Covered initially across **Argentina, Uruguay, and Chile**, the MVP targets **5 strategic sectors** (Technology, Healthcare, Energy, Tourism, and the Knowledge Economy) across approximately **20 key occupations**.

Leveraging automated connections to official APIs (such as ILOSTAT, CEPALSTAT, World Bank, Datos Argentina, and SIMEL Chile) alongside validated tabular data uploads, the platform delivers a multidimensional **Employability Index**, historical time-series analytics, automated trend alerts, and skill mismatch detection between educational supply and market demand. With complete data lineage and strict methodology traceability, the platform empowers governments, public agencies, and educational institutions to proactively address labor disruptions and optimize human capital development.

---

## 4. Palabras Clave / Keywords

- **Español:** Mercado laboral, Observatorio predictivo, Índice de empleabilidad, Brechas de habilidades, Normalización de datos, Trazabilidad metodológica, Políticas públicas, Argentina, Uruguay, Chile.
- **English:** Labor market intelligence, Predictive observatory, Employability index, Skills mismatch, Data harmonization, Methodology traceability, Public policy, Latin America.

---

## 5. Estructura del Equipo e Institución (Equipo 26 - Innova Lab)

### Instructora / Mentora
- **Instructora:** María del Valle Bustos
- **Área:** Gerencia Operativa de Innovación Tecnológica y Talento Digital
- **Institución:** Agencia de Habilidades para el Futuro — Ministerio de Educación, Buenos Aires Ciudad
- **Sede:** Carlos H. Perette 750 - Barrio 31, Piso 5, C.A.B.A., Argentina

### Nómina del Equipo 26

| Rol | Nombre y Apellido | Correo Electrónico |
|:---|:---|:---|
| **Frontend** | Melvin Gabriela Farias Ramirez | `melvingabriela17@gmail.com` |
| **Frontend** | Ludmila Ruiz Diaz | `ludmila.b.ruizdiaz@gmail.com` |
| **Frontend** | Germán Pablo Gonzalez | `germancai@hotmail.com` |
| **Backend** | Nicolás Snider | `nicolas.snider@gmail.com` |
| **Backend** | Colby Vertilus | `vertiluscolby@gmail.com` |
| **Backend** | Enzo Figlioli | `enzofiglioli.p@gmail.com` |
| **Diseño UX/UI** | Selena Romei | `selenaromeicm@gmail.com` |
| **Diseño UX/UI** | Lucas Rossi Caula | `lucas1rc2003@gmail.com` |
| **Diseño UX/UI** | Guillermo Damián Pérez Maidana | `guilleperezmaida@gmail.com` |
| **Data Analytics** | Matias Vrecic | `m_vrecic@hotmail.com` |
| **Data Analytics** | Ximena Facal | `xime.facal@live.com.ar` |
| **Data Analytics** | Ignacio Lopez Parra | `lopezparraignacio@gmail.com` |
| **Testing / QA** | Christian Facundo Aldavez | `christian.aldavez90@gmail.com` |
| **Testing / QA** | Eduardo Arevalo | `eduardo.arevalo072@gmail.com` |
| **Testing / QA** | Alejandro Medina Jurado | `medinaale93@gmail.com` |

### Dinámica y Encuentros del Equipo
- **Día y horario regular:** Martes de 18:30 a 20:30 h.
- **Modalidad habitual:** Virtual vía Google Meet ([meet.google.com/bcf-jmos-ydi](https://meet.google.com/bcf-jmos-ydi)).
- **Primer encuentro (Presencial):** Martes 8 de septiembre, 18:30 a 20:30 h.
  - **Sede:** Centro de Simulación — 25 de Mayo 444, Microcentro, CABA.
  - **Formulario de asistencia:** [Registro de asistencia](https://forms.gle/Wm6Wog2vxTTtDhJh8).
- **Pauta de confidencialidad:** Toda la información compartida en el marco del proyecto, documentación técnica y datos de contacto es de uso exclusivo del equipo en Innova Lab.

---

## 6. Documentación del Proyecto y Entregables

- 🗺️ **[ROADMAP.md](ROADMAP.md)**: Roadmap de trabajo oficial v1.0, matriz completa de KPIs, filtros jerárquicos, catálogo de 14 fuentes y cronograma de 12 semanas (Sprints 0 a 6).
- 📄 **[roadmap_observatorio.docx](roadmap_observatorio.docx)**: Documento base original de trabajo del equipo.
- 📋 **[Observatorio_predictivo.md](Observatorio_predictivo.md)**: Especificación integral del producto digital, problemática y plan detallado de tareas por rol.
- 🏛️ **[docs/architecture.md](docs/architecture.md)**: Clean Architecture, Thin Controllers, servicios desacoplados y persistencia aislada.
- 🌐 **[docs/api_sources.md](docs/api_sources.md)**: Guía técnica de consumo de APIs oficiales (Datos AR, Banco Mundial, ILOSTAT, CEPALSTAT).
- 🤖 **[AGENTS.md](AGENTS.md)**: Reglas metodológicas para desarrolladores y agentes de IA (convenciones GitFlow y prohibición de magic strings).