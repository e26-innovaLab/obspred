import { Area, CartesianGrid, ComposedChart, Legend, Line, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import type { Proyeccion } from '../../../types/kpi';
import { SinDatos } from '../../../components/common/SinDatos';
import { CHART_THEME, EJE_PROPS, PALETA_MARCA, TRAZO_TIPO } from '../../../styles/paletaMarca';
import { filasProyeccion, formatPeriodo, formatValor, puedeProyectar } from '../../../components/charts/series';

// Histórico (línea continua) + proyección (punteada) + banda de confianza.
// Regla del proyecto: sin ≥ 3 períodos históricos comparables no se muestra
// proyección — nunca se estima sin base suficiente.
export function ProyeccionPanel({ proyeccion, altura = 280 }: { proyeccion: Proyeccion; altura?: number }) {
  if (!puedeProyectar(proyeccion)) {
    return (
      <SinDatos
        mensaje={
          proyeccion.motivoNoProyectable ??
          'No hay suficientes períodos históricos comparables para proyectar (se requieren al menos 3).'
        }
      />
    );
  }

  const filas = filasProyeccion(proyeccion);
  const ultimoObservado = [...filas].reverse().find((f) => f.observado != null)?.periodo;
  const confianza = Math.round(proyeccion.nivelConfianza * 100);

  return (
    <>
      <ResponsiveContainer width="100%" height={altura}>
        <ComposedChart data={filas} margin={{ top: 8, right: 16, bottom: 0, left: 0 }}>
          <CartesianGrid stroke={CHART_THEME.grilla} vertical={false} />
          <XAxis dataKey="periodo" tickFormatter={formatPeriodo} {...EJE_PROPS} />
          <YAxis width={56} domain={['auto', 'auto']} {...EJE_PROPS} />
          <Tooltip
            labelFormatter={(l) => formatPeriodo(String(l))}
            formatter={(v, nombre) =>
              Array.isArray(v)
                ? [`${formatValor(v[0], proyeccion.unidad)} – ${formatValor(v[1], proyeccion.unidad)}`, nombre]
                : [formatValor(v as number | null, proyeccion.unidad), nombre]
            }
          />
          <Legend />
          <Area
            dataKey="banda"
            name={`Rango probable (${confianza} %)`}
            stroke="none"
            fill={CHART_THEME.bandaConfianza}
            fillOpacity={CHART_THEME.bandaOpacidad}
            isAnimationActive={false}
          />
          <Line
            dataKey="observado"
            name="Histórico"
            stroke={PALETA_MARCA.azulOscuro}
            strokeWidth={2}
            dot={{ r: 3 }}
            connectNulls={false}
            isAnimationActive={false}
          />
          <Line
            dataKey="proyectado"
            name="Proyección"
            stroke={PALETA_MARCA.azulClaro}
            strokeWidth={2}
            strokeDasharray={TRAZO_TIPO.proyeccion}
            dot={{ r: 3, fill: PALETA_MARCA.blanco }}
            isAnimationActive={false}
          />
          {ultimoObservado && (
            <ReferenceLine
              x={ultimoObservado}
              stroke={PALETA_MARCA.gris}
              strokeDasharray="3 3"
              label={{ value: 'Último dato', position: 'insideTopRight', fontSize: 11, fill: CHART_THEME.texto }}
            />
          )}
        </ComposedChart>
      </ResponsiveContainer>
      <p className="proyeccion-panel__nota">
        Proyección orientativa ({proyeccion.metodo.toLowerCase()}). No reemplaza el dato observado.
      </p>
    </>
  );
}
