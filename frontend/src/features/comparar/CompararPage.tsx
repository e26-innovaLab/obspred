import { INDICADORES } from '../../services/mock/catalogo';
import { ChartCard } from '../../components/charts/ChartCard';
import { SerieHistoricaChart } from '../../components/charts/SerieHistoricaChart';
import { SinDatos } from '../../components/common/SinDatos';
import { formatPeriodo } from '../../components/charts/series';
import { FiltrosComparacion } from './components/FiltrosComparacion';
import { ComparativaCards } from './components/ComparativaCards';
import { MapaCalorGrid } from './components/MapaCalorGrid';
import { useComparacionData, useFiltrosComparacion } from './hooks/useComparacion';

// Vista Comparar países (Figma: "Comparar" / "Explorar").
// 1) Indicadores comparativos: último valor de cada país.
// 2) Evolución: una línea por país para el indicador elegido.
// 3) Mapa de calor: el indicador elegido por sector × país.
export function CompararPage() {
  const f = useFiltrosComparacion();

  return (
    <section className="page">
      <h2>Comparar países</h2>
      <p>Compará indicadores del mercado laboral entre Argentina, Uruguay y Chile.</p>

      <FiltrosComparacion
        paises={f.paises}
        sector={f.sector}
        indicador={f.indicador}
        onTogglePais={f.togglePais}
        onSector={f.setSector}
        onIndicador={f.setIndicador}
      />

      {f.paises.length === 0 ? (
        <SinDatos mensaje="Seleccioná uno o más países para comenzar a comparar." />
      ) : (
        <Contenido paises={f.paises} sector={f.sector} indicador={f.indicador} />
      )}
    </section>
  );
}

function Contenido({ paises, sector, indicador }: Pick<ReturnType<typeof useFiltrosComparacion>, 'paises' | 'sector' | 'indicador'>) {
  const { comparativa, series, mapaCalor } = useComparacionData(paises, sector, indicador);
  const nombre = INDICADORES.find((i) => i.id === indicador)?.nombre ?? '';

  return (
    <>
      <ChartCard
        titulo="Indicadores comparativos"
        descripcion="Último dato disponible de cada país"
        estado={comparativa.state}
        onRetry={comparativa.retry}
        altura={160}
        fuentes={(data) => data.flatMap((i) => i.valores.flatMap((v) => (v.fuente ? [v.fuente] : [])))}
      >
        {(data) => <ComparativaCards indicadores={data} />}
      </ChartCard>

      <ChartCard
        titulo="Comparación de indicadores"
        descripcion={`${nombre} · una línea por país`}
        estado={series.state}
        onRetry={series.retry}
        fuentes={(s) => s.flatMap((x) => x.fuentes)}
      >
        {(s) => <SerieHistoricaChart series={s} />}
      </ChartCard>

      <ChartCard
        titulo="Mapa de calor por sector"
        descripcion={
          mapaCalor.state.status === 'success'
            ? `${nombre} · ${formatPeriodo(mapaCalor.state.data.periodo)} · más oscuro = valor más alto`
            : nombre
        }
        estado={mapaCalor.state}
        onRetry={mapaCalor.retry}
        altura={300}
        fuentes={(m) => m.fuentes}
      >
        {(m) => <MapaCalorGrid mapa={m} />}
      </ChartCard>
    </>
  );
}
