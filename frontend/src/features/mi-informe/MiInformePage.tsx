import { useInforme } from '../../store/InformeContext';
import './MiInformePage.css';

export function MiInformePage() {
  const { graficos, quitar, limpiar } = useInforme();

  if (graficos.length === 0) {
    return (
      <section className="page mi-informe">
        <h2>Mi informe</h2>
        <div className="mi-informe__vacio">
          <p>Todavía no agregaste gráficos al informe.</p>
          <p className="mi-informe__hint">
            Usá el botón <strong>＋ Mi informe</strong> que aparece en cada sección para guardar una vista.
          </p>
        </div>
      </section>
    );
  }

  return (
    <section className="page mi-informe">
      <header className="mi-informe__header">
        <h2>Mi informe</h2>
        <div className="mi-informe__acciones">
          <button type="button" className="btn-secundario" onClick={limpiar}>
            Limpiar todo
          </button>
          <button type="button" className="btn-primario" onClick={() => window.print()}>
            Descargar PDF
          </button>
        </div>
      </header>

      <div className="mi-informe__grid">
        {graficos.map((g) => (
          <article key={g.id} className="chart-card mi-informe__card">
            <header className="chart-card__header">
              <div>
                <span className="mi-informe__seccion-badge">{g.seccion}</span>
                <h3>{g.titulo}</h3>
                {g.descripcion && <p className="chart-card__descripcion">{g.descripcion}</p>}
              </div>
              <button
                type="button"
                className="mi-informe__quitar"
                aria-label="Quitar del informe"
                onClick={() => quitar(g.id)}
              >
                ✕
              </button>
            </header>
            <div className="mi-informe__meta">
              {g.paises && g.paises.length > 0 && <span>Países: {g.paises.join(', ')}</span>}
              <span className="mi-informe__fecha">
                Guardado: {new Date(g.timestamp).toLocaleString('es-AR')}
              </span>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
