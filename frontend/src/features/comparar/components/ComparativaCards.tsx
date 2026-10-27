import type { ComparativaIndicador } from '../../../types/kpi';
import { PAISES } from '../../../services/mock/catalogo';
import { SERIE_PAIS } from '../../../styles/paletaMarca';
import { formatPeriodo, formatValor } from '../../../components/charts/series';

const nombrePais = (id: string) => PAISES.find((p) => p.id === id)?.nombre ?? id;

// Tarjetas "Indicadores comparativos" del Figma: un indicador por tarjeta y
// una fila por país con barra proporcional. Si un país informa un período
// distinto al más reciente, se aclara para no comparar peras con manzanas.
export function ComparativaCards({ indicadores }: { indicadores: ComparativaIndicador[] }) {
  return (
    <div className="comparativa-grid">
      {indicadores.map((ind) => {
        const max = Math.max(...ind.valores.map((v) => v.valor ?? 0));
        const periodoMasReciente = ind.valores
          .map((v) => v.periodo)
          .filter((p): p is string => p !== null)
          .sort()
          .at(-1);

        return (
          <article key={ind.indicador} className="comparativa-card">
            <h4>{ind.nombre}</h4>
            <ul>
              {ind.valores.map((v) => (
                <li key={v.pais}>
                  <span className="comparativa-card__pais">{nombrePais(v.pais)}</span>
                  {v.valor === null ? (
                    <span className="comparativa-card__sin-dato">Sin dato</span>
                  ) : (
                    <>
                      <span className="comparativa-card__barra" aria-hidden>
                        <span
                          style={{
                            width: `${max > 0 ? (v.valor / max) * 100 : 0}%`,
                            background: SERIE_PAIS[v.pais].color,
                          }}
                        />
                      </span>
                      <strong>{formatValor(v.valor, ind.unidad)}</strong>
                    </>
                  )}
                  {v.periodo && v.periodo !== periodoMasReciente && (
                    <span className="comparativa-card__periodo">dato de {formatPeriodo(v.periodo)}</span>
                  )}
                </li>
              ))}
            </ul>
          </article>
        );
      })}
    </div>
  );
}
