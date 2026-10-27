import type { DimensionRanking, Filtros, Indicador, KpiResumen, Ranking, Tendencia as TendenciaKpi } from '../../types/kpi';
import type { Alerta } from '../../types/alerta';
import { SECTORES, indicadorPorId, ocupacionesPorSector } from './catalogo';
import { getSeries } from './tendencias';
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

// ---- Gráficos del Inicio (asíncronos, misma firma que services/api) ----

const SENTIDO_POSITIVO: Record<string, 'sube' | 'baja'> = { tasa_desempleo: 'baja' };
const UMBRAL_ESTABILIDAD = 2; // ±2 % = estabilidad (a confirmar con Data)

const tendenciaDe = (v: number | null): TendenciaKpi | null =>
  v === null ? null : v > UMBRAL_ESTABILIDAD ? 'crecimiento' : v < -UMBRAL_ESTABILIDAD ? 'caida' : 'estabilidad';

/** Tarjetas de KPI: último valor, variación contra el período anterior y mini serie. */
export async function getKpis(indicadores: string[], filtros: Filtros, signal?: AbortSignal): Promise<KpiResumen[]> {
  return Promise.all(
    indicadores.map(async (indicador) => {
      const [s] = await getSeries(indicador, filtros, signal);
      const conDato = s.puntos.filter((p) => p.valor !== null);
      const ultimo = conDato.at(-1);
      const anterior = conDato.at(-2);
      const variacionPct =
        ultimo?.valor != null && anterior?.valor != null && anterior.valor !== 0
          ? Math.round(((ultimo.valor - anterior.valor) / Math.abs(anterior.valor)) * 1000) / 10
          : null;
      return {
        indicador,
        nombre: s.nombre,
        unidad: s.unidad,
        periodo: ultimo?.periodo ?? null,
        valor: ultimo?.valor ?? null,
        valorAnterior: anterior?.valor ?? null,
        variacionPct,
        tendencia: tendenciaDe(variacionPct),
        sentidoPositivo: SENTIDO_POSITIVO[indicador] ?? 'sube',
        sparkline: s.puntos.slice(-8).map((p) => p.valor),
        fuente: s.fuentes[0],
      };
    }),
  );
}

const HABILIDADES = [
  'Análisis de datos',
  'Programación (Python / JS)',
  'Atención al cliente',
  'Gestión de proyectos',
  'Inglés técnico',
  'Ciberseguridad',
  'Energías renovables',
];

function esperar(signal?: AbortSignal): Promise<void> {
  return new Promise((resolve, reject) => {
    const t = setTimeout(resolve, 450);
    signal?.addEventListener('abort', () => {
      clearTimeout(t);
      reject(new DOMException('Cancelado', 'AbortError'));
    });
  });
}

/**
 * Rankings del Inicio. Habilidades solo tiene fuente oficial en Chile
 * (SENCE — SABE): para AR y UY devuelve items vacíos → "Sin datos".
 */
export async function getRanking(
  dimension: DimensionRanking,
  indicador: string,
  filtros: Filtros,
  signal?: AbortSignal,
  limite = 5,
): Promise<Ranking> {
  await esperar(signal);
  const candidatos: Array<{ id: string; nombre: string }> =
    dimension === 'sector'
      ? SECTORES
      : dimension === 'ocupacion'
        ? ocupacionesPorSector(filtros.sector)
        : filtros.pais === 'CL'
          ? HABILIDADES.map((h) => ({ id: h.toLowerCase().replace(/\W+/g, '-'), nombre: h }))
          : [];

  const items = candidatos
    .map((c) => {
      const seed = `ranking-${dimension}-${indicador}-${filtros.pais}-${c.id}`;
      const variacionPct = Math.round(seededRange(`${seed}-var`, -12, 18) * 10) / 10;
      return {
        id: c.id,
        nombre: c.nombre,
        valor: Math.round(seededRange(seed, 150, 3800)),
        variacionPct,
        tendencia: tendenciaDe(variacionPct),
      };
    })
    .sort((a, b) => b.valor - a.valor)
    .slice(0, limite);

  return {
    dimension,
    indicador,
    unidad: indicadorPorId(indicador)?.unidad ?? '',
    periodo: '2026-Q2',
    items,
    fuentes: [
      {
        fuente: dimension === 'habilidad' ? { ...fuenteMock('CL', seedFuente(dimension)), nombre: 'SENCE — SABE' } : fuenteMock(filtros.pais, seedFuente(dimension)),
        tipo: 'observado',
      },
    ],
  };
}

const seedFuente = (dimension: string) => `ranking-fuente-${dimension}`;
