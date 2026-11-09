import type { PasoCarga } from '../types';

interface Props {
  pasoActual: PasoCarga;
  total?: number;
}

// Barra de progreso de 4 pasos, igual al diseño de UX.
export function ProgresoPasos({ pasoActual, total = 4 }: Props) {
  return (
    <div className="progreso-pasos" aria-label={`Paso ${pasoActual} de ${total}`}>
      <p className="progreso-pasos__label">PASO {pasoActual} DE {total}</p>
      <div className="progreso-pasos__barra" role="progressbar" aria-valuenow={pasoActual} aria-valuemin={1} aria-valuemax={total}>
        {Array.from({ length: total }, (_, i) => (
          <div
            key={i}
            className={`progreso-pasos__segmento ${i + 1 <= pasoActual ? 'progreso-pasos__segmento--activo' : ''}`}
          />
        ))}
      </div>
    </div>
  );
}
