import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { SerieHistorica } from '../../../services/mock/tendencias';
import { SinDatos } from '../../../components/common/SinDatos';

export function SerieHistoricaChart({ serie }: { serie: SerieHistorica[] }) {
  if (serie.length === 0) return <SinDatos />;

  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={serie}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="periodo" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="empleo" name="Empleo" stroke="#3b82f6" strokeWidth={2} />
        <Line type="monotone" dataKey="salario" name="Salario (índice)" stroke="#10b981" strokeWidth={2} />
        <Line type="monotone" dataKey="actividadSectorial" name="Actividad sectorial" stroke="#f59e0b" strokeWidth={2} />
      </LineChart>
    </ResponsiveContainer>
  );
}
