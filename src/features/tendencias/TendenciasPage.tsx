import { FiltrosBar } from '../../components/common/FiltrosBar';
import { useTendenciasData } from './hooks/useTendenciasData';
import { SerieHistoricaChart } from './components/SerieHistoricaChart';
import { ProyeccionPanel } from './components/ProyeccionPanel';

// Vista 3 — Tendencias.
// Evolución histórica de empleo, salarios y actividad sectorial, con
// proyección a futuro cuando hay serie suficiente. Filtros activos:
// País · Sector · Ocupación · Período.
export function TendenciasPage() {
  const { serie, proyeccion } = useTendenciasData();

  return (
    <section className="page">
      <h2>Tendencias</h2>
      <FiltrosBar mostrarSector mostrarOcupacion mostrarPeriodo={false} />

      <h3>Evolución histórica</h3>
      <SerieHistoricaChart serie={serie} />

      <h3>Proyección</h3>
      <ProyeccionPanel proyeccion={proyeccion} />
    </section>
  );
}
