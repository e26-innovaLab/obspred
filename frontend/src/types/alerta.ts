import type { Pais, Sector } from './kpi';

export type NivelAlerta = 'alto' | 'medio' | 'bajo';

export interface Alerta {
  id: string;
  titulo: string;
  descripcion: string;
  nivel: NivelAlerta;
  fecha: string; // ISO date
  pais: Pais;
  sector?: Sector;
}
