import type { FuenteTrazable } from '../../../services/mock/trazabilidad';

const ESTADO_LABEL: Record<FuenteTrazable['estado'], string> = {
  activa: 'Activa',
  desactualizada: 'Desactualizada',
  'no-disponible': 'No disponible',
};

export function FuentesTable({ fuentes }: { fuentes: FuenteTrazable[] }) {
  return (
    <table className="fuentes-table">
      <thead>
        <tr>
          <th>Fuente</th>
          <th>Indicadores que alimenta</th>
          <th>Última actualización</th>
          <th>Estado</th>
        </tr>
      </thead>
      <tbody>
        {fuentes.map((f) => (
          <tr key={f.id}>
            <td>
              {f.nombre}
              {f.metodologia && <div className="fuentes-table__metodologia">{f.metodologia}</div>}
            </td>
            <td>{f.indicadoresQueAlimenta.join(', ')}</td>
            <td>{new Date(f.fechaActualizacion).toLocaleDateString('es-AR')}</td>
            <td data-estado={f.estado}>{ESTADO_LABEL[f.estado]}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
