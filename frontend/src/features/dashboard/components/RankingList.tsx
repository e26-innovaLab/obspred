import type { Ranking } from '../../../types/kpi';
import { formatValor } from '../../../components/charts/series';

// Ranking con barras horizontales (Figma Inicio: "Sectores con mayor demanda",
// "Ocupaciones destacadas", "Habilidades más solicitadas"). HTML + CSS en vez
// de Recharts: los nombres largos se leen completos y se adapta al celular.
export function RankingList({ ranking }: { ranking: Ranking }) {
  const max = Math.max(...ranking.items.map((i) => i.valor ?? 0));

  return (
    <ol className="ranking-list">
      {ranking.items.map((item) => (
        <li key={item.id}>
          <span className="ranking-list__nombre">{item.nombre}</span>
          <span className="ranking-list__barra" aria-hidden>
            <span style={{ width: `${max > 0 ? ((item.valor ?? 0) / max) * 100 : 0}%` }} />
          </span>
          <strong>{formatValor(item.valor, '')}</strong>
          {item.variacionPct !== null && (
            <span className="ranking-list__variacion" data-tendencia={item.tendencia ?? 'estabilidad'}>
              {item.variacionPct > 0 ? '▲' : item.variacionPct < 0 ? '▼' : '■'}{' '}
              {formatValor(Math.abs(item.variacionPct), '%')}
            </span>
          )}
        </li>
      ))}
    </ol>
  );
}
