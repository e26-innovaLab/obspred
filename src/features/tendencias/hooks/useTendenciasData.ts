import { useMemo } from 'react';
import { useFiltros } from '../../../store/useFiltros';
import { getSerieHistorica, getProyeccion } from '../../../services/mock/tendencias';

export function useTendenciasData() {
  const { filtros } = useFiltros();

  const serie = useMemo(() => getSerieHistorica(filtros), [filtros]);
  const proyeccion = useMemo(() => getProyeccion(filtros, serie), [filtros, serie]);

  return { serie, proyeccion };
}
