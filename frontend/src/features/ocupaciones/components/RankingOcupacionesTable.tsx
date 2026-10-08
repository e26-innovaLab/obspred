import type { Pais } from '../../../types/kpi';
import { PAISES } from '../../../services/mock/catalogo';
import { SERIE_PAIS } from '../../../styles/paletaMarca';
import type { FilaOcupacion } from '../hooks/useOcupacionesData';

interface Props {
  filas: FilaOcupacion[];
  paises: Pais[];
  seleccionadaId?: string;
  onSeleccionar: (id: string) => void;
}

const nombrePais = (id: Pais) => PAISES.find((p) => p.id === id)?.nombre ?? id;

// Ranking de ocupaciones con dos columnas por país marcado (puestos e
// índice). En pantallas chicas la tabla se desplaza hacia el costado.
export function RankingOcupacionesTable({ filas, paises, seleccionadaId, onSeleccionar }: Props) {
  return (
    <div className="tabla-scroll">
      <table className="ranking-table ranking-table--paises">
        <thead>
          <tr>
            <th rowSpan={2} scope="col">
              Ocupación
            </th>
            {paises.map((p) => (
              <th key={p} colSpan={2} scope="colgroup" className="ranking-table__pais">
                <span className="filtros-comparacion__muestra" style={{ background: SERIE_PAIS[p].color }} aria-hidden />
                {nombrePais(p)}
              </th>
            ))}
          </tr>
          <tr>
            {paises.map((p) => [
              <th key={`${p}-puestos`} scope="col" className="ranking-table__num">
                Puestos
              </th>,
              <th key={`${p}-indice`} scope="col" className="ranking-table__num">
                Índice
              </th>,
            ])}
          </tr>
        </thead>
        <tbody>
          {filas.map((f) => (
            <tr
              key={f.ocupacionId}
              aria-selected={f.ocupacionId === seleccionadaId}
              tabIndex={0}
              onClick={() => onSeleccionar(f.ocupacionId)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  onSeleccionar(f.ocupacionId);
                }
              }}
            >
              <td>{f.nombre}</td>
              {paises.map((p) => {
                const d = f.porPais[p];
                return [
                  <td key={`${p}-puestos`} className="ranking-table__num">
                    {d ? d.puestos.toLocaleString('es-AR') : 'Sin dato'}
                  </td>,
                  <td key={`${p}-indice`} className="ranking-table__num">
                    {d ? d.indice : 'Sin dato'}
                  </td>,
                ];
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
