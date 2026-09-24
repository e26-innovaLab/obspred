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

export interface Filtros {
  pais: Pais;
  sector?: Sector;
  ocupacionId?: string;
  periodo?: string;
}
