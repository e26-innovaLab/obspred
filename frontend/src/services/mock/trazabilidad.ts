import type { Filtros } from '../../types/kpi';
import type { Fuente } from '../../types/kpi';
import { fuenteMock } from './fuentes';

export interface FuenteTrazable extends Fuente {
  id: string;
  indicadoresQueAlimenta: string[];
  metodologia?: string;
}

const INDICADORES_POR_FUENTE = [
  ['Tasa de desempleo', 'Empleo registrado'],
  ['Índice de Empleabilidad'],
  ['Salarios', 'Actividad sectorial'],
];

export function getFuentesTrazables(filtros: Filtros): FuenteTrazable[] {
  const seed = `${filtros.pais}-trazabilidad`;

  return INDICADORES_POR_FUENTE.map((indicadores, i) => {
    const fuente = fuenteMock(filtros.pais, `${seed}-${i}`);
    return {
      ...fuente,
      id: `fuente-${i}`,
      indicadoresQueAlimenta: indicadores,
      metodologia: i === 1 ? 'Índice de Empleabilidad — metodología v1 (ponderación por dimensión)' : undefined,
    };
  });
}
