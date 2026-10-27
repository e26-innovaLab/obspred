import { useState } from 'react';
import { FiltrosBar } from '../../components/common/FiltrosBar';
import { useBrechasData } from './hooks/useBrechasData';
import { BrechasChart } from './components/BrechasChart';
import { HabilidadesEmergentesList } from './components/HabilidadesEmergentesList';
import { PAISES } from '../../services/mock/catalogo';
import type { Pais } from '../../types/kpi';

const ORDEN_PAISES = PAISES.map((p) => p.id as Pais);

// Vista 4 — Brechas de habilidades.
// Comparación entre demanda del mercado y oferta formativa disponible, y
// habilidades emergentes. Filtros activos: País · Sector · Ocupación.
export function BrechasPage() {
  const { habilidades, emergentes } = useBrechasData();

  const [paises, setPaisesLocal] = useState<Pais[]>(ORDEN_PAISES);
  const togglePais = (pais: Pais) =>
    setPaisesLocal((prev) => {
      const nuevos = prev.includes(pais) ? prev.filter((p) => p !== pais) : [...prev, pais];
      return ORDEN_PAISES.filter((p) => nuevos.includes(p));
    });

  return (
    <section className="page">
      <h2>Brechas de habilidades</h2>
      <p className="page__descripcion">Compará la demanda de habilidades del mercado con la oferta formativa disponible.</p>
      <FiltrosBar mostrarSector mostrarOcupacion mostrarPeriodo={false} paisesMultiples={{ seleccionados: paises, onToggle: togglePais }} />

      <h3>Demanda vs. oferta formativa</h3>
      <BrechasChart habilidades={habilidades} />

      <h3>Habilidades emergentes</h3>
      <HabilidadesEmergentesList emergentes={emergentes} />
    </section>
  );
}
