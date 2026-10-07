import type { Fuente, TipoIndicador } from '../../types/kpi';

interface Props {
  fuente: Fuente;
  tipo: TipoIndicador;
}

const TIPO_LABEL: Record<TipoIndicador, string> = {
  observado: 'Observado',
  calculado: 'Calculado',
  proyeccion: 'Proyección',
};

// Componente compartido: muestra fuente + fecha + tipo de indicador.
// Principio 03 del roadmap: "Cada indicador en pantalla muestra su fuente,
// fecha y tipo. Sin excepción."
export function FuenteBadge({ fuente, tipo }: Props) {
  return (
    <span className="fuente-badge" data-estado={fuente.estado}>
      <strong>{TIPO_LABEL[tipo]}</strong> · {fuente.nombre} ·{' '}
      {new Date(fuente.fechaActualizacion).toLocaleDateString('es-AR')}
    </span>
  );
}
