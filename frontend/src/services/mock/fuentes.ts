import type { Fuente, Pais } from '../../types/kpi';
import { seededInt } from './random';

// Fuentes oficiales relevadas para el MVP (ver roadmap, sección 7).
const FUENTES_POR_PAIS: Record<Pais, string[]> = {
  AR: ['Datos Argentina — Series de Tiempo', 'INDEC — EPH', 'CEPALSTAT'],
  UY: ['INE Uruguay — ECH', 'CEPALSTAT', 'ANEP — Observatorio de la Educación'],
  CL: ['SIMEL Chile — INE', 'Banco Central de Chile', 'CEPALSTAT'],
};

export function fuenteMock(pais: Pais, seed: string): Fuente {
  const opciones = FUENTES_POR_PAIS[pais];
  const idx = seededInt(`${seed}-fuente`, 0, opciones.length - 1);
  const diasDesdeActualizacion = seededInt(`${seed}-dias`, 0, 95);
  const estadoRoll = seededInt(`${seed}-estado`, 0, 9);

  const fecha = new Date();
  fecha.setDate(fecha.getDate() - diasDesdeActualizacion);

  const estado: Fuente['estado'] =
    estadoRoll === 0 ? 'no-disponible' : diasDesdeActualizacion > 60 ? 'desactualizada' : 'activa';

  return {
    nombre: opciones[idx],
    fechaActualizacion: fecha.toISOString(),
    estado,
  };
}
