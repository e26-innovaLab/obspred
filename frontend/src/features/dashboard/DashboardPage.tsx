import { FiltrosBar } from '../../components/common/FiltrosBar';
import { KpiCard } from '../../components/common/KpiCard';
import { SinDatos } from '../../components/common/SinDatos';
import { ChartCard } from '../../components/charts/ChartCard';
import { SerieHistoricaChart } from '../../components/charts/SerieHistoricaChart';
import { useFiltros } from '../../store/useFiltros';
import { useDashboardData, useDashboardGraficos, KPIS_INICIO } from './hooks/useDashboardData';
import { TendenciaSectorList } from './components/TendenciaSectorList';
import { AlertasPanel } from './components/AlertasPanel';
import { RankingList } from './components/RankingList';

// Vista 1 — Dashboard general (Figma: "Inicio").
// Indicadores principales con variación, evolución de la demanda, rankings,
// estado de tendencia por sector y alertas activas.
// Filtros activos: País · Sector · Período.
export function DashboardPage() {
  const { filtros } = useFiltros();
  const { tendenciasPorSector, alertas } = useDashboardData();
  const g = useDashboardGraficos();

  return (
    <section className="page">
      <h2>Panorama general</h2>
      <p className="page__descripcion">Vista general de los principales indicadores del observatorio.</p>
      <FiltrosBar mostrarSector mostrarPeriodo />

      <h3 className="page__seccion">Indicadores principales</h3>
      {g.kpis.state.status === 'loading' && (
        <div className="kpi-grid" role="status" aria-label="Cargando indicadores">
          {KPIS_INICIO.map((id) => (
            <div key={id} className="kpi-card kpi-card--skeleton" />
          ))}
        </div>
      )}
      {g.kpis.state.status === 'error' && (
        <div className="chart-card__error" role="alert">
          <p>{g.kpis.state.error}</p>
          <button type="button" onClick={g.kpis.retry}>
            Reintentar
          </button>
        </div>
      )}
      {g.kpis.state.status === 'empty' && <SinDatos />}
      {g.kpis.state.status === 'success' && (
        <div className="kpi-grid">
          {g.kpis.state.data.map((k) => (
            <KpiCard
              key={k.indicador}
              indicador={{
                id: k.indicador,
                nombre: k.nombre,
                valor: k.valor,
                unidad: k.unidad,
                tipo: k.fuente.tipo,
                fuente: k.fuente.fuente,
                pais: filtros.pais,
                sector: filtros.sector,
                periodo: k.periodo ?? '',
              }}
              variacionPct={k.variacionPct}
              sentidoPositivo={k.sentidoPositivo}
              sparkline={k.sparkline}
            />
          ))}
        </div>
      )}

      <div className="dashboard__graficos">
        <ChartCard
          titulo="Evolución de la demanda"
          descripcion="Puestos demandados · variación temporal"
          estado={g.demanda.state}
          onRetry={g.demanda.retry}
          altura={240}
          fuentes={(s) => s.flatMap((x) => x.fuentes)}
        >
          {(s) => <SerieHistoricaChart series={s} altura={240} />}
        </ChartCard>

        <ChartCard
          titulo="Sectores con mayor demanda"
          descripcion="Puestos demandados en el último período"
          estado={g.sectores.state}
          onRetry={g.sectores.retry}
          altura={240}
          fuentes={(r) => r.fuentes}
        >
          {(r) => <RankingList ranking={r} />}
        </ChartCard>
      </div>

      <div className="page__columns">
        <ChartCard
          titulo="Ocupaciones destacadas"
          descripcion={filtros.sector ? 'Dentro del sector elegido' : 'Todas las ocupaciones'}
          estado={g.ocupaciones.state}
          onRetry={g.ocupaciones.retry}
          altura={200}
          fuentes={(r) => r.fuentes}
        >
          {(r) => <RankingList ranking={r} />}
        </ChartCard>

        <ChartCard
          titulo="Habilidades más solicitadas"
          descripcion="Según avisos de empleo"
          estado={g.habilidades.state}
          onRetry={g.habilidades.retry}
          altura={200}
          fuentes={(r) => r.fuentes}
          mensajeSinDatos="Por ahora solo hay fuente oficial de habilidades para Chile (SENCE — SABE)."
        >
          {(r) => <RankingList ranking={r} />}
        </ChartCard>
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
