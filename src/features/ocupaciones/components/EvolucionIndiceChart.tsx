import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import type { EvolucionIndicePunto } from '../../../services/mock/ocupaciones';
import { SinDatos } from '../../../components/common/SinDatos';

export function EvolucionIndiceChart({ evolucion }: { evolucion: EvolucionIndicePunto[] }) {
  if (evolucion.length === 0) return <SinDatos />;

  return (
    <ResponsiveContainer width="100%" height={220}>
      <LineChart data={evolucion}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="periodo" />
        <YAxis domain={[0, 100]} />
        <Tooltip />
        <Line type="monotone" dataKey="indice" stroke="#3b82f6" strokeWidth={2} dot />
      </LineChart>
    </ResponsiveContainer>
  );
}
