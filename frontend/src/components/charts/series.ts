// Transformaciones puras: formato del contrato (una serie por país) →
// formato de Recharts (una fila por período). Sin React: testeables con Vitest.
import type { Pais, Proyeccion, SerieTemporal } from '../../types/kpi';

export type FilaSerie = { periodo: string } & Partial<Record<Pais, number | null>>;

/** [{pais:'AR', puntos}, {pais:'UY', puntos}] → [{periodo, AR: 6.1, UY: null}] */
export function pivotearPorPais(series: SerieTemporal[]): FilaSerie[] {
  const filas = new Map<string, FilaSerie>();
  for (const s of series) {
    for (const p of s.puntos) {
      const fila = filas.get(p.periodo) ?? { periodo: p.periodo };
      fila[s.pais] = p.valor;
      filas.set(p.periodo, fila);
    }
  }
  return [...filas.values()].sort((a, b) => a.periodo.localeCompare(b.periodo));
}

export const hayDatos = (series: SerieTemporal[]) => series.some((s) => s.puntos.some((p) => p.valor !== null));

export const MIN_PERIODOS_PROYECCION = 3;

export function puedeProyectar(p: Proyeccion): boolean {
  const observados = p.historico.filter((x) => x.valor !== null).length;
  return p.proyectable && observados >= MIN_PERIODOS_PROYECCION && p.proyeccion.length > 0;
}

export interface FilaProyeccion {
  periodo: string;
  observado?: number | null;
  proyectado?: number | null;
  banda?: [number, number];
}

/** Une histórico y proyección; el último observado abre la línea proyectada. */
export function filasProyeccion(p: Proyeccion): FilaProyeccion[] {
  const filas: FilaProyeccion[] = p.historico.map((h) => ({ periodo: h.periodo, observado: h.valor }));
  const ultimo = [...filas].reverse().find((f) => f.observado != null);
  if (ultimo && ultimo.observado != null && puedeProyectar(p)) {
    ultimo.proyectado = ultimo.observado;
    ultimo.banda = [ultimo.observado, ultimo.observado];
    for (const x of p.proyeccion) {
      filas.push({ periodo: x.periodo, proyectado: x.valor, banda: [x.limiteInferior, x.limiteSuperior] });
    }
  }
  return filas;
}

const NUM = new Intl.NumberFormat('es-AR', { maximumFractionDigits: 1 });

export function formatValor(valor: number | null | undefined, unidad = ''): string {
  if (valor == null) return 'Sin dato';
  if (unidad === '%') return `${NUM.format(valor)} %`;
  return unidad && unidad !== 'índice' ? `${NUM.format(valor)} ${unidad}` : NUM.format(valor);
}

/** 2025-Q3 → "T3 2025" */
export function formatPeriodo(periodo: string): string {
  const m = /^(\d{4})-Q([1-4])$/.exec(periodo);
  return m ? `T${m[2]} ${m[1]}` : periodo;
}
