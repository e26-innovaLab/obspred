import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import type { DimensionIndice } from '../../../services/mock/ocupaciones';
import { SinDatos } from '../../../components/common/SinDatos';

export function IndiceEmpleabilidadChart({ dimensiones }: { dimensiones: DimensionIndice[] }) {
  if (dimensiones.length === 0) return <SinDatos />;

  return (
    <ResponsiveContainer width="100%" height={240}>
      <BarChart data={dimensiones} layout="vertical" margin={{ left: 24 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis type="number" domain={[0, 100]} />
        <YAxis type="category" dataKey="nombre" width={160} />
        <Tooltip />
        <Bar dataKey="valor" fill="#3b82f6" radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
