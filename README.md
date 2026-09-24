# Observatorio Predictivo — Frontend

Frontend (React + TypeScript + Vite) del **Observatorio predictivo de tendencias
socioeconómicas, laborales y educativas** (Argentina, Uruguay y Chile) —
proyecto de innova.lab, Grupo N° 5.

## Estado actual

Las 5 vistas del Observatorio están implementadas y funcionando con **datos
mock** (`src/services/mock/`), generados de forma determinística por
filtro para simular la futura API sin necesitar el backend todavía. Cuando
el contrato de la API interna esté definido (roadmap, paso 4), los hooks de
cada feature (`features/*/hooks/`) se actualizan para consumir
`services/api/` en lugar de `services/mock/` — los componentes no cambian.

## Stack

- React 19 + TypeScript
- Vite (con code-splitting por ruta vía `React.lazy`)
- React Router (navegación entre vistas)
- Axios (consumo de la futura API interna)
- Recharts (visualizaciones)
- Context API (filtros globales compartidos)

## Estructura de carpetas

```
src/
├── app.tsx / router.tsx      # bootstrap y ruteo de la app
├── components/
│   ├── layout/                # header, navegación, layout general
│   ├── common/                # componentes compartidos (FuenteBadge, etc.)
│   └── charts/                # wrappers de gráficos reutilizables
├── features/                  # una carpeta por vista del Observatorio
│   ├── dashboard/              # Vista 1 — Dashboard general
│   ├── ocupaciones/            # Vista 2 — Ocupaciones e Índice de Empleabilidad
│   ├── tendencias/             # Vista 3 — Evolución histórica y proyecciones
│   ├── brechas/                 # Vista 4 — Brechas de habilidades
│   └── trazabilidad/            # Vista 5 — Trazabilidad y fuentes
│       └── (components/ hooks/ types/ dentro de cada feature)
├── services/
│   ├── api/                      # cliente HTTP y llamadas a la futura API interna
│   └── mock/                     # datos simulados (reemplazan a api/ hasta que el backend exista)
├── hooks/                       # hooks compartidos entre features
├── types/                        # tipos compartidos (Indicador, Filtros, Fuente...)
├── store/                         # filtros globales (Context API)
├── config/                         # configuración y variables de entorno
└── styles/                          # estilos globales adicionales
```

**Regla del equipo (principio 07 del roadmap):** nada entra a una carpeta
compartida (`components/common`, `hooks`, `types`, `services`) sin que al
menos dos features lo necesiten. Todo lo específico de una vista vive dentro
de su carpeta en `features/`.

## Principios que sigue el frontend

Según el roadmap del proyecto (Sprint 0):

1. El lenguaje de la interfaz es el lenguaje del usuario, no el del sistema.
2. Cada indicador en pantalla muestra su **fuente, fecha y tipo**
   (observado / calculado / proyección) — ver `FuenteBadge`.
3. Si un dato no está disponible, se muestra "sin datos" — nunca un número
   inventado.
4. Las proyecciones solo se muestran con ≥ 3 períodos históricos comparables.
5. Los filtros se encadenan: País → Sector → Ocupación → Período.

## Cómo correr el proyecto

```bash
npm install
cp .env.example .env   # completar VITE_API_BASE_URL cuando el backend esté disponible
npm run dev
```

## Scripts

- `npm run dev` — entorno de desarrollo
- `npm run build` — build de producción
- `npm run lint` — linter
- `npm run preview` — previsualizar el build
