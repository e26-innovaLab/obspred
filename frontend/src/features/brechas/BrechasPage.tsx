import { useState } from 'react';
import { FiltrosBar } from '../../components/common/FiltrosBar';
import { useBrechasData } from './hooks/useBrechasData';
import { BrechasChart } from './components/BrechasChart';
import { HabilidadesEmergentesList } from './components/HabilidadesEmergentesList';
import { PAISES } from '../../services/mock/catalogo';
import type { Pais, Ranking } from '../../types/kpi';
import { useInforme } from '../../store/useInforme';
import { useFiltros } from '../../store/useFiltros';

const ORDEN_PAISES = PAISES.map((p) => p.id as Pais);

export function BrechasPage() {
  const { habilidades, emergentes } = useBrechasData();
  const informe = useInforme();
  const { filtros } = useFiltros();

  const [paises, setPaisesLocal] = useState<Pais[]>(ORDEN_PAISES);
  const togglePais = (pais: Pais) =>
    setPaisesLocal((prev) => {
      const nuevos = prev.includes(pais) ? prev.filter((p) => p !== pais) : [...prev, pais];
      return ORDEN_PAISES.filter((p) => nuevos.includes(p));
    });

  const fechaGuardado = new Date().toLocaleDateString('es-AR', {
    day: '2-digit', month: 'long', year: 'numeric',
  });

  // ---- Guardar demanda vs. oferta ----
  const idBrechas = 'brechas-demanda-oferta';
  const guardadoBrechas = informe.estaGuardado(idBrechas);
  const handleGuardarBrechas = () => {
    if (guardadoBrechas) { informe.quitar(idBrechas); return; }
    const datos: Ranking = {
      dimension: 'habilidad',
      indicador: 'demanda_vs_oferta',
      unidad: 'puntaje',
      periodo: filtros.periodo ?? '',
      items: habilidades.map((h) => ({
        id: h.habilidad,
        nombre: h.habilidad,
        valor: h.demanda,
        variacionPct: null,
        tendencia: null,
      })),
      fuentes: [],
    };
    informe.guardar({
      id: idBrechas,
      titulo: 'Demanda vs. oferta formativa',
      descripcion: 'Puntaje de demanda del mercado por habilidad',
      contenido: { tipo: 'ranking', datos },
      fuentes: [],
      filtros,
      fechaGuardado,
    });
  };

  // ---- Guardar habilidades emergentes ----
  const idEmergentes = 'brechas-emergentes';
  const guardadoEmergentes = informe.estaGuardado(idEmergentes);
  const handleGuardarEmergentes = () => {
    if (guardadoEmergentes) { informe.quitar(idEmergentes); return; }
    const datos: Ranking = {
      dimension: 'habilidad',
      indicador: 'habilidades_emergentes',
      unidad: 'puntaje',
      periodo: filtros.periodo ?? '',
      items: emergentes.map((h) => ({
        id: h.habilidad,
        nombre: h.habilidad,
        valor: h.demanda,
        variacionPct: null,
        tendencia: null,
      })),
      fuentes: [],
    };
    informe.guardar({
      id: idEmergentes,
      titulo: 'Habilidades emergentes',
      descripcion: 'Habilidades con alta demanda emergente en el mercado',
      contenido: { tipo: 'ranking', datos },
      fuentes: [],
      filtros,
      fechaGuardado,
    });
  };

  return (
    <section className="page">
      <h2>Brechas de habilidades</h2>
      <p className="page__descripcion">Comparás la demanda de habilidades del mercado con la oferta formativa disponible.</p>
      <FiltrosBar mostrarSector mostrarOcupacion mostrarPeriodo={false} paisesMultiples={{ seleccionados: paises, onToggle: togglePais }} />

      <article className="chart-card">
        <header className="chart-card__header">
          <div>
            <h3>Demanda vs. oferta formativa</h3>
          </div>
          <div className="chart-card__header-acciones">
            <button
              type="button"
              className={`chart-card__btn-guardar${guardadoBrechas ? ' chart-card__btn-guardar--activo' : ''}`}
              onClick={handleGuardarBrechas}
              aria-pressed={guardadoBrechas}
              title={guardadoBrechas ? 'Quitar del informe' : 'Guardar en mi informe'}
            >
              {guardadoBrechas ? '✓ Guardado' : '＋ Mi informe'}
            </button>
          </div>
        </header>
        <div className="chart-card__cuerpo">
          <BrechasChart habilidades={habilidades} />
        </div>
      </article>

      <article className="chart-card" style={{ marginTop: '1.25rem' }}>
        <header className="chart-card__header">
          <div>
            <h3>Habilidades emergentes</h3>
          </div>
          <div className="chart-card__header-acciones">
            <button
              type="button"
              className={`chart-card__btn-guardar${guardadoEmergentes ? ' chart-card__btn-guardar--activo' : ''}`}
              onClick={handleGuardarEmergentes}
              aria-pressed={guardadoEmergentes}
              title={guardadoEmergentes ? 'Quitar del informe' : 'Guardar en mi informe'}
            >
              {guardadoEmergentes ? '✓ Guardado' : '＋ Mi informe'}
            </button>
          </div>
        </header>
        <div className="chart-card__cuerpo">
          <HabilidadesEmergentesList emergentes={emergentes} />
        </div>
      </article>
    </section>
  );
}
