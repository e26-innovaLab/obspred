import { createContext } from 'react';
import type { Filtros } from '../types/kpi';

export interface FiltrosContextValue {
  filtros: Filtros;
  setPais: (pais: Filtros['pais']) => void;
  setSector: (sector: Filtros['sector']) => void;
  setOcupacionId: (id: Filtros['ocupacionId']) => void;
  setPeriodo: (periodo: Filtros['periodo']) => void;
}

export const FiltrosContext = createContext<FiltrosContextValue | null>(null);
