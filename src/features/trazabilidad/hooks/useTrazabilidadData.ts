import { useMemo } from 'react';
import { useFiltros } from '../../../store/useFiltros';
import { getFuentesTrazables } from '../../../services/mock/trazabilidad';

export function useTrazabilidadData() {
  const { filtros } = useFiltros();
  const fuentes = useMemo(() => getFuentesTrazables(filtros), [filtros]);
  return { fuentes };
}
