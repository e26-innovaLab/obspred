import { useMemo, useState, type ReactNode } from 'react';
import type { Filtros } from '../types/kpi';
import { PERIODOS } from '../services/mock/catalogo';
import { FiltrosContext, type FiltrosContextValue } from './filtrosContextInstance';

const FILTROS_INICIALES: Filtros = {
  pais: 'AR',
  sector: undefined,
  ocupacionId: undefined,
  periodo: PERIODOS[PERIODOS.length - 1].id,
};

// Contexto global de filtros. País → Sector → Ocupación se encadenan
// (jerarquía de filtros del roadmap): cambiar el país o el sector limpia
// la ocupación seleccionada si deja de ser válida.
export function FiltrosProvider({ children }: { children: ReactNode }) {
  const [filtros, setFiltros] = useState<Filtros>(FILTROS_INICIALES);

  const value = useMemo<FiltrosContextValue>(
    () => ({
      filtros,
      setPais: (pais) => setFiltros((f) => ({ ...f, pais, ocupacionId: undefined })),
      setSector: (sector) => setFiltros((f) => ({ ...f, sector, ocupacionId: undefined })),
      setOcupacionId: (ocupacionId) => setFiltros((f) => ({ ...f, ocupacionId })),
      setPeriodo: (periodo) => setFiltros((f) => ({ ...f, periodo })),
    }),
    [filtros],
  );

  return <FiltrosContext.Provider value={value}>{children}</FiltrosContext.Provider>;
}
