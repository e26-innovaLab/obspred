import { useState } from 'react';
import { ChartCard } from '../../components/charts/ChartCard';
import { SerieHistoricaChart } from '../../components/charts/SerieHistoricaChart';
import { RankingList } from '../dashboard/components/RankingList';
import { SinDatos } from '../../components/common/SinDatos';
import { useDashboardGraficos } from '../dashboard/hooks/useDashboardData';

// Vista "Mi informe" — Dashboard personalizable.
// El usuario selecciona los gráficos que quiere incluir y descarga el informe como PDF.
// Los gráficos disponibles reutilizan los mismos datos del Dashboard general.

interface Widget {
  id: string;
  titulo: string;
  descripcion: string;
}

const WIDGETS_DISPONIBLES: Widget[] = [
  {
    id: 'demanda',
    titulo: 'Evolución de la demanda',
    descripcion: 'Puestos demandados · variación temporal',
  },
  {
    id: 'sectores',
    titulo: 'Sectores con mayor demanda',
    descripcion: 'Puestos demandados en el último período',
  },
  {
    id: 'ocupaciones',
    titulo: 'Ocupaciones destacadas',
    descripcion: 'Las más demandadas en la selección actual',
  },
  {
    id: 'habilidades',
    titulo: 'Habilidades más solicitadas',
    descripcion: 'Según avisos de empleo',
  },
];

export function MiDashboardPage() {
  const [seleccionados, setSeleccionados] = useState<Set<string>>(new Set());
  const g = useDashboardGraficos();

  const toggle = (id: string) =>
    setSeleccionados((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });

  const descargarPDF = () => {
    window.print();
  };

  const fechaHoy = new Date().toLocaleDateString('es-AR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  });

  return (
    <section className="page">
      <h2>Mi informe</h2>
      <p className="page__descripcion">
        Seleccioná los gráficos que querés incluir, armá tu informe y descargalo como PDF.
      </p>

      <div className="mi-dashboard__layout">
        {/* Panel selector de gráficos */}
        <aside className="mi-dashboard__selector">
          <h3 className="mi-dashboard__selector-titulo">Gráficos disponibles</h3>
          <p className="mi-dashboard__selector-ayuda">Tildá los que querés incluir en tu informe.</p>

          {WIDGETS_DISPONIBLES.map((w) => (
            <label key={w.id} className={`mi-dashboard__opcion${seleccionados.has(w.id) ? ' mi-dashboard__opcion--activo' : ''}`}>
              <input
                type="checkbox"
                checked={seleccionados.has(w.id)}
                onChange={() => toggle(w.id)}
                className="mi-dashboard__checkbox"
              />
              <div className="mi-dashboard__opcion-texto">
                <strong>{w.titulo}</strong>
                <span>{w.descripcion}</span>
              </div>
            </label>
          ))}

          {seleccionados.size > 0 && (
            <button
              type="button"
              className="mi-dashboard__btn-pdf"
              onClick={descargarPDF}
              aria-label="Descargar informe como PDF"
            >
              ↓ Descargar PDF ({seleccionados.size} {seleccionados.size === 1 ? 'gráfico' : 'gráficos'})
            </button>
          )}
        </aside>

        {/* Área de preview */}
        <div className="mi-dashboard__main">
          {seleccionados.size === 0 ? (
            <SinDatos mensaje="Seleccioná al menos un gráfico para armar tu informe." />
          ) : (
            <div className="mi-dashboard__preview" id="mi-dashboard-preview">
              {/* Encabezado del informe (visible en PDF) */}
              <div className="mi-dashboard__informe-header">
                <h3>Observatorio Predictivo de Tendencias</h3>
                <p>Informe personalizado · {fechaHoy}</p>
              </div>

              {/* Gráficos seleccionados */}
              <div className="dashboard__graficos">
                {seleccionados.has('demanda') && (
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
                )}

                {seleccionados.has('sectores') && (
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
                )}

                {seleccionados.has('ocupaciones') && (
                  <ChartCard
                    titulo="Ocupaciones destacadas"
                    descripcion="Las más demandadas en la selección actual"
                    estado={g.ocupaciones.state}
                    onRetry={g.ocupaciones.retry}
                    altura={200}
                    fuentes={(r) => r.fuentes}
                  >
                    {(r) => <RankingList ranking={r} />}
                  </ChartCard>
                )}

                {seleccionados.has('habilidades') && (
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
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
