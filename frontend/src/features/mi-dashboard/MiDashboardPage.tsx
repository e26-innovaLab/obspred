import './MiDashboardPage.css';
import { useInforme } from '../../store/useInforme';
import { SerieHistoricaChart } from '../../components/charts/SerieHistoricaChart';
import { RankingList } from '../dashboard/components/RankingList';
import { SinDatos } from '../../components/common/SinDatos';
import { FuenteBadge } from '../../components/common/FuenteBadge';
import type { Snapshot } from '../../store/informeContextInstance';

// Vista "Mi informe" — Dashboard personalizable.
// Muestra los gráficos que el usuario fue guardando desde cualquier página.
// El usuario puede quitarlos individualmente y descargar el conjunto como PDF.

export function MiDashboardPage() {
  const { snapshots, quitar, limpiar } = useInforme();

  const descargarPDF = () => window.print();

  return (
    <section className="page">
      <h2>Mi informe</h2>
      <p className="page__descripcion">
        Guardá gráficos desde cualquier página con el botón <strong>＋ Mi informe</strong> y
        descargalos juntos como PDF.
      </p>

      {snapshots.length === 0 ? (
        <SinDatos mensaje="Todavía no guardaste ningún gráfico. Navegá por el observatorio y usá el botón «＋ Mi informe» en cada gráfico que te interese." />
      ) : (
        <>
          {/* Barra de acciones */}
          <div className="mi-dashboard__acciones">
            <span className="mi-dashboard__contador">
              {snapshots.length} {snapshots.length === 1 ? 'gráfico guardado' : 'gráficos guardados'}
            </span>
            <div className="mi-dashboard__acciones-botones">
              <button
                type="button"
                className="mi-dashboard__btn-limpiar"
                onClick={limpiar}
                aria-label="Vaciar el informe"
              >
                Vaciar informe
              </button>
              <button
                type="button"
                className="mi-dashboard__btn-pdf"
                onClick={descargarPDF}
                aria-label="Descargar informe como PDF"
              >
                ↓ Descargar PDF
              </button>
            </div>
          </div>

          {/* Preview / contenido del informe */}
          <div className="mi-dashboard__preview" id="mi-dashboard-preview">
            {/* Encabezado visible en el PDF */}
            <div className="mi-dashboard__informe-header">
              <h3>Observatorio Predictivo de Tendencias</h3>
              <p>Informe personalizado · {snapshots[0]?.fechaGuardado}</p>
            </div>

            <div className="dashboard__graficos">
              {snapshots.map((snap) => (
                <SnapshotCard key={snap.id} snap={snap} onQuitar={() => quitar(snap.id)} />
              ))}
            </div>
          </div>
        </>
      )}
    </section>
  );
}

// Renderiza un snapshot guardado con su gráfico y fuentes.
function SnapshotCard({ snap, onQuitar }: { snap: Snapshot; onQuitar: () => void }) {
  const { titulo, descripcion, contenido, fuentes, filtros, fechaGuardado } = snap;

  return (
    <article className="chart-card mi-dashboard__snapshot">
      <header className="chart-card__header">
        <div>
          <h3>{titulo}</h3>
          {descripcion && <p className="chart-card__descripcion">{descripcion}</p>}
          <p className="mi-dashboard__snapshot-meta">
            {filtros.pais}
            {filtros.sector ? ` · ${filtros.sector}` : ''}
            {filtros.periodo ? ` · ${filtros.periodo}` : ''}
            {' · '}
            {fechaGuardado}
          </p>
        </div>
        <button
          type="button"
          className="mi-dashboard__btn-quitar"
          onClick={onQuitar}
          aria-label={`Quitar "${titulo}" del informe`}
          title="Quitar del informe"
        >
          ✕
        </button>
      </header>

      <div className="chart-card__cuerpo">
        {contenido.tipo === 'serie' && (
          <SerieHistoricaChart series={contenido.datos} altura={240} />
        )}
        {contenido.tipo === 'ranking' && (
          <RankingList ranking={contenido.datos} />
        )}
      </div>

      {fuentes.length > 0 && (
        <footer className="chart-card__fuentes">
          {fuentes.map((f) => (
            <FuenteBadge key={`${f.fuente.nombre}-${f.tipo}`} fuente={f.fuente} tipo={f.tipo} />
          ))}
        </footer>
      )}
    </article>
  );
}
