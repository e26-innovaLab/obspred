import { FiltrosBar } from '../../components/common/FiltrosBar';
import { useOcupacionesData } from './hooks/useOcupacionesData';
import { RankingOcupacionesTable } from './components/RankingOcupacionesTable';
import { IndiceEmpleabilidadChart } from './components/IndiceEmpleabilidadChart';
import { EvolucionIndiceChart } from './components/EvolucionIndiceChart';

// Vista 2 — Ocupaciones.
// Ranking de ocupaciones, Índice de Empleabilidad por ocupación con sus
// dimensiones y evolución histórica. Filtros activos: País · Sector ·
// Ocupación · Período.
export function OcupacionesPage() {
  const { ranking, seleccionadaId, setSeleccionadaId, dimensiones, evolucion } = useOcupacionesData();
  const seleccionada = ranking.find((r) => r.ocupacionId === seleccionadaId);

  return (
    <section className="page">
      <h2>Ocupaciones</h2>
      <FiltrosBar mostrarSector mostrarPeriodo />

      <RankingOcupacionesTable ranking={ranking} seleccionadaId={seleccionadaId} onSeleccionar={setSeleccionadaId} />

      {seleccionada && (
        <div className="page__columns">
          <div>
            <h3>Dimensiones del índice — {seleccionada.nombre}</h3>
            <IndiceEmpleabilidadChart dimensiones={dimensiones} />
          </div>
          <div>
            <h3>Evolución histórica del índice</h3>
            <EvolucionIndiceChart evolucion={evolucion} />
          </div>
        </div>
      )}
    </section>
  );
}
