import { useFiltros } from '../../../store/useFiltros';
import { useAsyncData } from '../../../hooks/useAsyncData';
import { env } from '../../../config/env';
import * as api from '../../../services/api/indicadores';
import * as mock from '../../../services/mock/tendencias';
import { hayDatos } from '../../../components/charts/series';

// Mock o API real según VITE_USE_MOCKS; ambos tienen la misma firma.
const servicio = env.useMocks ? mock : api;

export function useTendenciasData(indicador: string) {
  const { filtros } = useFiltros();
  const key = `${indicador}|${filtros.pais}|${filtros.sector ?? ''}|${filtros.ocupacionId ?? ''}`;

  const serie = useAsyncData(
    `serie|${key}`,
    (signal) => servicio.getSeries(indicador, filtros, signal),
    (s) => !hayDatos(s),
  );

  // "Sin proyección" no es un error: lo resuelve ProyeccionPanel con su motivo.
  const proyeccion = useAsyncData(`proy|${key}`, (signal) => servicio.getProyeccion(indicador, filtros, signal));

  return { serie, proyeccion };
}
