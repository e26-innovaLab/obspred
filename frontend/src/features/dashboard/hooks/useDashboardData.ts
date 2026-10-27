import { useMemo } from 'react';
import { useFiltros } from '../../../store/useFiltros';
import { env } from '../../../config/env';
import { useAsyncData } from '../../../hooks/useAsyncData';
import { hayDatos } from '../../../components/charts/series';
import * as api from '../../../services/api/indicadores';
import * as mockDashboard from '../../../services/mock/dashboard';
import * as mockTendencias from '../../../services/mock/tendencias';
import { getIndicadoresPrincipales, getTendenciaPorSector, getAlertasActivas } from '../../../services/mock/dashboard';
import type { DimensionRanking } from '../../../types/kpi';

const servicio = env.useMocks ? { ...mockTendencias, ...mockDashboard } : api;

// Figma Inicio: 4 tarjetas de "Indicadores principales".
export const KPIS_INICIO = ['tasa_desempleo', 'tasa_empleo', 'salario_real_indice', 'puestos_demandados'];
const INDICADOR_DEMANDA = 'puestos_demandados';

// Datos síncronos del mock original (los sigue usando DetailPage).
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

// Gráficos del Inicio: asíncronos, con estados de carga / error / sin datos.
export function useDashboardGraficos() {
  const { filtros } = useFiltros();
  const base = `${filtros.pais}|${filtros.sector ?? ''}|${filtros.periodo ?? ''}`;

  const kpis = useAsyncData(
    `kpis|${base}`,
    (signal) => servicio.getKpis(KPIS_INICIO, filtros, signal),
    (k) => k.every((x) => x.valor === null),
  );

  const demanda = useAsyncData(
    `demanda|${base}`,
    (signal) => servicio.getSeries(INDICADOR_DEMANDA, filtros, signal),
    (s) => !hayDatos(s),
  );

  const sinItems = (r: { items: unknown[] }) => r.items.length === 0;
  const fetchRanking = (dimension: DimensionRanking) => (signal: AbortSignal) =>
    servicio.getRanking(dimension, INDICADOR_DEMANDA, filtros, signal);

  const sectores = useAsyncData(`ranking|sector|${base}`, fetchRanking('sector'), sinItems);
  const ocupaciones = useAsyncData(`ranking|ocupacion|${base}`, fetchRanking('ocupacion'), sinItems);
  const habilidades = useAsyncData(`ranking|habilidad|${base}`, fetchRanking('habilidad'), sinItems);

  return {
    kpis,
    demanda,
    sectores,
    ocupaciones,
    habilidades,
  };
}
