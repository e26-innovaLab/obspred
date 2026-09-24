import { useFiltros } from '../../store/useFiltros';
import { PAISES, SECTORES, PERIODOS, ocupacionesPorSector } from '../../services/mock/catalogo';

interface Props {
  // Cada vista muestra solo los filtros que sus KPIs necesitan
  // (principio del roadmap: "los filtros de Sector y Ocupación se activan
  // solo cuando el KPI los requiere").
  mostrarSector?: boolean;
  mostrarOcupacion?: boolean;
  mostrarPeriodo?: boolean;
}

export function FiltrosBar({ mostrarSector = true, mostrarOcupacion = false, mostrarPeriodo = true }: Props) {
  const { filtros, setPais, setSector, setOcupacionId, setPeriodo } = useFiltros();
  const ocupacionesDisponibles = ocupacionesPorSector(filtros.sector);

  return (
    <div className="filtros-bar" role="group" aria-label="Filtros del Observatorio">
      <label>
        País
        <select value={filtros.pais} onChange={(e) => setPais(e.target.value as typeof filtros.pais)}>
          {PAISES.map((p) => (
            <option key={p.id} value={p.id}>
              {p.nombre}
            </option>
          ))}
        </select>
      </label>

      {mostrarSector && (
        <label>
          Sector
          <select
            value={filtros.sector ?? ''}
            onChange={(e) => setSector((e.target.value || undefined) as typeof filtros.sector)}
          >
            <option value="">Todos los sectores</option>
            {SECTORES.map((s) => (
              <option key={s.id} value={s.id}>
                {s.nombre}
              </option>
            ))}
          </select>
        </label>
      )}

      {mostrarOcupacion && (
        <label>
          Ocupación
          <select
            value={filtros.ocupacionId ?? ''}
            onChange={(e) => setOcupacionId(e.target.value || undefined)}
          >
            <option value="">Todas las ocupaciones</option>
            {ocupacionesDisponibles.map((o) => (
              <option key={o.id} value={o.id}>
                {o.nombre}
              </option>
            ))}
          </select>
        </label>
      )}

      {mostrarPeriodo && (
        <label>
          Período
          <select value={filtros.periodo ?? ''} onChange={(e) => setPeriodo(e.target.value)}>
            {PERIODOS.map((p) => (
              <option key={p.id} value={p.id}>
                {p.label}
              </option>
            ))}
          </select>
        </label>
      )}
    </div>
  );
}
