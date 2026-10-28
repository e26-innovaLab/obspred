import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import type { HabilidadComparada } from '../../../types/brecha';
import { SinDatos } from '../../../components/common/SinDatos';
import { PALETA_MARCA } from '../../../styles/paletaMarca';

// Gráfico horizontal: las habilidades van en el eje Y para que los nombres
// se lean sin rotar ni cortarse. XAxis muestra el puntaje 0–100.
export function BrechasChart({ habilidades }: { habilidades: HabilidadComparada[] }) {
  if (habilidades.length === 0) return <SinDatos />;

  const altura = Math.max(260, habilidades.length * 48);

  return (
    <ResponsiveContainer width="100%" height={altura}>
      <BarChart
        layout="vertical"
        data={habilidades}
        margin={{ top: 4, right: 24, bottom: 4, left: 8 }}
        barCategoryGap="30%"
        barGap={4}
      >
        <CartesianGrid strokeDasharray="3 3" horizontal={false} />
        <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 12 }} />
        <YAxis
          type="category"
          dataKey="habilidad"
          width={180}
          tick={{ fontSize: 13 }}
        />
        <Tooltip
          formatter={(value: number, name: string) => [`${value}`, name]}
          contentStyle={{ fontSize: 13 }}
        />
        <Legend wrapperStyle={{ fontSize: 13 }} />
        <Bar
          dataKey="demanda"
          name="Demanda del mercado"
          fill={PALETA_MARCA.azulClaro}
          radius={[0, 4, 4, 0]}
        />
        <Bar
          dataKey="ofertaFormativa"
          name="Oferta formativa"
          fill={PALETA_MARCA.amarillo}
          radius={[0, 4, 4, 0]}
        />
      </BarChart>
    </ResponsiveContainer>
  );
}
