import { apiClient } from './client';
import type { Filtros, Indicador } from '../../types/kpi';

// Servicio de acceso a indicadores. Los endpoints reales se completan
// cuando el contrato de API interna quede documentado (ver roadmap, paso 4).
export async function getIndicadores(filtros: Filtros): Promise<Indicador[]> {
  const { data } = await apiClient.get<Indicador[]>('/indicadores', {
    params: filtros,
  });
  return data;
}
