import { Line, LineChart, ResponsiveContainer, YAxis } from 'recharts';
import type { Indicador } from '../../types/kpi';
import { PALETA_MARCA } from '../../styles/paletaMarca';
import { formatPeriodo, formatValor } from '../charts/series';
import { FuenteBadge } from './FuenteBadge';

interface Props {
  indicador: Indicador<number | null>;
  /** Variación % contra el período anterior (Figma: "Variación / Tendencia"). */
  variacionPct?: number | null;
  /** Qué dirección es buena: que baje el desempleo es positivo. */
  sentidoPositivo?: 'sube' | 'baja';
  /** Últimos valores para la mini línea; null = sin dato en ese período. */
  sparkline?: Array<number | null>;
}

export function KpiCard({ indicador, variacionPct, sentidoPositivo = 'sube', sparkline }: Props) {
  const hayVariacion = variacionPct !== undefined && variacionPct !== null;
  const esBueno = hayVariacion && (sentidoPositivo === 'sube' ? variacionPct > 0 : variacionPct < 0);
  const estado = !hayVariacion || variacionPct === 0 ? 'neutro' : esBueno ? 'bueno' : 'malo';
  const flecha = !hayVariacion ? '' : variacionPct > 0 ? '▲' : variacionPct < 0 ? '▼' : '■';

  return (
    <article className="kpi-card">
      <h3>{indicador.nombre}</h3>
      <p className="kpi-card__valor">
        {indicador.valor === null ? 'Sin dato' : formatValor(indicador.valor, indicador.unidad === '%' ? '%' : '')}
        {indicador.unidad && indicador.unidad !== '%' && indicador.valor !== null && (
          <span className="kpi-card__unidad">{indicador.unidad}</span>
        )}
      </p>

      {hayVariacion && (
        <p className="kpi-card__variacion" data-estado={estado}>
          {flecha} {formatValor(Math.abs(variacionPct), '%')}
          <span> vs. período anterior · {formatPeriodo(indicador.periodo)}</span>
        </p>
      )}

      {sparkline && sparkline.some((v) => v !== null) && (
        <div className="kpi-card__sparkline" aria-hidden>
          <ResponsiveContainer width="100%" height={36}>
            <LineChart data={sparkline.map((v, i) => ({ i, v }))} margin={{ top: 4, right: 2, bottom: 4, left: 2 }}>
              {/* Eje oculto ajustado al rango: si arranca en 0 la línea se ve plana. */}
              <YAxis hide domain={['dataMin', 'dataMax']} />
              <Line
                dataKey="v"
                stroke={PALETA_MARCA.azulClaro}
                strokeWidth={2}
                dot={false}
                connectNulls={false}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      <FuenteBadge fuente={indicador.fuente} tipo={indicador.tipo} />
    </article>
  );
}
