import type { Filtros, Indicador } from '../../types/kpi';
import type { Alerta } from '../../types/alerta';
import { SECTORES } from './catalogo';
import { seededInt, seededRange } from './random';
import { fuenteMock } from './fuentes';

export interface IndicadorPrincipal {
  id: string;
  nombre: string;
  valor: number;
  unidad: string;
}

export function getIndicadoresPrincipales(filtros: Filtros): Indicador<number>[] {
  const seed = `${filtros.pais}-${filtros.sector ?? 'all'}-${filtros.periodo ?? 'last'}`;

  const base: Array<Pick<Indicador, 'id' | 'nombre' | 'unidad' | 'tipo'>> = [
    { id: 'desempleo', nombre: 'Tasa de desempleo', unidad: '%', tipo: 'observado' },
    { id: 'empleo-registrado', nombre: 'Empleo registrado', unidad: '%', tipo: 'observado' },
    { id: 'salario-promedio', nombre: 'Salario promedio (índice)', unidad: 'idx', tipo: 'calculado' },
  ];

  return base.map((b) => ({
    ...b,
    valor:
      b.id === 'salario-promedio'
        ? Math.round(seededRange(`${seed}-${b.id}`, 95, 130))
        : Number(seededRange(`${seed}-${b.id}`, 4, 14).toFixed(1)),
    fuente: fuenteMock(filtros.pais, `${seed}-${b.id}`),
    pais: filtros.pais,
    sector: filtros.sector,
    periodo: filtros.periodo ?? '2026-Q2',
  }));
}

export interface TendenciaSector {
  sector: string;
  sectorNombre: string;
  estado: 'crecimiento' | 'estabilidad' | 'caida';
}

export function getTendenciaPorSector(filtros: Filtros): TendenciaSector[] {
  const seed = `${filtros.pais}-${filtros.periodo ?? 'last'}`;
  const estados: TendenciaSector['estado'][] = ['crecimiento', 'estabilidad', 'caida'];

  return SECTORES.map((s) => {
    const roll = seededInt(`${seed}-${s.id}`, 0, 2);
    return { sector: s.id, sectorNombre: s.nombre, estado: estados[roll] };
  });
}

const ALERTAS_TITULO: Array<{ titulo: string; descripcion: string; nivel: Alerta['nivel'] }> = [
  {
    titulo: 'Variación significativa en empleo registrado',
    descripcion: 'El indicador se movió más de 2 puntos respecto al período anterior.',
    nivel: 'alto',
  },
  {
    titulo: 'Nueva brecha de habilidades detectada',
    descripcion: 'Se identificó una habilidad con alta demanda y baja cobertura formativa.',
    nivel: 'medio',
  },
  {
    titulo: 'Fuente desactualizada',
    descripcion: 'Una de las fuentes utilizadas no publica datos nuevos hace más de 60 días.',
    nivel: 'bajo',
  },
];

export function getAlertasActivas(filtros: Filtros): Alerta[] {
  const seed = `${filtros.pais}-${filtros.sector ?? 'all'}-alertas`;
  const cantidad = seededInt(seed, 1, 3);

  return ALERTAS_TITULO.slice(0, cantidad).map((a, i) => {
    const dias = seededInt(`${seed}-${i}`, 0, 10);
    const fecha = new Date();
    fecha.setDate(fecha.getDate() - dias);
    return {
      id: `alerta-${i}`,
      ...a,
      fecha: fecha.toISOString(),
      pais: filtros.pais,
      sector: filtros.sector,
    };
  });
}
