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
      {/* <FiltrosBar
        mostrarSector={false}
        mostrarPeriodo={false}
        paisesMultiples={{ seleccionados: paises, onToggle: togglePais }}
      /> */}
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

      <section className="metodologia-grid">
        <div className="metodologia-card">
          <h2>Cómo se construyen los indicadores</h2>
          <div className="metodologia-paso">
            <p className="metodologia-paso__titulo">Definición</p>
            <p className="metodologia-paso__descripcion">Precisar qué mide cada indicador y su unidad.</p>
          </div>
          <div className="metodologia-paso">
            <p className="metodologia-paso__titulo">Normalización</p>
            <p className="metodologia-paso__descripcion">Documentar escalas y reglas para comparar países.</p>
          </div>
          <div className="metodologia-paso">
            <p className="metodologia-paso__titulo">Cálculo</p>
            <p className="metodologia-paso__descripcion">Registrar fórmula, período y tratamiento de faltantes.</p>
          </div>
          <div className="metodologia-paso">
            <p className="metodologia-paso__titulo">Actualización</p>
            <p className="metodologia-paso__descripcion">Indicar frecuencia y fecha de última revisión.</p>
          </div>
        </div>
        <div className="metodologia-card">
           <h2>Calidad, comparabilidad y límites</h2>
           <div className="metodologia-item">
            <p className="metodologia-item__titulo">Cobertura desigual</p>
            <p className="metodologia-item__descripcion">Los países pueden publicar datos con distinta periodicidad.</p>
           </div>
           <div className="metodologia-item">
            <p className="metodologia-item__titulo">Definiciones diferentes</p>
            <p className="metodologia-item__descripcion">Validar equivalencias antes de comparar indicadores.</p>
           </div>
           <div className="metodologia-item">
            <p className="metodologia-item__titulo">Datos faltantes</p>
            <p className="metodologia-item__descripcion">Documentar vacíos, estimaciones y decisiones de tratamiento.</p>
           </div>
        </div>

        <div className="metodologia-card metodologia-card--full">
          <h2>Trazabilidad y revisión</h2>
          <p>Cada indicador debería enlazar a su fuente original, fecha de consulta, metodología y versión del dato.</p>
        </div>
      </section>
    </section>
  );
}
