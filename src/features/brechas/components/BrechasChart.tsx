import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { HabilidadComparada } from '../../../types/brecha';
import { SinDatos } from '../../../components/common/SinDatos';
import { PALETA_MARCA } from '../../../styles/paletaMarca';

export function BrechasChart({ habilidades }: { habilidades: HabilidadComparada[] }) {
  if (habilidades.length === 0) return <SinDatos />;

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={habilidades} margin={{ bottom: 40 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="habilidad" angle={-20} textAnchor="end" interval={0} height={70} />
        <YAxis domain={[0, 100]} />
        <Tooltip />
        <Legend />
        <Bar dataKey="demanda" name="Demanda del mercado" fill={PALETA_MARCA.azulClaro} radius={[4, 4, 0, 0]} />
        <Bar dataKey="ofertaFormativa" name="Oferta formativa" fill={PALETA_MARCA.amarillo} radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
