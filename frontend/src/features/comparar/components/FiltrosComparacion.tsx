import { INDICADORES, PAISES, SECTORES } from '../../../services/mock/catalogo';
import { SERIE_PAIS } from '../../../styles/paletaMarca';
import type { Pais, Sector } from '../../../types/kpi';

interface Props {
  paises: Pais[];
  sector?: Sector;
  indicador: string;
  onTogglePais: (p: Pais) => void;
  onSector: (s?: Sector) => void;
  onIndicador: (i: string) => void;
}

// Filtros de la vista Comparar: país múltiple (checkbox, como en el Figma de
// Explorar), sector e indicador. Reusa las clases de .filtros-bar.
export function FiltrosComparacion({ paises, sector, indicador, onTogglePais, onSector, onIndicador }: Props) {
  return (
    <div className="filtros-bar" role="group" aria-label="Filtros de comparación">
      <fieldset className="filtros-comparacion__paises">
        <legend>Países</legend>
        {PAISES.map((p) => (
          <label key={p.id} className="filtros-comparacion__pais">
            <input type="checkbox" checked={paises.includes(p.id)} onChange={() => onTogglePais(p.id)} />
            <span className="filtros-comparacion__muestra" style={{ background: SERIE_PAIS[p.id].color }} aria-hidden />
            {p.nombre}
          </label>
        ))}
      </fieldset>

      <label>
        Sector
        <select value={sector ?? ''} onChange={(e) => onSector((e.target.value || undefined) as Sector | undefined)}>
          <option value="">Todos los sectores</option>
          {SECTORES.map((s) => (
            <option key={s.id} value={s.id}>
              {s.nombre}
            </option>
          ))}
        </select>
      </label>

      <label>
        Indicador
        <select value={indicador} onChange={(e) => onIndicador(e.target.value)}>
          {INDICADORES.map((i) => (
            <option key={i.id} value={i.id}>
              {i.nombre}
            </option>
          ))}
        </select>
      </label>
    </div>
  );
}
