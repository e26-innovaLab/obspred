import { useContext } from 'react';
import { InformeContext, type InformeContextValue } from './informeContextInstance';

export function useInforme(): InformeContextValue {
  const ctx = useContext(InformeContext);
  if (!ctx) throw new Error('useInforme debe usarse dentro de <InformeProvider>');
  return ctx;
}
