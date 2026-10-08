import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { Pais } from '../../../types/kpi';
import type { FilaPorPais } from '../hooks/useOcupacionesData';
import { SinDatos } from '../../../components/common/SinDatos';
import { PAISES } from '../../../services/mock/catalogo';
import { formatPeriodo } from '../../../components/charts/series';
import { CHART_THEME, EJE_PROPS, SERIE_PAIS, ordenPorPais } from '../../../styles/paletaMarca';

const nombrePais = (id: Pais) => PAISES.find((p) => p.id === id)?.nombre ?? id;

// Evolución del Índice de Empleabilidad de la ocupación elegida, una línea por país.
export function EvolucionIndiceChart({ evolucion, paises }: { evolucion: FilaPorPais[]; paises: Pais[] }) {
  if (evolucion.length === 0 || paises.length === 0) return <SinDatos />;

  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={evolucion} margin={{ top: 8, right: 16, bottom: 0, left: 0 }}>
        <CartesianGrid stroke={CHART_THEME.grilla} vertical={false} />
        <XAxis dataKey="nombre" tickFormatter={formatPeriodo} {...EJE_PROPS} />
        <YAxis domain={[0, 100]} width={40} {...EJE_PROPS} />
        <Tooltip itemSorter={ordenPorPais} labelFormatter={(l) => formatPeriodo(String(l))} />
        <Legend itemSorter={ordenPorPais} />
        {paises.map((p) => (
          <Line
            key={p}
            type="monotone"
            dataKey={p}
            name={nombrePais(p)}
            stroke={SERIE_PAIS[p].color}
            strokeWidth={2}
            dot={{ r: 3, fill: SERIE_PAIS[p].color }}
            isAnimationActive={false}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}
