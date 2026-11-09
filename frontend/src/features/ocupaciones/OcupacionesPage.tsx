import { useState } from 'react';
import { FiltrosBar } from '../../components/common/FiltrosBar';
import { SinDatos } from '../../components/common/SinDatos';
import { FuenteBadge } from '../../components/common/FuenteBadge';
import { useOcupacionesData } from './hooks/useOcupacionesData';
import { RankingOcupacionesTable } from './components/RankingOcupacionesTable';
import { IndiceEmpleabilidadChart } from './components/IndiceEmpleabilidadChart';
import { EvolucionIndiceChart } from './components/EvolucionIndiceChart';
import { useInforme } from '../../store/useInforme';
import { useFiltros } from '../../store/useFiltros';
import type { Ranking, SerieTemporal, TipoIndicador } from '../../types/kpi';

const FILAS_INICIALES = 10;

export function OcupacionesPage() {
  const [verTodas, setVerTodas] = useState(false);
  const { paises, togglePais, filas, seleccionada, seleccionadaId, setSeleccionadaId, dimensiones, evolucion } =
    useOcupacionesData();
  const informe = useInforme();
  const { filtros } = useFiltros();

  const fechaGuardado = new Date().toLocaleDateString('es-AR', {
    day: '2-digit', month: 'long', year: 'numeric',
  });

  // ---- Guardar ranking de ocupaciones ----
  const idRanking = 'ocupaciones-ranking';
  const guardadoRanking = informe.estaGuardado(idRanking);
  const handleGuardarRanking = () => {
    if (guardadoRanking) { informe.quitar(idRanking); return; }
    const datos: Ranking = {
      dimension: 'ocupacion',
      indicador: 'puestos_disponibles',
      unidad: 'puestos',
      periodo: filtros.periodo ?? '',
      items: filas.map((f) => ({
        id: f.ocupacionId,
        nombre: f.nombre,
        valor: f.porPais[paises[0]]?.puestos ?? null,
        variacionPct: null,
        tendencia: null,
      })),
      fuentes: [],
    };
    informe.guardar({
      id: idRanking,
      titulo: 'Ranking de ocupaciones',
      descripcion: 'Puestos disponibles por ocupación · primer país seleccionado',
      contenido: { tipo: 'ranking', datos },
      fuentes: [],
      filtros,
      fechaGuardado,
    });
  };

  // ---- Guardar evolución del índice ----
  const idEvolucion = seleccionada
    ? `ocupaciones-evolucion-${seleccionada.ocupacionId}`
    : 'ocupaciones-evolucion';
  const guardadoEvolucion = informe.estaGuardado(idEvolucion);
  const handleGuardarEvolucion = () => {
    if (!seleccionada) return;
    if (guardadoEvolucion) { informe.quitar(idEvolucion); return; }
    const datos: SerieTemporal[] = paises.map((pais) => ({
      pais,
      indicador: 'indice_empleabilidad',
      nombre: `Índice – ${pais}`,
      unidad: 'índice 0–100',
      frecuencia: 'trimestral',
      puntos: evolucion.map((e) => ({
        periodo: e.nombre,
        valor: (e[pais] as number | undefined) ?? null,
        tipo: 'calculado' as TipoIndicador,
      })),
      fuentes: [],
    }));
    informe.guardar({
      id: idEvolucion,
      titulo: `Evolución del índice – ${seleccionada.nombre}`,
      contenido: { tipo: 'serie', datos },
      fuentes: [],
      filtros,
      fechaGuardado,
    });
  };

  return (
    <section className="page">
      <h2>Ocupaciones</h2>
      <p className="page__descripcion">
        Comparás puestos disponibles e índice de Empleabilidad de cada ocupación entre países. Elegí una fila para ver
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
              <div className="chart-card__header-acciones">
                <button
                  type="button"
                  className={`chart-card__btn-guardar${guardadoRanking ? ' chart-card__btn-guardar--activo' : ''}`}
                  onClick={handleGuardarRanking}
                  aria-pressed={guardadoRanking}
                  title={guardadoRanking ? 'Quitar del informe' : 'Guardar en mi informe'}
                >
                  {guardadoRanking ? '✓ Guardado' : '＋ Mi informe'}
                </button>
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
                  <div className="chart-card__header-acciones">
                    <button
                      type="button"
                      className={`chart-card__btn-guardar${guardadoEvolucion ? ' chart-card__btn-guardar--activo' : ''}`}
                      onClick={handleGuardarEvolucion}
                      aria-pressed={guardadoEvolucion}
                      title={guardadoEvolucion ? 'Quitar del informe' : 'Guardar en mi informe'}
                    >
                      {guardadoEvolucion ? '✓ Guardado' : '＋ Mi informe'}
                    </button>
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
