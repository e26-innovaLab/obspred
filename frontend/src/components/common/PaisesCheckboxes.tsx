import { PAISES } from '../../services/mock/catalogo';
import { SERIE_PAIS } from '../../styles/paletaMarca';
import type { Pais } from '../../types/kpi';

interface Props {
  seleccionados: Pais[];
  onToggle: (pais: Pais) => void;
}

// Selección múltiple de países con su color de serie, para comparar.
// Compartido: lo usan Comparar países y Ocupaciones (AGENTS.md, principio 7).
export function PaisesCheckboxes({ seleccionados, onToggle }: Props) {
  return (
    <fieldset className="filtros-comparacion__paises">
      <legend>Países</legend>
      {PAISES.map((p) => {
        const checked = seleccionados.includes(p.id);
        return (
          <label
            key={p.id}
            className="filtros-comparacion__pais"
            style={{ '--color-pais': SERIE_PAIS[p.id].color } as React.CSSProperties}
          >
            <input
              type="checkbox"
              checked={checked}
              onChange={() => onToggle(p.id)}
              className="filtros-comparacion__input-oculto"
            />
            <span
              className="filtros-comparacion__muestra"
              data-checked={checked}
              aria-hidden
            />
            {p.nombre}
          </label>
        );
      })}
    </fieldset>
  );
}
