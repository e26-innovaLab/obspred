// Tipos del flujo de carga de datos (4 pasos).
// Cuando Backend implemente el endpoint real, estos tipos mapean al contrato de la API.

export type PaisId = 'ARG' | 'URY' | 'CHL';

export type FormatoArchivo = 'csv' | 'xlsx';

export interface ArchivoSeleccionado {
  nombre: string;
  tamanio: number; // bytes
  formato: FormatoArchivo;
  archivo: File;
}

export interface InfoOrigen {
  pais: PaisId | '';
  fuente: string;
  fechaActualizacion: string; // DD/MM/AAAA
}

export interface RegistroPreview {
  pais: string;
  ocupacion: string;
  periodo: string;
  indicador: string;
  valor: number;
}

export interface ResultadoValidacion {
  valido: boolean;
  totalRegistros: number;
  erroresEstructura: number;
  preview: RegistroPreview[];
}

export type PasoCarga = 1 | 2 | 3 | 4;
