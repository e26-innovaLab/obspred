import { createContext } from 'react';
import type { Filtros, Fuente, TipoIndicador, SerieTemporal, Ranking } from '../types/kpi';

// Un snapshot es una "foto" del gráfico en el momento en que el usuario lo guardó,
// incluyendo los datos y los filtros activos en ese instante.
export type SnapshotContenido =
  | { tipo: 'serie'; datos: SerieTemporal[] }
  | { tipo: 'ranking'; datos: Ranking };

export interface Snapshot {
  /** Clave única para deduplicar (ej: "demanda", "ranking-sector"). */
  id: string;
  titulo: string;
  descripcion?: string;
  contenido: SnapshotContenido;
  fuentes: Array<{ fuente: Fuente; tipo: TipoIndicador }>;
  /** Copia de los filtros al momento de guardar. */
  filtros: Filtros;
  fechaGuardado: string;
}

export interface InformeContextValue {
  snapshots: Snapshot[];
  estaGuardado: (id: string) => boolean;
  guardar: (snap: Snapshot) => void;
  quitar: (id: string) => void;
  limpiar: () => void;
}

export const InformeContext = createContext<InformeContextValue | null>(null);
