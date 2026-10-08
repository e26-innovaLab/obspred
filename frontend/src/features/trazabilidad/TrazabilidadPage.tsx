import { FiltrosBar } from '../../components/common/FiltrosBar';
import { useTrazabilidadData } from './hooks/useTrazabilidadData';
import { FuentesTable } from './components/FuentesTable';

// Vista 5 — Trazabilidad y fuentes.
// Fuente, fecha de actualización y tipo de cada indicador; estado de
// frescura de cada fuente y acceso a la metodología. Filtros: País · Fuente.
export function TrazabilidadPage() {
  const { fuentes } = useTrazabilidadData();

  return (
    <section className="page">
      <h2>Trazabilidad y fuentes</h2>
      <p className="page__descripcion">Consultá el origen, la actualización y la metodología de los datos del observatorio.</p>
      <FiltrosBar mostrarSector={false} mostrarPeriodo={false} />

      <FuentesTable fuentes={fuentes} />
    </section>
  );
}
