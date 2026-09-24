import { useMemo } from 'react';
import { useFiltros } from '../../../store/useFiltros';
import { getIndicadoresPrincipales, getTendenciaPorSector, getAlertasActivas } from '../../../services/mock/dashboard';

// Hoy consume el mock; el día que exista la API interna, este hook cambia
// de implementación (a fetch/react-query) sin tocar los componentes de la vista.
export function useDashboardData() {
  const { filtros } = useFiltros();

  return useMemo(
    () => ({
      indicadores: getIndicadoresPrincipales(filtros),
      tendenciasPorSector: getTendenciaPorSector(filtros),
      alertas: getAlertasActivas(filtros),
    }),
    [filtros],
  );
}
