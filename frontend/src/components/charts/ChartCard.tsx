import type { ReactNode } from 'react';
import type { AsyncState } from '../../hooks/useAsyncData';
import type { Fuente, TipoIndicador } from '../../types/kpi';
import { FuenteBadge } from '../common/FuenteBadge';
import { SinDatos } from '../common/SinDatos';

interface Props<T> {
  titulo: string;
  descripcion?: string;
  estado: AsyncState<T>;
  onRetry?: () => void;
  /** Fuentes a mostrar al pie (principio 03). Se deduplican por nombre + tipo. */
  fuentes?: (data: T) => Array<{ fuente: Fuente; tipo: TipoIndicador }>;
  mensajeSinDatos?: string;
  altura?: number;
  acciones?: ReactNode; // ej. selector de indicador
  children: (data: T) => ReactNode;
}

// Envoltorio para cualquier gráfico: título, estados (cargando / error /
// sin datos / ok) y trazabilidad al pie. Compartido: lo usan Tendencias y
// Comparar países (AGENTS.md, principio 7).
export function ChartCard<T>({
  titulo,
  descripcion,
  estado,
  onRetry,
  fuentes,
  mensajeSinDatos,
  altura = 280,
  acciones,
  children,
}: Props<T>) {
  return (
    <article className="chart-card" aria-busy={estado.status === 'loading'}>
      <header className="chart-card__header">
        <div>
          <h3>{titulo}</h3>
          {descripcion && <p className="chart-card__descripcion">{descripcion}</p>}
        </div>
        {acciones}
      </header>

      <div className="chart-card__cuerpo" style={{ minHeight: altura }}>
        {estado.status === 'loading' && <ChartSkeleton altura={altura} />}
        {estado.status === 'error' && (
          <div className="chart-card__error" role="alert">
            <p>{estado.error}</p>
            {onRetry && (
              <button type="button" onClick={onRetry}>
                Reintentar
              </button>
            )}
          </div>
        )}
        {estado.status === 'empty' && <SinDatos mensaje={mensajeSinDatos} />}
        {estado.status === 'success' && children(estado.data)}
      </div>

      {estado.status === 'success' && fuentes && (
        <footer className="chart-card__fuentes">
          {unicas(fuentes(estado.data)).map((f) => (
            <FuenteBadge key={`${f.fuente.nombre}-${f.tipo}`} fuente={f.fuente} tipo={f.tipo} />
          ))}
        </footer>
      )}
    </article>
  );
}

function ChartSkeleton({ altura }: { altura: number }) {
  return (
    <div className="chart-skeleton" style={{ height: altura }} role="status">
      <span className="visually-hidden">Cargando gráfico…</span>
      {[62, 48, 75, 55, 82, 68, 90].map((h, i) => (
        <span key={i} className="chart-skeleton__barra" style={{ height: `${h}%` }} />
      ))}
    </div>
  );
}

function unicas(items: Array<{ fuente: Fuente; tipo: TipoIndicador }>) {
  const vistos = new Set<string>();
  return items.filter((f) => {
    const k = `${f.fuente.nombre}|${f.tipo}`;
    if (vistos.has(k)) return false;
    vistos.add(k);
    return true;
  });
}
