import { useState } from "react";
import { FiltrosBar } from "../../components/common/FiltrosBar";
import { useTrazabilidadData } from "./hooks/useTrazabilidadData";
import { FuentesTable } from "./components/FuentesTable";
import { PAISES } from "../../services/mock/catalogo";
import type { Pais } from "../../types/kpi";

const ORDEN_PAISES = PAISES.map((p) => p.id as Pais);

// Vista 5 — Trazabilidad y fuentes.
// Fuente, fecha de actualización y tipo de cada indicador; estado de
// frescura de cada fuente y acceso a la metodología. Filtros: País · Fuente.
export function TrazabilidadPage() {
  const { fuentes } = useTrazabilidadData();

  const [paises, setPaisesLocal] = useState<Pais[]>(ORDEN_PAISES);
  const togglePais = (pais: Pais) =>
    setPaisesLocal((prev) => {
      const nuevos = prev.includes(pais)
        ? prev.filter((p) => p !== pais)
        : [...prev, pais];
      return ORDEN_PAISES.filter((p) => nuevos.includes(p));
    });

  return (
    <section className="page">
      <h2>Trazabilidad y fuentes</h2>
      <p className="page__descripcion">
        Conocé el origen, la cobertura y los límites de los datos de Faro.
      </p>
      <FiltrosBar
        mostrarSector={false}
        mostrarPeriodo={false}
        paisesMultiples={{ seleccionados: paises, onToggle: togglePais }}
      />

      <section className="coverage-section">
        <h2>Cobertura de datos</h2>
        <div className="kpi-grid">
          <div className="kpi-card kpi-card--azul">
            <p className="kpi-label">PAÍSES</p>
            <p className="kpi-value">3</p>
            <p className="kpi-description">Argentina · Uruguay · Chile</p>
          </div>
          <div className="kpi-card kpi-card--verde">
            <p className="kpi-label">SECTORES</p>
            <p className="kpi-value">5</p>
            <p className="kpi-description">Áreas priorizadas por Faro</p>
          </div>
          <div className="kpi-card kpi-card--amarillo">
            <p className="kpi-label">INDICADORES</p>
            <p className="kpi-value">4</p>
            <p className="kpi-description">Definiciones por validar</p>
          </div>
          <div className="kpi-card kpi-card--gris">
            <p className="kpi-label">PERÍODO</p>
            <p className="kpi-value">Por fuente</p>
            <p className="kpi-description">Disponibilidad variable</p>
          </div>
        </div>
      </section>

      <section className="fuentes-section">
        <h2>Catálogo de fuentes</h2>
        <div className="fuentes-table-container">
          <FuentesTable fuentes={fuentes} />
        </div>
      </section>
    </section>
  );
}
