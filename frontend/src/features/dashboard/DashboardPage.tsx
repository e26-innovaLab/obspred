import { FiltrosBar } from '../../components/common/FiltrosBar';
import { KpiCard } from '../../components/common/KpiCard';
import { useDashboardData } from './hooks/useDashboardData';
import { TendenciaSectorList } from './components/TendenciaSectorList';
import { AlertasPanel } from './components/AlertasPanel';

// Vista 1 — Dashboard general.
// Indicadores principales, estado de tendencia por sector y alertas activas.
// Filtros activos: País · Sector · Período.
export function DashboardPage() {
  const { indicadores, tendenciasPorSector, alertas } = useDashboardData();

  return (
    <section className="page">
      <h2>Dashboard general</h2>
      <FiltrosBar mostrarSector mostrarPeriodo />

      <div className="kpi-grid">
        {indicadores.map((i) => (
          <KpiCard key={i.id} indicador={i} />
        ))}
      </div>

      <div className="page__columns">
        <div>
          <h3>Estado de tendencia por sector</h3>
          <TendenciaSectorList tendencias={tendenciasPorSector} />
        </div>
        <div>
          <h3>Alertas activas</h3>
          <AlertasPanel alertas={alertas} />
        </div>
      </div>
    </section>
  );
}
