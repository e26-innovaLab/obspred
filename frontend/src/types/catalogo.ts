import type { Pais, Sector } from './kpi';

// Catálogos de referencia (Sprint 0): 3 países, 5 sectores, ~20 ocupaciones.
export interface PaisInfo {
  id: Pais;
  nombre: string;
}

export interface SectorInfo {
  id: Sector;
  nombre: string;
}

export interface Ocupacion {
  id: string;
  nombre: string;
  sector: Sector;
}

export interface Periodo {
  id: string; // ej. "2026-Q2"
  label: string; // ej. "2do trimestre 2026"
}
