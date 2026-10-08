// Configuración centralizada de variables de entorno del frontend.
// Definir estas variables en un archivo .env (ver .env.example).

export const env = {
  // El Backend monta sus rutas bajo /api/v1 (backend/app/core/constants.py).
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1',
  // true → los servicios de gráficos usan services/mock (misma firma que la API).
  useMocks: (import.meta.env.VITE_USE_MOCKS ?? 'true') === 'true',
} as const;
