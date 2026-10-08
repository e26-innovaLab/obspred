import type { Alerta } from '../../../types/alerta';
import { SinDatos } from '../../../components/common/SinDatos';

export function AlertasPanel({ alertas }: { alertas: Alerta[] }) {
  if (alertas.length === 0) return <SinDatos mensaje="No hay alertas activas para este país y sector." />;

  return (
    <ul className="alertas-panel">
      {alertas.map((a) => (
        <li key={a.id} data-nivel={a.nivel}>
          <div className="alertas-panel__titulo">{a.titulo}</div>
          <p>{a.descripcion}</p>
          <time dateTime={a.fecha}>{new Date(a.fecha).toLocaleDateString('es-AR')}</time>
        </li>
      ))}
    </ul>
  );
}
