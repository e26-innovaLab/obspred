import type { TendenciaSector } from '../../../services/mock/dashboard';

const ESTADO_LABEL: Record<TendenciaSector['estado'], string> = {
  crecimiento: '▲ Crecimiento',
  estabilidad: '▬ Estabilidad',
  caida: '▼ Caída',
};

export function TendenciaSectorList({ tendencias }: { tendencias: TendenciaSector[] }) {
  return (
    <ul className="tendencia-sector-list">
      {tendencias.map((t) => (
        <li key={t.sector} data-estado={t.estado}>
          <span>{t.sectorNombre}</span>
          <span>{ESTADO_LABEL[t.estado]}</span>
        </li>
      ))}
    </ul>
  );
}
