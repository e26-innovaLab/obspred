import { useCallback, useMemo, useState, type ReactNode } from 'react';
import { InformeContext, type InformeContextValue, type Snapshot } from './informeContextInstance';

// Provider global del informe personalizado.
// Guarda snapshots de gráficos que el usuario va seleccionando desde cualquier página.
export function InformeProvider({ children }: { children: ReactNode }) {
  const [snapshots, setSnapshots] = useState<Snapshot[]>([]);

  const estaGuardado = useCallback((id: string) => snapshots.some((s) => s.id === id), [snapshots]);

  const guardar = useCallback((snap: Snapshot) => {
    setSnapshots((prev) => {
      // Si ya existe ese id lo reemplaza (actualiza los datos con los filtros actuales).
      const sinEste = prev.filter((s) => s.id !== snap.id);
      return [...sinEste, snap];
    });
  }, []);

  const quitar = useCallback((id: string) => {
    setSnapshots((prev) => prev.filter((s) => s.id !== id));
  }, []);

  const limpiar = useCallback(() => setSnapshots([]), []);

  const value = useMemo<InformeContextValue>(
    () => ({ snapshots, estaGuardado, guardar, quitar, limpiar }),
    [snapshots, estaGuardado, guardar, quitar, limpiar],
  );

  return <InformeContext.Provider value={value}>{children}</InformeContext.Provider>;
}
