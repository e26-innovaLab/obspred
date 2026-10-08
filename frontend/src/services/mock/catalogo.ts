import type { PaisInfo, SectorInfo, Ocupacion, Periodo } from '../../types/catalogo';
import type { IndicadorCatalogo } from '../../types/kpi';

// Catálogo estático del MVP (Sprint 0): 3 países, 5 sectores, ~20 ocupaciones.
// Cuando exista la API interna, este archivo se reemplaza por una consulta
// a GET /catalogo (paso 4 del roadmap: "el contrato de API se acuerda con
// Frontend en la Semana 0 antes de buildear").

export const PAISES: PaisInfo[] = [
  { id: 'AR', nombre: 'Argentina' },
  { id: 'UY', nombre: 'Uruguay' },
  { id: 'CL', nombre: 'Chile' },
];

export const SECTORES: SectorInfo[] = [
  { id: 'tecnologia', nombre: 'Tecnología' },
  { id: 'salud', nombre: 'Salud' },
  { id: 'energia', nombre: 'Energía' },
  { id: 'turismo', nombre: 'Turismo' },
  { id: 'economia-conocimiento', nombre: 'Economía del conocimiento' },
];

export const OCUPACIONES: Ocupacion[] = [
  { id: 'dev-software', nombre: 'Desarrollador/a de software', sector: 'tecnologia' },
  { id: 'analista-datos', nombre: 'Analista de datos', sector: 'tecnologia' },
  { id: 'soporte-ti', nombre: 'Soporte técnico TI', sector: 'tecnologia' },
  { id: 'diseno-ux', nombre: 'Diseñador/a UX/UI', sector: 'tecnologia' },
  { id: 'enfermeria', nombre: 'Enfermería', sector: 'salud' },
  { id: 'tecnico-laboratorio', nombre: 'Técnico/a de laboratorio', sector: 'salud' },
  { id: 'kinesiologia', nombre: 'Kinesiología', sector: 'salud' },
  { id: 'gestion-hospitalaria', nombre: 'Gestión hospitalaria', sector: 'salud' },
  { id: 'tecnico-energias-renovables', nombre: 'Técnico/a en energías renovables', sector: 'energia' },
  { id: 'ingenieria-electrica', nombre: 'Ingeniería eléctrica', sector: 'energia' },
  { id: 'operador-planta', nombre: 'Operador/a de planta energética', sector: 'energia' },
  { id: 'guia-turistico', nombre: 'Guía turístico/a', sector: 'turismo' },
  { id: 'gestion-hotelera', nombre: 'Gestión hotelera', sector: 'turismo' },
  { id: 'chef-gastronomia', nombre: 'Gastronomía / Chef', sector: 'turismo' },
  { id: 'marketing-turistico', nombre: 'Marketing turístico', sector: 'turismo' },
  { id: 'investigador-i+d', nombre: 'Investigador/a I+D', sector: 'economia-conocimiento' },
  { id: 'consultor-innovacion', nombre: 'Consultor/a de innovación', sector: 'economia-conocimiento' },
  { id: 'propiedad-intelectual', nombre: 'Especialista en propiedad intelectual', sector: 'economia-conocimiento' },
  { id: 'analista-financiero', nombre: 'Analista financiero/a', sector: 'economia-conocimiento' },
  { id: 'gestion-proyectos', nombre: 'Gestión de proyectos', sector: 'economia-conocimiento' },
];

export const PERIODOS: Periodo[] = [
  { id: '2025-Q3', label: '3er trimestre 2025' },
  { id: '2025-Q4', label: '4to trimestre 2025' },
  { id: '2026-Q1', label: '1er trimestre 2026' },
  { id: '2026-Q2', label: '2do trimestre 2026' },
];

// Indicadores graficables (a confirmar con Data — principio 01).
// Cuando exista GET /catalogo, la lista llega del Backend.
export const INDICADORES: IndicadorCatalogo[] = [
  { id: 'puestos_demandados', nombre: 'Puestos demandados', unidad: 'avisos' },
  { id: 'tasa_desempleo', nombre: 'Tasa de desempleo', unidad: '%' },
  { id: 'tasa_empleo', nombre: 'Tasa de empleo', unidad: '%' },
  { id: 'salario_real_indice', nombre: 'Salario real (índice base 100)', unidad: 'índice' },
  { id: 'empleo_registrado', nombre: 'Empleo registrado', unidad: 'miles de personas' },
];

export function indicadorPorId(id: string): IndicadorCatalogo | undefined {
  return INDICADORES.find((i) => i.id === id);
}

export function ocupacionesPorSector(sector?: string): Ocupacion[] {
  if (!sector) return OCUPACIONES;
  return OCUPACIONES.filter((o) => o.sector === sector);
}
