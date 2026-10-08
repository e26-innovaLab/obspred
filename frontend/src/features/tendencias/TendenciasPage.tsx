import { useState } from 'react';
import { FiltrosBar } from '../../components/common/FiltrosBar';
import { INDICADORES } from '../../services/mock/catalogo';
import { useTendenciasData } from './hooks/useTendenciasData';
import { ChartCard } from '../../components/charts/ChartCard';
import { SerieHistoricaChart } from '../../components/charts/SerieHistoricaChart';
import { ProyeccionPanel } from './components/ProyeccionPanel';
import { CambiosSignificativos } from './components/CambiosSignificativos';

// Vista 3 — Tendencias.
// Evolución histórica de un indicador y su proyección (solo con serie
// suficiente). Filtros activos: País · Sector · Ocupación + selector de
// indicador (Figma: "Evolución de indicadores → Seleccionar indicador").
export function TendenciasPage() {
  const [indicador, setIndicador] = useState(INDICADORES[0].id);
  const { serie, proyeccion, cambios } = useTendenciasData(indicador);
  const marcas = cambios.state.status === 'success' ? cambios.state.data : [];
  const nombre = INDICADORES.find((i) => i.id === indicador)?.nombre ?? '';

  const selector = (
    <label className="chart-card__selector">
      Indicador
      <select value={indicador} onChange={(e) => setIndicador(e.target.value)}>
        {INDICADORES.map((i) => (
          <option key={i.id} value={i.id}>
            {i.nombre}
          </option>
        ))}
      </select>
    </label>
  );

  return (
    <section className="page">
      <h2>Tendencias</h2>
      <p className="page__descripcion">Analizá la evolución de los principales indicadores del mercado laboral.</p>
      <FiltrosBar mostrarSector mostrarOcupacion mostrarPeriodo={false} />

      <ChartCard
        titulo="Evolución de indicadores"
        descripcion={nombre}
        estado={serie.state}
        onRetry={serie.retry}
        acciones={selector}
        fuentes={(series) => series.flatMap((s) => s.fuentes)}
        mensajeSinDatos="Las fuentes de este país no publican este indicador para la selección actual."
      >
        {(series) => (
          <>
            <SerieHistoricaChart series={series} marcas={marcas} />
            {cambios.state.status === 'success' && <CambiosSignificativos cambios={marcas} />}
          </>
        )}
      </ChartCard>

      <ChartCard
        titulo="Proyección"
        descripcion={`${nombre} · próximos 6 meses`}
        estado={proyeccion.state}
        onRetry={proyeccion.retry}
        fuentes={(p) => p.fuentes}
      >
        {(p) => <ProyeccionPanel proyeccion={p} />}
      </ChartCard>
    </section>
  );
}
