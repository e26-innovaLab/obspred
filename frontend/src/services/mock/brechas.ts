import type { Filtros } from '../../types/kpi';
import type { HabilidadComparada } from '../../types/brecha';
import { seededInt, seededRange } from './random';

const HABILIDADES_POR_SECTOR: Record<string, string[]> = {
  tecnologia: ['Cloud computing', 'Análisis de datos', 'Ciberseguridad', 'IA aplicada', 'DevOps'],
  salud: ['Telemedicina', 'Gestión de historias clínicas digitales', 'Cuidado geriátrico', 'Bioestadística'],
  energia: ['Energías renovables', 'Eficiencia energética', 'Mantenimiento predictivo', 'Normativa ambiental'],
  turismo: ['Gestión de experiencias digitales', 'Marketing en redes', 'Idiomas', 'Sostenibilidad turística'],
  'economia-conocimiento': ['Propiedad intelectual', 'Gestión de la innovación', 'Análisis financiero', 'Product management'],
};

const DEFAULT_HABILIDADES = ['Alfabetización digital', 'Trabajo en equipo remoto', 'Pensamiento analítico'];

export function getHabilidadesComparadas(filtros: Filtros): HabilidadComparada[] {
  const habilidades = filtros.sector ? HABILIDADES_POR_SECTOR[filtros.sector] ?? DEFAULT_HABILIDADES : DEFAULT_HABILIDADES;
  const seed = `${filtros.pais}-${filtros.sector ?? 'all'}-${filtros.ocupacionId ?? 'all'}`;

  return habilidades.map((habilidad) => {
    const demanda = Math.round(seededRange(`${seed}-${habilidad}-dem`, 40, 98));
    const ofertaFormativa = Math.round(seededRange(`${seed}-${habilidad}-of`, 20, 90));
    return {
      habilidad,
      demanda,
      ofertaFormativa,
      emergente: seededInt(`${seed}-${habilidad}-emerg`, 0, 4) === 0,
    };
  });
}
