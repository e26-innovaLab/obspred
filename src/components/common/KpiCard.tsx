import type { Indicador } from '../../types/kpi';
import { FuenteBadge } from './FuenteBadge';

export function KpiCard({ indicador }: { indicador: Indicador<number> }) {
  return (
    <article className="kpi-card">
      <h3>{indicador.nombre}</h3>
      <p className="kpi-card__valor">
        {indicador.valor}
        <span className="kpi-card__unidad">{indicador.unidad}</span>
      </p>
      <FuenteBadge fuente={indicador.fuente} tipo={indicador.tipo} />
    </article>
  );
}
