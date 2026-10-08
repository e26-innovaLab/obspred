import type { OcupacionRanking } from '../../../services/mock/ocupaciones';

interface Props {
  ranking: OcupacionRanking[];
  seleccionadaId?: string;
  onSeleccionar: (id: string) => void;
}

export function RankingOcupacionesTable({ ranking, seleccionadaId, onSeleccionar }: Props) {
  return (
    <table className="ranking-table">
      <thead>
        <tr>
          <th>Ocupación</th>
          <th>Puestos disponibles</th>
          <th>Índice de Empleabilidad</th>
        </tr>
      </thead>
      <tbody>
        {ranking.map((r) => (
          <tr
            key={r.ocupacionId}
            aria-selected={r.ocupacionId === seleccionadaId}
            onClick={() => onSeleccionar(r.ocupacionId)}
          >
            <td>{r.nombre}</td>
            <td>{r.puestosDisponibles.toLocaleString('es-AR')}</td>
            <td>{r.indiceEmpleabilidad}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
