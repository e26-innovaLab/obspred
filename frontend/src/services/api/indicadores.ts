import { apiGet, ISO3_A_PAIS, PAIS_A_ISO3 } from './client';
import type {
  ComparativaIndicador,
  Filtros,
  Fuente,
  Indicador,
  MapaCalor,
  Pais,
  Proyeccion,
  PuntoSerie,
  Sector,
  SerieTemporal,
  TipoIndicador,
} from '../../types/kpi';

// Servicio de acceso a indicadores. Contrato completo:
// frontend/docs/contrato-api-graficos.md

// ---- DTO: forma exacta del JSON del Backend (snake_case, ISO3) ----

interface FuenteDto {
  fuente: string;
  fecha_actualizacion: string; // YYYY-MM-DD
  estado_fuente: 'activa' | 'desactualizada' | 'no_disponible';
  tipo: TipoIndicador;
  metodologia_url?: string | null;
}

interface SerieDto {
  pais: string;
  indicador: string;
  nombre: string;
  unidad: string;
  frecuencia: SerieTemporal['frecuencia'];
  puntos: PuntoSerie[];
  fuentes: FuenteDto[];
}

interface ProyeccionDto {
  pais: string;
  indicador: string;
  unidad: string;
  historico: PuntoSerie[];
  proyeccion: Array<{ periodo: string; valor: number; limite_inferior: number; limite_superior: number }>;
  proyectable: boolean;
  motivo_no_proyectable: string | null;
  metodo: string;
  nivel_confianza: number;
  fuentes: FuenteDto[];
}

function mapFuente(f: FuenteDto): { fuente: Fuente; tipo: TipoIndicador } {
  return {
    tipo: f.tipo,
    fuente: {
      nombre: f.fuente,
      fechaActualizacion: f.fecha_actualizacion,
      estado: f.estado_fuente === 'no_disponible' ? 'no-disponible' : f.estado_fuente,
      metodologiaUrl: f.metodologia_url ?? undefined,
    },
  };
}

function filtrosAQuery(f: Filtros, paises: Filtros['pais'][] = [f.pais]) {
  return {
    pais: paises.map((p) => PAIS_A_ISO3[p]).join(','),
    sector: f.sector,
    ocupacion: f.ocupacionId,
  };
}

// ---- Endpoints ----

/** GET /indicadores — ya existe en Backend (lista plana, un registro por dato). */
export async function getIndicadores(filtros: Filtros, signal?: AbortSignal): Promise<Indicador[]> {
  return apiGet<Indicador[]>('/indicadores', filtrosAQuery(filtros), signal);
}

/** GET /metricas/series — una serie por país, lista para graficar. */
export async function getSeries(
  indicador: string,
  filtros: Filtros,
  signal?: AbortSignal,
  paises?: Filtros['pais'][],
): Promise<SerieTemporal[]> {
  const data = await apiGet<{ series: SerieDto[] }>(
    '/metricas/series',
    { indicador, ...filtrosAQuery(filtros, paises) },
    signal,
  );
  return data.series.map((s) => ({ ...s, pais: ISO3_A_PAIS[s.pais], fuentes: s.fuentes.map(mapFuente) }));
}

/** GET /metricas/proyecciones — histórico + proyección con banda de confianza. */
export async function getProyeccion(
  indicador: string,
  filtros: Filtros,
  signal?: AbortSignal,
  horizonte = 2,
): Promise<Proyeccion> {
  const p = await apiGet<ProyeccionDto>(
    '/metricas/proyecciones',
    { indicador, horizonte, ...filtrosAQuery(filtros) },
    signal,
  );
  return {
    pais: ISO3_A_PAIS[p.pais],
    indicador: p.indicador,
    unidad: p.unidad,
    historico: p.historico,
    proyeccion: p.proyeccion.map((x) => ({
      periodo: x.periodo,
      valor: x.valor,
      limiteInferior: x.limite_inferior,
      limiteSuperior: x.limite_superior,
    })),
    proyectable: p.proyectable,
    motivoNoProyectable: p.motivo_no_proyectable ?? undefined,
    metodo: p.metodo,
    nivelConfianza: p.nivel_confianza,
    fuentes: p.fuentes.map(mapFuente),
  };
}

// ---- Comparativa entre países y mapa de calor ----

interface ComparativaDto {
  indicadores: Array<{
    indicador: string;
    nombre: string;
    unidad: string;
    valores: Array<{ pais: string; valor: number | null; periodo: string | null; fuente: FuenteDto | null }>;
  }>;
}

interface MapaCalorDto {
  indicador: string;
  nombre: string;
  unidad: string;
  periodo: string;
  filas: Array<{ id: Sector; nombre: string }>;
  columnas: string[]; // ISO3
  celdas: Array<{ fila: Sector; columna: string; valor: number | null; variacion_pct: number | null }>;
  fuentes: FuenteDto[];
}

/** GET /metricas/comparativa — último valor de cada país por indicador. */
export async function getComparativa(
  indicadores: string[],
  paises: Pais[],
  sector: Sector | undefined,
  signal?: AbortSignal,
): Promise<ComparativaIndicador[]> {
  const data = await apiGet<ComparativaDto>(
    '/metricas/comparativa',
    { indicadores: indicadores.join(','), pais: paises.map((p) => PAIS_A_ISO3[p]).join(','), sector },
    signal,
  );
  return data.indicadores.map((i) => ({
    ...i,
    valores: i.valores.map((v) => ({
      pais: ISO3_A_PAIS[v.pais],
      valor: v.valor,
      periodo: v.periodo,
      fuente: v.fuente ? mapFuente(v.fuente) : null,
    })),
  }));
}

/** GET /metricas/mapa-calor — matriz sector × país de un indicador. */
export async function getMapaCalor(indicador: string, paises: Pais[], signal?: AbortSignal): Promise<MapaCalor> {
  const d = await apiGet<MapaCalorDto>(
    '/metricas/mapa-calor',
    { indicador, filas: 'sector', pais: paises.map((p) => PAIS_A_ISO3[p]).join(',') },
    signal,
  );
  return {
    indicador: d.indicador,
    nombre: d.nombre,
    unidad: d.unidad,
    periodo: d.periodo,
    sectores: d.filas,
    paises: d.columnas.map((c) => ISO3_A_PAIS[c]),
    celdas: d.celdas.map((c) => ({
      sector: c.fila,
      pais: ISO3_A_PAIS[c.columna],
      valor: c.valor,
      variacionPct: c.variacion_pct,
    })),
    fuentes: d.fuentes.map(mapFuente),
  };
}
