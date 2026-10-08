import { FiltrosBar } from '../../components/common/FiltrosBar';
import { KpiCard } from '../../components/common/KpiCard';
import { useDashboardData } from '../dashboard/hooks/useDashboardData';

// Vista de Detalle
export function DetailPage() {
  // Reutilizamos temporalmente los indicadores del hook de dashboard
  const { indicadores } = useDashboardData();

  return (
    <section className="page">
      <h2>Detalle</h2>
      <p className="text-muted">Información detallada del elemento seleccionado.</p>

      {/* Filtros  */}
      <FiltrosBar mostrarSector mostrarPeriodo />

      {/* Título */}
      <div className="detail__header my-4">
        <h3>Título</h3>
        <p className="text-muted">Contexto</p>
      </div>

      {/*Indicadores principales*/}
      <div className="kpi-grid">
        {indicadores.map((i) => (
          <KpiCard key={i.id} indicador={i} />
        ))}
      </div>

      {/*Evolución de la Demanda */}
      <div className="detail__section my-6">
        <h3>Evolución de la Demanda</h3>
        <span className="text-muted text-sm">Variación temporal</span>
        <div className="border rounded p-8 text-center my-3 text-muted">
          [ aqui va el gráfico de líneas ]
        </div>
      </div>

      {/* Habilidades */}
      <div className="detail__section my-6">
        <h3>Habilidades</h3>
        <ul className="divide-y border-t border-b my-2">
          {[1, 2, 3, 4, 5].map((item) => (
            <li key={item} className="flex justify-between py-2 text-sm">
              <span>Elemento {item}</span>
              <span className="text-muted">valor o cantidad</span>
            </li>
          ))}
        </ul>
      </div>

      {/*Formación y Brecha */}
      <div className="detail__section my-6">
        <h3>Formación y brecha</h3>
        <div className="page__columns grid grid-cols-1 md:grid-cols-2 gap-6 mt-3">
          <div>
            <h4 className="font-semibold text-sm mb-2">Formación Requerida</h4>
            <ul className="divide-y">
              {[1, 2, 3, 4].map((item) => (
                <li key={item} className="flex justify-between py-1.5 text-sm">
                  <span>Elemento {item}</span>
                  <span className="text-muted">valor o cantidad</span>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-sm mb-2">Brecha requerida</h4>
            <ul className="divide-y">
              {[1, 2, 3, 4].map((item) => (
                <li key={item} className="flex justify-between py-1.5 text-sm">
                  <span>Elemento {item}</span>
                  <span className="text-muted">valor o cantidad</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/*Fuentes y Metodología */}
      <div className="detail__section pt-6 border-t mt-8">
        <h3>Fuentes y metodología</h3>
        <div className="page__columns grid grid-cols-1 md:grid-cols-2 gap-4 my-3 text-sm">
          <div>
            <strong className="block">Fuente</strong>
            <span className="text-muted">Nombre de la fuente</span>
          </div>
          <div>
            <strong className="block">Última actualización</strong>
            <span className="text-muted">Fecha</span>
          </div>
        </div>
        <div className="text-sm mt-3">
          <strong className="block">Metodología</strong>
          <p className="text-muted">Descripción breve de cómo se obtienen/interpretan los datos</p>
        </div>
      </div>
    </section>
  );
}