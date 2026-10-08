import type { Filtros, Pais, Proyeccion, PuntoSerie, SerieTemporal } from '../../types/kpi';
import { seededRange } from './random';
import { indicadorPorId } from './catalogo';
import { fuenteMock } from './fuentes';

// Mock determinístico con la MISMA firma y forma que services/api/indicadores.ts
// (AGENTS.md, regla 2): cuando Backend publique /metricas/*, solo cambia
// VITE_USE_MOCKS. Casos de borde a propósito, para ver los estados de UI:
//  - Uruguay tiene huecos (valor: null) → la línea se corta, no se interpola.
//  - Uruguay + ocupación → sin datos (sus fuentes no desagregan por ocupación).

const LATENCIA_MS = 450;
const ULTIMO_PERIODO = '2026-Q2';
const PERIODOS_HISTORICOS = 12;

const BASE: Record<string, { min: number; max: number; pendiente: number }> = {
  puestos_demandados: { min: 1200, max: 4200, pendiente: 45 },
  tasa_desempleo: { min: 5, max: 11, pendiente: -0.08 },
  tasa_empleo: { min: 42, max: 57, pendiente: 0.1 },
  salario_real_indice: { min: 88, max: 108, pendiente: 0.4 },
  empleo_registrado: { min: 1400, max: 6200, pendiente: 12 },
};

function esperar(signal?: AbortSignal): Promise<void> {
  return new Promise((resolve, reject) => {
    const t = setTimeout(resolve, LATENCIA_MS);
    signal?.addEventListener('abort', () => {
      clearTimeout(t);
      reject(new DOMException('Cancelado', 'AbortError'));
    });
  });
}

const aNumero = (p: string) => Number(p.slice(0, 4)) * 4 + Number(p.slice(-1)) - 1;
const aPeriodo = (n: number) => `${Math.floor(n / 4)}-Q${(n % 4) + 1}`;

function puntos(indicador: string, pais: Pais, filtros: Filtros): PuntoSerie[] {
  const cfg = BASE[indicador] ?? BASE.tasa_empleo;
  const seed = `${indicador}-${pais}-${filtros.sector ?? 'all'}-${filtros.ocupacionId ?? 'all'}`;
  const base = seededRange(seed, cfg.min, cfg.max);
  const fin = aNumero(ULTIMO_PERIODO);

  return Array.from({ length: PERIODOS_HISTORICOS }, (_, i) => {
    const n = fin - PERIODOS_HISTORICOS + 1 + i;
    const periodo = aPeriodo(n);
    const sinDato = pais === 'UY' && (!!filtros.ocupacionId || n % 5 === 2);
    if (sinDato) return { periodo, valor: null, tipo: 'observado' as const };
    const ruido = seededRange(`${seed}-${periodo}`, -0.04, 0.04) * base;
    const valor = base + cfg.pendiente * (n - fin) * (base / cfg.max) + ruido;
    return { periodo, valor: Math.round(valor * 10) / 10, tipo: 'observado' as const };
  });
}

function serie(indicador: string, pais: Pais, filtros: Filtros): SerieTemporal {
  const meta = indicadorPorId(indicador);
  return {
    pais,
    indicador,
    nombre: meta?.nombre ?? indicador,
    unidad: meta?.unidad ?? '',
    frecuencia: 'trimestral',
    puntos: puntos(indicador, pais, filtros),
    fuentes: [{ fuente: fuenteMock(pais, `${indicador}-${pais}`), tipo: 'observado' }],
  };
}

export async function getSeries(
  indicador: string,
  filtros: Filtros,
  signal?: AbortSignal,
  paises: Pais[] = [filtros.pais],
): Promise<SerieTemporal[]> {
  await esperar(signal);
  return paises.map((p) => serie(indicador, p, filtros));
}

// Regresión lineal sobre los puntos observados; banda ±1,28·σ·√h (≈ 80 %).
// Principio 05: sin ≥ 3 períodos comparables, no se proyecta.
export async function getProyeccion(
  indicador: string,
  filtros: Filtros,
  signal?: AbortSignal,
  horizonte = 2,
): Promise<Proyeccion> {
  await esperar(signal);
  const s = serie(indicador, filtros.pais, filtros);
  const obs = s.puntos.flatMap((p, x) => (p.valor === null ? [] : [{ x, y: p.valor }]));
  const base = {
    pais: s.pais,
    indicador,
    unidad: s.unidad,
    historico: s.puntos,
    metodo: 'Regresión lineal sobre la serie trimestral observada',
    nivelConfianza: 0.8,
    fuentes: [...s.fuentes, { ...s.fuentes[0], tipo: 'proyeccion' as const }],
  };

  if (obs.length < 3) {
    return {
      ...base,
      proyeccion: [],
      proyectable: false,
      motivoNoProyectable: `Hay ${obs.length} período(s) con datos y se necesitan al menos 3 comparables.`,
    };
  }

  const n = obs.length;
  const mx = obs.reduce((a, p) => a + p.x, 0) / n;
  const my = obs.reduce((a, p) => a + p.y, 0) / n;
  const pend = obs.reduce((a, p) => a + (p.x - mx) * (p.y - my), 0) / obs.reduce((a, p) => a + (p.x - mx) ** 2, 0);
  const orden = my - pend * mx;
  const sigma = Math.sqrt(obs.reduce((a, p) => a + (p.y - orden - pend * p.x) ** 2, 0) / Math.max(n - 2, 1));
  const r = (v: number) => Math.round(v * 10) / 10;

  return {
    ...base,
    proyectable: true,
    proyeccion: Array.from({ length: horizonte }, (_, k) => {
      const h = k + 1;
      const valor = orden + pend * (s.puntos.length - 1 + h);
      const margen = 1.28 * sigma * Math.sqrt(h);
      return {
        periodo: aPeriodo(aNumero(ULTIMO_PERIODO) + h),
        valor: r(valor),
        limiteInferior: r(valor - margen),
        limiteSuperior: r(valor + margen),
      };
    }),
  };
}
