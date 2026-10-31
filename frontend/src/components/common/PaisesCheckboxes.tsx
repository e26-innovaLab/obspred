import { PAISES } from "../../services/mock/catalogo";
import { SERIE_PAIS } from "../../styles/paletaMarca";
import type { Pais } from "../../types/kpi";
import { AR, UY, CL } from "country-flag-icons/react/3x2";

{
  /* <AR title="Argentina" />
<UY title="Uruguay" />
<CL title="Chile" /> */
}

const BANDERAS = {
  AR: AR,
  UY: UY,
  CL: CL,
} as const;

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
        const Bandera = BANDERAS[p.id];
        return (
          <label
            key={p.id}
            className="filtros-comparacion__pais"
          >
            <input
              type="checkbox"
              checked={checked}
              onChange={() => onToggle(p.id)}
            />

            <Bandera
              className="filtros-comparacion__bandera"
              title={p.nombre}
              aria-hidden="true"
            />

            {p.nombre}
          </label>)
      })}
    </fieldset>
  );
}
