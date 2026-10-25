import { useState } from 'react';
import { FiltrosBar } from '../../components/common/FiltrosBar';
import { useTrazabilidadData } from './hooks/useTrazabilidadData';
import { FuentesTable } from './components/FuentesTable';
import { PAISES } from '../../services/mock/catalogo';
import type { Pais } from '../../types/kpi';

const ORDEN_PAISES = PAISES.map((p) => p.id as Pais);

// Vista 5 — Trazabilidad y fuentes.
// Fuente, fecha de actualización y tipo de cada indicador; estado de
// frescura de cada fuente y acceso a la metodología. Filtros: País · Fuente.
export function TrazabilidadPage() {
  const { fuentes } = useTrazabilidadData();

  const [paises, setPaisesLocal] = useState<Pais[]>(ORDEN_PAISES);
  const togglePais = (pais: Pais) =>
    setPaisesLocal((prev) => {
      const nuevos = prev.includes(pais) ? prev.filter((p) => p !== pais) : [...prev, pais];
      return ORDEN_PAISES.filter((p) => nuevos.includes(p));
    });

  return (
    <section className="page">
      <h2>Trazabilidad y fuentes</h2>
      <p className="page__descripcion">Consultá el origen, la actualización y la metodología de los datos del observatorio.</p>
      <FiltrosBar mostrarSector={false} mostrarPeriodo={false} paisesMultiples={{ seleccionados: paises, onToggle: togglePais }} />

      <FuentesTable fuentes={fuentes} />
    </section>
  );
}
