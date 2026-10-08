import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { Pais } from '../../../types/kpi';
import type { FilaPorPais } from '../hooks/useOcupacionesData';
import { SinDatos } from '../../../components/common/SinDatos';
import { PAISES } from '../../../services/mock/catalogo';
import { CHART_THEME, EJE_PROPS, SERIE_PAIS, ordenPorPais } from '../../../styles/paletaMarca';

const nombrePais = (id: Pais) => PAISES.find((p) => p.id === id)?.nombre ?? id;

// Índice de Empleabilidad y sus dimensiones (0–100), una barra por país.
// Responde "¿en qué país conviene más esta ocupación y por qué?".
export function IndiceEmpleabilidadChart({ dimensiones, paises }: { dimensiones: FilaPorPais[]; paises: Pais[] }) {
  if (dimensiones.length === 0 || paises.length === 0) return <SinDatos />;

  return (
    <ResponsiveContainer width="100%" height={Math.max(260, dimensiones.length * (paises.length * 14 + 20))}>
      <BarChart data={dimensiones} layout="vertical" margin={{ left: 8, right: 16 }} barGap={2}>
        <CartesianGrid stroke={CHART_THEME.grilla} horizontal={false} />
        <XAxis type="number" domain={[0, 100]} {...EJE_PROPS} />
        <YAxis type="category" dataKey="nombre" width={130} {...EJE_PROPS} />
        <Tooltip itemSorter={ordenPorPais} />
        <Legend itemSorter={ordenPorPais} />
        {paises.map((p) => (
          <Bar
            key={p}
            dataKey={p}
            name={nombrePais(p)}
            fill={SERIE_PAIS[p].color}
            radius={[0, 4, 4, 0]}
            barSize={12}
            isAnimationActive={false}
          />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
}
