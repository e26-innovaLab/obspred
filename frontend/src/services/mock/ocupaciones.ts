import type { Filtros } from '../../types/kpi';
import { ocupacionesPorSector } from './catalogo';
import { seededInt, seededRange } from './random';
import { fuenteMock } from './fuentes';
import type { Fuente } from '../../types/kpi';

export interface OcupacionRanking {
  ocupacionId: string;
  nombre: string;
  puestosDisponibles: number;
  indiceEmpleabilidad: number; // 0-100
  fuente: Fuente;
}

export interface DimensionIndice {
  nombre: string;
  valor: number; // 0-100
}

// El Índice de Empleabilidad se calcula a partir de estas dimensiones
// (metodología documentada en el roadmap del proyecto, Sprint 0).
const DIMENSIONES_INDICE = ['Demanda de puestos', 'Estabilidad salarial', 'Cobertura formativa', 'Crecimiento reciente'];

export function getRankingOcupaciones(filtros: Filtros): OcupacionRanking[] {
  const seed = `${filtros.pais}-${filtros.sector ?? 'all'}-${filtros.periodo ?? 'last'}`;
  const ocupaciones = ocupacionesPorSector(filtros.sector);

  return ocupaciones
    .map((o) => ({
      ocupacionId: o.id,
      nombre: o.nombre,
      puestosDisponibles: seededInt(`${seed}-${o.id}-puestos`, 40, 2400),
      indiceEmpleabilidad: Math.round(seededRange(`${seed}-${o.id}-idx`, 30, 95)),
      fuente: fuenteMock(filtros.pais, `${seed}-${o.id}`),
    }))
    .sort((a, b) => b.puestosDisponibles - a.puestosDisponibles);
}

export function getDimensionesIndice(filtros: Filtros, ocupacionId: string): DimensionIndice[] {
  const seed = `${filtros.pais}-${ocupacionId}-dim`;
  return DIMENSIONES_INDICE.map((nombre) => ({
    nombre,
    valor: Math.round(seededRange(`${seed}-${nombre}`, 30, 95)),
  }));
}

export interface EvolucionIndicePunto {
  periodo: string;
  indice: number;
}

export function getEvolucionIndice(filtros: Filtros, ocupacionId: string, periodos: string[]): EvolucionIndicePunto[] {
  const seed = `${filtros.pais}-${ocupacionId}-evolucion`;
  return periodos.map((periodo) => ({
    periodo,
    indice: Math.round(seededRange(`${seed}-${periodo}`, 35, 92)),
  }));
}
