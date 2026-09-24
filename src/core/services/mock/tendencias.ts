import type { Filtros } from '../../types/kpi';
import { seededRange } from './random';
import { PERIODOS } from './catalogo';

export interface SerieHistorica {
  periodo: string;
  empleo: number;
  salario: number;
  actividadSectorial: number;
}

// Serie histórica: al menos 3 períodos comparables habilita la proyección
// (principio 05 del roadmap: "Las proyecciones necesitan ≥ 3 períodos
// históricos comparables para mostrarse").
export function getSerieHistorica(filtros: Filtros): SerieHistorica[] {
  const seed = `${filtros.pais}-${filtros.sector ?? 'all'}-${filtros.ocupacionId ?? 'all'}`;

  return PERIODOS.map((p, i) => ({
    periodo: p.id,
    empleo: Math.round(seededRange(`${seed}-empleo-${p.id}`, 60 + i * 2, 75 + i * 2)),
    salario: Math.round(seededRange(`${seed}-salario-${p.id}`, 95 + i * 3, 115 + i * 3)),
    actividadSectorial: Math.round(seededRange(`${seed}-actividad-${p.id}`, 50 + i, 90 + i)),
  }));
}

export interface ProyeccionPunto {
  periodo: string;
  valorProyectado: number;
}

export function getProyeccion(filtros: Filtros, serie: SerieHistorica[]): ProyeccionPunto[] | null {
  // Regla: sin al menos 3 períodos históricos, no se genera proyección.
  if (serie.length < 3) return null;

  const seed = `${filtros.pais}-${filtros.sector ?? 'all'}-proyeccion`;
  const ultimoValor = serie[serie.length - 1].empleo;

  return Array.from({ length: 2 }).map((_, i) => ({
    periodo: `Proy. +${i + 1}`,
    valorProyectado: Math.round(ultimoValor + seededRange(`${seed}-${i}`, -3, 6)),
  }));
}
