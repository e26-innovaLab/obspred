import type { MapaCalor } from '../../../types/kpi';
import { PAISES } from '../../../services/mock/catalogo';
import { formatPeriodo, formatValor } from '../../../components/charts/series';

// Escala secuencial en 5 pasos, del celeste muy claro al azul oscuro de marca.
// Pasos discretos (no degradé continuo) para que la leyenda se pueda leer.
// `texto` asegura contraste ≥ 4.5:1 del número sobre cada color.
const ESCALA_CALOR = [
  { fondo: '#E3EEF3', texto: '#1D3343' },
  { fondo: '#A9CADA', texto: '#1D3343' },
  { fondo: '#6FA6C0', texto: '#1D3343' },
  { fondo: '#035C80', texto: '#FCFCFC' },
  { fondo: '#1D3343', texto: '#FCFCFC' },
] as const;

const nombrePais = (id: string) => PAISES.find((p) => p.id === id)?.nombre ?? id;

/** Índice 0–4 del paso de color (si todos los valores son iguales, el del medio). */
function pasoEscala(valor: number, min: number, max: number): number {
  if (max === min) return 2;
  const t = (valor - min) / (max - min);
  return Math.min(ESCALA_CALOR.length - 1, Math.floor(t * ESCALA_CALOR.length));
}

// Mapa de calor sector × país hecho con una <table> y CSS: no necesita
// librería, es accesible para lectores de pantalla y cada celda muestra el
// número, así el color nunca es la única forma de leer el dato.
export function MapaCalorGrid({ mapa }: { mapa: MapaCalor }) {
  const valores = mapa.celdas.flatMap((c) => (c.valor === null ? [] : [c.valor]));
  const min = Math.min(...valores);
  const max = Math.max(...valores);
  const celda = (sector: string, pais: string) => mapa.celdas.find((c) => c.sector === sector && c.pais === pais);

  return (
    <div className="mapa-calor">
      <div className="mapa-calor__scroll">
        <table>
          <caption className="visually-hidden">
            {mapa.nombre} por sector y país, {formatPeriodo(mapa.periodo)}
          </caption>
          <thead>
            <tr>
              <th scope="col">Sector</th>
              {mapa.paises.map((p) => (
                <th key={p} scope="col">
                  {nombrePais(p)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {mapa.sectores.map((s) => (
              <tr key={s.id}>
                <th scope="row">{s.nombre}</th>
                {mapa.paises.map((p) => {
                  const c = celda(s.id, p);
                  if (!c || c.valor === null) {
                    return (
                      <td key={p} className="mapa-calor__celda mapa-calor__celda--vacia">
                        Sin dato
                      </td>
                    );
                  }
                  const color = ESCALA_CALOR[pasoEscala(c.valor, min, max)];
                  const variacion =
                    c.variacionPct === null ? '' : `${c.variacionPct > 0 ? '▲' : c.variacionPct < 0 ? '▼' : '■'} ${formatValor(Math.abs(c.variacionPct), '%')}`;
                  return (
                    <td
                      key={p}
                      className="mapa-calor__celda"
                      style={{ background: color.fondo, color: color.texto }}
                      title={`${s.nombre} · ${nombrePais(p)}: ${formatValor(c.valor, mapa.unidad)}${variacion ? ` (${variacion} vs. período anterior)` : ''}`}
                    >
                      <strong>{formatValor(c.valor, mapa.unidad)}</strong>
                      {variacion && <span className="mapa-calor__variacion">{variacion}</span>}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mapa-calor__leyenda" aria-hidden>
        <span>{formatValor(min, mapa.unidad)}</span>
        {ESCALA_CALOR.map((c) => (
          <span key={c.fondo} className="mapa-calor__paso" style={{ background: c.fondo }} />
        ))}
        <span>{formatValor(max, mapa.unidad)}</span>
        <span className="mapa-calor__paso mapa-calor__celda--vacia" />
        <span>Sin dato</span>
      </div>
    </div>
  );
}
