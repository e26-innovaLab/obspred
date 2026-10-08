import axios from 'axios';
import { env } from '../../config/env';
import type { Pais } from '../../types/kpi';

// Cliente HTTP único hacia la API interna (Backend).
// El contrato de endpoints se acuerda con Backend (principio 02 del roadmap).
export const apiClient = axios.create({
  baseURL: env.apiBaseUrl,
  timeout: 15000,
});

// Espejo del envoltorio estándar del Backend
// (backend/app/api/v1/schemas/response_schema.py → ApiResponse[T]).
export interface ApiResponse<T> {
  success: boolean;
  status_code: number;
  message: string;
  data: T | null;
  errors: Array<{ code: string; detail: string; field?: string | null }> | null;
  meta: { page?: number | null; per_page?: number | null; total?: number | null; extra?: Record<string, unknown> | null } | null;
  timestamp: string;
}

// El Backend usa ISO3 (ARG/URY/CHL); el front mantiene AR/UY/CL.
// La traducción vive solo acá.
export const PAIS_A_ISO3: Record<Pais, string> = { AR: 'ARG', UY: 'URY', CL: 'CHL' };
export const ISO3_A_PAIS: Record<string, Pais> = { ARG: 'AR', URY: 'UY', CHL: 'CL' };

/** GET que desenvuelve ApiResponse<T> y devuelve mensajes aptos para el usuario. */
export async function apiGet<T>(
  url: string,
  params: Record<string, string | number | undefined>,
  signal?: AbortSignal,
): Promise<T> {
  try {
    const { data } = await apiClient.get<ApiResponse<T>>(url, { params, signal });
    if (!data.success || data.data == null) throw new Error(data.message);
    return data.data;
  } catch (err) {
    if (axios.isAxiosError<ApiResponse<null>>(err) && !axios.isCancel(err)) {
      throw new Error(
        err.response?.data?.message ?? 'No pudimos conectar con el Observatorio. Probá de nuevo en unos segundos.',
        { cause: err },
      );
    }
    throw err;
  }
}
