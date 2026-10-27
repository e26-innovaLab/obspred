import type { ComparativaIndicador, MapaCalor, Pais, Sector } from '../../types/kpi';
import { SECTORES, indicadorPorId } from './catalogo';
import { fuenteMock } from './fuentes';
import { getSeries } from './tendencias';
import { seededRange } from './random';

// Mock con la misma firma que services/api/indicadores.ts (AGENTS.md, regla 2).
// Casos de borde: Uruguay sin dato en Energía (la ECH no lo desagrega) y,
// en la comparativa, el último período de cada país puede ser distinto.

const LATENCIA_MS = 450;
const PERIODO = '2026-Q2';

function esperar(signal?: AbortSignal): Promise<void> {
  return new Promise((resolve, reject) => {
    const t = setTimeout(resolve, LATENCIA_MS);
    signal?.addEventListener('abort', () => {
      clearTimeout(t);
      reject(new DOMException('Cancelado', 'AbortError'));
    });
  });
}

const RANGO: Record<string, [number, number]> = {
  puestos_demandados: [200, 3800],
  tasa_desempleo: [3, 14],
  tasa_empleo: [38, 62],
  salario_real_indice: [82, 118],
  empleo_registrado: [80, 1600],
};

export async function getComparativa(
  indicadores: string[],
  paises: Pais[],
  sector: Sector | undefined,
  signal?: AbortSignal,
): Promise<ComparativaIndicador[]> {
  // Reutiliza las series del mock de tendencias: el valor comparado es el
  // último período con dato de cada país (no se inventa el que falta).
  const resultado = await Promise.all(
    indicadores.map(async (indicador) => {
      const series = await getSeries(indicador, { pais: paises[0] ?? 'AR', sector }, signal, paises);
      const meta = indicadorPorId(indicador);
      return {
        indicador,
        nombre: meta?.nombre ?? indicador,
        unidad: meta?.unidad ?? '',
        valores: series.map((s) => {
          const ultimo = [...s.puntos].reverse().find((p) => p.valor !== null);
          return {
            pais: s.pais,
            valor: ultimo?.valor ?? null,
            periodo: ultimo?.periodo ?? null,
            fuente: ultimo ? s.fuentes[0] : null,
          };
        }),
      };
    }),
  );
  return resultado;
}

export async function getMapaCalor(indicador: string, paises: Pais[], signal?: AbortSignal): Promise<MapaCalor> {
  await esperar(signal);
  const meta = indicadorPorId(indicador);
  const [min, max] = RANGO[indicador] ?? [0, 100];

  return {
    indicador,
    nombre: meta?.nombre ?? indicador,
    unidad: meta?.unidad ?? '',
    periodo: PERIODO,
    sectores: SECTORES,
    paises,
    celdas: SECTORES.flatMap((s) =>
      paises.map((pais) => {
        const seed = `calor-${indicador}-${pais}-${s.id}`;
        if (pais === 'UY' && s.id === 'energia') {
          return { sector: s.id, pais, valor: null, variacionPct: null };
        }
        return {
          sector: s.id,
          pais,
          valor: Math.round(seededRange(seed, min, max) * 10) / 10,
          variacionPct: Math.round(seededRange(`${seed}-var`, -12, 15) * 10) / 10,
        };
      }),
    ),
    fuentes: paises.map((p) => ({ fuente: fuenteMock(p, `calor-${indicador}-${p}`), tipo: 'observado' as const })),
  };
}
