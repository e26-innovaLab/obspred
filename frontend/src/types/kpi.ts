// Tipos base para indicadores del Observatorio Predictivo.
// Regla del proyecto (principio 03/04): todo indicador debe declarar
// fuente, fecha de actualización y tipo (observado / calculado / proyección).

export type TipoIndicador = 'observado' | 'calculado' | 'proyeccion';

export type Pais = 'AR' | 'UY' | 'CL';

export type Sector =
  | 'tecnologia'
  | 'salud'
  | 'energia'
  | 'turismo'
  | 'economia-conocimiento';

export interface Fuente {
  nombre: string;
  fechaActualizacion: string; // ISO date
  estado: 'activa' | 'desactualizada' | 'no-disponible';
  metodologiaUrl?: string;
}

export interface Indicador<T = number> {
  id: string;
  nombre: string;
  valor: T;
  unidad?: string;
  tipo: TipoIndicador;
  fuente: Fuente;
  pais: Pais;
  sector?: Sector;
  ocupacionId?: string;
  periodo: string; // ej. "2026-Q2"
}

// ---- Series y proyecciones (contrato: frontend/docs/contrato-api-graficos.md)

export type Frecuencia = 'anual' | 'trimestral' | 'mensual';

export interface IndicadorCatalogo {
  id: string; // ej. tasa_desempleo
  nombre: string;
  unidad: string; // %, índice, avisos…
}

export interface PuntoSerie {
  periodo: string; // 2024, 2024-Q1 o 2024-01
  valor: number | null; // null = sin dato en la fuente (nunca se inventa)
  tipo: TipoIndicador;
}

export interface SerieTemporal {
  pais: Pais;
  indicador: string;
  nombre: string;
  unidad: string;
  frecuencia: Frecuencia;
  puntos: PuntoSerie[];
  fuentes: Array<{ fuente: Fuente; tipo: TipoIndicador }>;
}

export interface PuntoProyeccion {
  periodo: string;
  valor: number;
  limiteInferior: number;
  limiteSuperior: number;
}

export interface Proyeccion {
  pais: Pais;
  indicador: string;
  unidad: string;
  historico: PuntoSerie[];
  proyeccion: PuntoProyeccion[];
  proyectable: boolean; // false si hay < 3 períodos comparables (principio 05)
  motivoNoProyectable?: string;
  metodo: string;
  nivelConfianza: number; // ej. 0.8
  fuentes: Array<{ fuente: Fuente; tipo: TipoIndicador }>;
}

export interface Filtros {
  pais: Pais;
  sector?: Sector;
  ocupacionId?: string;
  periodo?: string;
}

// ---- Comparativa entre países y mapa de calor (contrato §3.6 y §3.7)

export interface ValorPorPais {
  pais: Pais;
  valor: number | null;
  periodo: string | null; // cada país puede tener su último período distinto
  fuente: { fuente: Fuente; tipo: TipoIndicador } | null;
}

export interface ComparativaIndicador {
  indicador: string;
  nombre: string;
  unidad: string;
  valores: ValorPorPais[];
}

export interface CeldaMapaCalor {
  sector: Sector;
  pais: Pais;
  valor: number | null; // null = la fuente no cubre ese sector en ese país
  variacionPct: number | null;
}

export interface MapaCalor {
  indicador: string;
  nombre: string;
  unidad: string;
  periodo: string;
  sectores: Array<{ id: Sector; nombre: string }>;
  paises: Pais[];
  celdas: CeldaMapaCalor[];
  fuentes: Array<{ fuente: Fuente; tipo: TipoIndicador }>;
}

// ---- Dashboard: tarjetas de KPI y rankings (contrato §3.4 y §3.5)

export type Tendencia = 'crecimiento' | 'estabilidad' | 'caida';

export interface KpiResumen {
  indicador: string;
  nombre: string;
  unidad: string;
  periodo: string | null;
  valor: number | null;
  valorAnterior: number | null;
  variacionPct: number | null;
  tendencia: Tendencia | null;
  /** Para pintar bien la variación: que baje el desempleo es bueno. */
  sentidoPositivo: 'sube' | 'baja';
  sparkline: Array<number | null>; // últimos períodos, para la mini línea
  fuente: { fuente: Fuente; tipo: TipoIndicador };
}

export type DimensionRanking = 'sector' | 'ocupacion' | 'habilidad';

export interface RankingItem {
  id: string;
  nombre: string;
  valor: number | null;
  variacionPct: number | null;
  tendencia: Tendencia | null;
}

export interface Ranking {
  dimension: DimensionRanking;
  indicador: string;
  unidad: string;
  periodo: string;
  items: RankingItem[];
  fuentes: Array<{ fuente: Fuente; tipo: TipoIndicador }>;
}

// ---- Tendencias: cambios significativos marcados sobre la serie (contrato §3.10)

export interface CambioSignificativo {
  id: string;
  pais: Pais;
  indicador: string;
  periodo: string; // período donde se detectó el cambio
  variacionPct: number;
  nivel: 'alto' | 'medio' | 'bajo';
  titulo: string;
  descripcion: string;
}
