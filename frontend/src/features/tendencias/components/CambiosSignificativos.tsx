import type { CambioSignificativo } from '../../../types/kpi';
import { formatPeriodo } from '../../../components/charts/series';

// Lista de los cambios marcados en el gráfico con "!". Une las alertas del
// brief ("detección de cambios significativos") con la serie que las explica.
export function CambiosSignificativos({ cambios }: { cambios: CambioSignificativo[] }) {
  if (cambios.length === 0) {
    return <p className="cambios-significativos__vacio">Sin cambios significativos en el período mostrado.</p>;
  }

  return (
    <div className="cambios-significativos">
      <h4>
        <span className="cambios-significativos__icono" aria-hidden>
          !
        </span>
        Cambios significativos
      </h4>
      <ul className="alertas-panel">
        {cambios.map((c) => (
          <li key={c.id} data-nivel={c.nivel}>
            <div className="alertas-panel__titulo">{c.titulo}</div>
            <p>{c.descripcion}</p>
            <time>{formatPeriodo(c.periodo)}</time>
          </li>
        ))}
      </ul>
    </div>
  );
}
