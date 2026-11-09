import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';

export interface GraficoSnapshot {
  id: string;
  titulo: string;
  descripcion?: string;
  seccion: string;
  timestamp: number;
  paises?: string[];
  datos?: unknown;
}

interface InformeContextValue {
  graficos: GraficoSnapshot[];
  agregar: (g: Omit<GraficoSnapshot, 'id' | 'timestamp'>) => void;
  quitar: (id: string) => void;
  limpiar: () => void;
}

const InformeContext = createContext<InformeContextValue | null>(null);

export function InformeProvider({ children }: { children: ReactNode }) {
  const [graficos, setGraficos] = useState<GraficoSnapshot[]>([]);

  const agregar = useCallback((g: Omit<GraficoSnapshot, 'id' | 'timestamp'>) => {
    setGraficos((prev) => [
      ...prev,
      { ...g, id: `${Date.now()}-${Math.random().toString(36).slice(2)}`, timestamp: Date.now() },
    ]);
  }, []);

  const quitar = useCallback((id: string) => {
    setGraficos((prev) => prev.filter((g) => g.id !== id));
  }, []);

  const limpiar = useCallback(() => setGraficos([]), []);

  return (
    <InformeContext.Provider value={{ graficos, agregar, quitar, limpiar }}>
      {children}
    </InformeContext.Provider>
  );
}

export function useInforme() {
  const ctx = useContext(InformeContext);
  if (!ctx) throw new Error('useInforme debe usarse dentro de InformeProvider');
  return ctx;
}
