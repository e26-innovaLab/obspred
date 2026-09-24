import { useContext } from 'react';
import { FiltrosContext, type FiltrosContextValue } from './filtrosContextInstance';

export function useFiltros(): FiltrosContextValue {
  const ctx = useContext(FiltrosContext);
  if (!ctx) throw new Error('useFiltros debe usarse dentro de <FiltrosProvider>');
  return ctx;
}
