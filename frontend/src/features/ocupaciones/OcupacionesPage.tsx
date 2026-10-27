import { useState } from 'react';
import { FiltrosBar } from '../../components/common/FiltrosBar';
import { SinDatos } from '../../components/common/SinDatos';
import { FuenteBadge } from '../../components/common/FuenteBadge';
import { useOcupacionesData } from './hooks/useOcupacionesData';
import { RankingOcupacionesTable } from './components/RankingOcupacionesTable';
import { IndiceEmpleabilidadChart } from './components/IndiceEmpleabilidadChart';
import { EvolucionIndiceChart } from './components/EvolucionIndiceChart';

// Vista 2 — Ocupaciones.
// Ranking de ocupaciones con comparación entre países, Índice de
// Empleabilidad con sus dimensiones y evolución histórica por país.
// Filtros activos: Países (múltiple) · Sector · Período.
// Se muestran las primeras 10 para que el detalle quede a la vista;
// el botón despliega las ~20 del catálogo.
const FILAS_INICIALES = 10;

export function OcupacionesPage() {
  const [verTodas, setVerTodas] = useState(false);
  const { paises, togglePais, filas, seleccionada, seleccionadaId, setSeleccionadaId, dimensiones, evolucion } =
    useOcupacionesData();

  return (
    <section className="page">
      <h2>Ocupaciones</h2>
      <p className="page__descripcion">
        Compará puestos disponibles e Índice de Empleabilidad de cada ocupación entre países. Elegí una fila para ver
        su detalle.
      </p>
      <FiltrosBar mostrarSector mostrarPeriodo paisesMultiples={{ seleccionados: paises, onToggle: togglePais }} />

      {paises.length === 0 ? (
        <SinDatos mensaje="Seleccioná uno o más países para comparar ocupaciones." />
      ) : (
        <div className="ocupaciones__layout">
          <article className="chart-card">
            <header className="chart-card__header">
              <div>
                <h3>Ranking de ocupaciones</h3>
                <p className="chart-card__descripcion">Ordenado por puestos del primer país seleccionado</p>
              </div>
            </header>
            <RankingOcupacionesTable
              filas={verTodas ? filas : filas.slice(0, FILAS_INICIALES)}
              paises={paises}
              seleccionadaId={seleccionadaId}
              onSeleccionar={setSeleccionadaId}
            />
            {filas.length > FILAS_INICIALES && (
              <button type="button" className="ocupaciones__ver-mas" onClick={() => setVerTodas(!verTodas)}>
                {verTodas ? 'Ver menos' : `Ver las ${filas.length} ocupaciones`}
              </button>
            )}
          </article>

          {seleccionada && (
            <aside className="ocupaciones__detalle" aria-label={`Detalle de ${seleccionada.nombre}`}>
              <article className="chart-card">
                <header className="chart-card__header">
                  <div>
                    <p className="ocupaciones__detalle-titulo">Detalle de la ocupación</p>
                    <h3>{seleccionada.nombre}</h3>
                    <p className="chart-card__descripcion">Índice de empleabilidad total y sus dimensiones (0–100)</p>
                  </div>
                </header>
                <IndiceEmpleabilidadChart dimensiones={dimensiones} paises={paises} />
                <footer className="chart-card__fuentes">
                  {paises.map((p) => {
                    const d = seleccionada.porPais[p];
                    return d ? <FuenteBadge key={p} fuente={d.fuente} tipo="calculado" /> : null;
                  })}
                </footer>
              </article>

              <article className="chart-card">
                <header className="chart-card__header">
                  <div>
                    <h3>Evolución del índice</h3>
                    <p className="chart-card__descripcion">{seleccionada.nombre} · una línea por país</p>
                  </div>
                </header>
                <EvolucionIndiceChart evolucion={evolucion} paises={paises} />
              </article>
            </aside>
          )}
        </div>
      )}
    </section>
  );
}
