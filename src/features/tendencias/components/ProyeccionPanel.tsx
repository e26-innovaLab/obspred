import type { ProyeccionPunto } from '../../../services/mock/tendencias';
import { SinDatos } from '../../../components/common/SinDatos';

export function ProyeccionPanel({ proyeccion }: { proyeccion: ProyeccionPunto[] | null }) {
  // Regla del proyecto: sin ≥3 períodos históricos comparables, no se
  // muestra proyección — nunca se estima sin base suficiente.
  if (!proyeccion) {
    return <SinDatos mensaje="No hay suficientes períodos históricos comparables para proyectar (se requieren al menos 3)." />;
  }

  return (
    <ul className="proyeccion-panel">
      {proyeccion.map((p) => (
        <li key={p.periodo}>
          <span>{p.periodo}</span>
          <strong>{p.valorProyectado}</strong>
        </li>
      ))}
      <li className="proyeccion-panel__nota">Proyección orientativa — no reemplaza el dato observado.</li>
    </ul>
  );
}
