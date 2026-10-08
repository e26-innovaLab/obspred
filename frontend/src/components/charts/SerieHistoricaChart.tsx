import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ReferenceDot, ResponsiveContainer } from 'recharts';
import type { CambioSignificativo, SerieTemporal } from '../../types/kpi';
import { CHART_THEME, EJE_PROPS, PALETA_MARCA, SERIE_PAIS } from '../../styles/paletaMarca';
import { PAISES } from '../../services/mock/catalogo';
import { formatPeriodo, formatValor, pivotearPorPais } from './series';

interface Props {
  series: SerieTemporal[]; // una por país; con un solo país se ve una línea
  altura?: number;
  /** Cambios significativos a marcar sobre la línea (alertas). */
  marcas?: CambioSignificativo[];
}

const nombrePais = (id: string) => PAISES.find((p) => p.id === id)?.nombre ?? id;

// Evolución histórica de UN indicador (una unidad por gráfico: no se mezclan
// % con índices en el mismo eje). Los períodos sin dato quedan como hueco
// (connectNulls=false): no se interpola lo que la fuente no publicó.
// Las `marcas` (círculo amarillo con "!") señalan cambios significativos.
export function SerieHistoricaChart({ series, altura = 280, marcas = [] }: Props) {
  const filas = pivotearPorPais(series);
  const unidad = series[0]?.unidad ?? '';

  return (
    <ResponsiveContainer width="100%" height={altura}>
      <LineChart data={filas} margin={{ top: 8, right: 16, bottom: 0, left: 0 }}>
        <CartesianGrid stroke={CHART_THEME.grilla} vertical={false} />
        <XAxis dataKey="periodo" tickFormatter={formatPeriodo} {...EJE_PROPS} />
        <YAxis width={56} {...EJE_PROPS} />
        <Tooltip
          labelFormatter={(l) => formatPeriodo(String(l))}
          formatter={(v, nombre) => [formatValor(v as number | null, unidad), nombre]}
        />
        <Legend />
        {series.map((s) => (
          <Line
            key={s.pais}
            type="monotone"
            dataKey={s.pais}
            name={nombrePais(s.pais)}
            stroke={SERIE_PAIS[s.pais].color}
            strokeWidth={2}
            connectNulls={false}
            dot={{ r: 3, fill: SERIE_PAIS[s.pais].color }}
            activeDot={{ r: 5 }}
            isAnimationActive={false}
          />
        ))}
        {marcas.map((m) => {
          const y = filas.find((f) => f.periodo === m.periodo)?.[m.pais];
          if (y == null) return null;
          return (
            <ReferenceDot
              key={m.id}
              x={m.periodo}
              y={y}
              r={9}
              fill={PALETA_MARCA.amarillo}
              stroke={PALETA_MARCA.azulOscuro}
              strokeWidth={2}
              label={{ value: '!', position: 'center', fontSize: 12, fontWeight: 700, fill: PALETA_MARCA.azulOscuro }}
            />
          );
        })}
      </LineChart>
    </ResponsiveContainer>
  );
}
