import { FiltrosBar } from '../../components/common/FiltrosBar';
import { useBrechasData } from './hooks/useBrechasData';
import { BrechasChart } from './components/BrechasChart';
import { HabilidadesEmergentesList } from './components/HabilidadesEmergentesList';

// Vista 4 — Brechas de habilidades.
// Comparación entre demanda del mercado y oferta formativa disponible, y
// habilidades emergentes. Filtros activos: País · Sector · Ocupación.
export function BrechasPage() {
  const { habilidades, emergentes } = useBrechasData();

  return (
    <section className="page">
      <h2>Brechas de habilidades</h2>
      <p className="page__descripcion">Compará la demanda de habilidades del mercado con la oferta formativa disponible.</p>
      <FiltrosBar mostrarSector mostrarOcupacion mostrarPeriodo={false} />

      <h3>Demanda vs. oferta formativa</h3>
      <BrechasChart habilidades={habilidades} />

      <h3>Habilidades emergentes</h3>
      <HabilidadesEmergentesList emergentes={emergentes} />
    </section>
  );
}
