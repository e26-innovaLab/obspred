import { useCallback, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import { env } from '../../../config/env';
import { useAsyncData } from '../../../hooks/useAsyncData';
import { hayDatos } from '../../../components/charts/series';
import * as api from '../../../services/api/indicadores';
import * as mockComparativa from '../../../services/mock/comparativa';
import * as mockTendencias from '../../../services/mock/tendencias';
import { INDICADORES, PAISES, SECTORES } from '../../../services/mock/catalogo';
import type { Pais, Sector } from '../../../types/kpi';

const servicio = env.useMocks ? { ...mockTendencias, ...mockComparativa } : api;

// Indicadores de las tarjetas comparativas (Figma: "Indicadores comparativos").
export const INDICADORES_COMPARATIVOS = ['tasa_desempleo', 'tasa_empleo', 'salario_real_indice'];

const PAISES_VALIDOS = PAISES.map((p) => p.id);
const SECTORES_VALIDOS = SECTORES.map((s) => s.id);

// Los filtros de esta vista viven en la URL (?paises=AR,CL&sector=…&indicador=…)
// para poder compartir una comparación por link. A diferencia del resto de
// las vistas, acá el país es múltiple.
export function useFiltrosComparacion() {
  const [params, setParams] = useSearchParams();

  const paises = useMemo<Pais[]>(() => {
    const crudo = params.get('paises');
    if (crudo === null) return PAISES_VALIDOS;
    return crudo.split(',').filter((p): p is Pais => PAISES_VALIDOS.includes(p as Pais));
  }, [params]);

  const sectorCrudo = params.get('sector');
  const sector = SECTORES_VALIDOS.includes(sectorCrudo as Sector) ? (sectorCrudo as Sector) : undefined;
  const indicadorCrudo = params.get('indicador');
  const indicador = INDICADORES.some((i) => i.id === indicadorCrudo) ? (indicadorCrudo as string) : 'tasa_desempleo';

  const actualizar = useCallback(
    (cambios: Record<string, string | undefined>) =>
      setParams(
        (prev) => {
          const next = new URLSearchParams(prev);
          for (const [k, v] of Object.entries(cambios)) {
            if (v === undefined) next.delete(k);
            else next.set(k, v);
          }
          return next;
        },
        { replace: true },
      ),
    [setParams],
  );

  const togglePais = (pais: Pais) => {
    const nuevos = paises.includes(pais) ? paises.filter((p) => p !== pais) : [...paises, pais];
    // Se respeta el orden del catálogo (AR, UY, CL) para que los colores no salten.
    actualizar({ paises: PAISES_VALIDOS.filter((p) => nuevos.includes(p)).join(',') });
  };

  return {
    paises,
    sector,
    indicador,
    togglePais,
    setSector: (s?: Sector) => actualizar({ sector: s }),
    setIndicador: (i: string) => actualizar({ indicador: i }),
  };
}

export function useComparacionData(paises: Pais[], sector: Sector | undefined, indicador: string) {
  const base = `${paises.join(',')}|${sector ?? ''}`;

  const comparativa = useAsyncData(
    `comp|${base}`,
    (signal) => servicio.getComparativa(INDICADORES_COMPARATIVOS, paises, sector, signal),
    (data) => data.every((i) => i.valores.every((v) => v.valor === null)),
  );

  const series = useAsyncData(
    `series|${base}|${indicador}`,
    (signal) => servicio.getSeries(indicador, { pais: paises[0], sector }, signal, paises),
    (s) => !hayDatos(s),
  );

  // El mapa de calor recorre todos los sectores, así que no depende del filtro de sector.
  const mapaCalor = useAsyncData(
    `calor|${paises.join(',')}|${indicador}`,
    (signal) => servicio.getMapaCalor(indicador, paises, signal),
    (m) => m.celdas.every((c) => c.valor === null),
  );

  return { comparativa, series, mapaCalor };
}
