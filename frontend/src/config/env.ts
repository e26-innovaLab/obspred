// Configuración centralizada de variables de entorno del frontend.
// Definir estas variables en un archivo .env (ver .env.example).

export const env = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api',
} as const;
