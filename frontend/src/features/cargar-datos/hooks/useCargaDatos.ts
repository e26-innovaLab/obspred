import { useState } from 'react';
import type {
  ArchivoSeleccionado,
  InfoOrigen,
  PasoCarga,
  ResultadoValidacion,
} from '../types';

// Mock de validación: simula lo que hará el backend al recibir el archivo.
function validarMock(_archivo: ArchivoSeleccionado): ResultadoValidacion {
  return {
    valido: true,
    totalRegistros: 1248,
    erroresEstructura: 0,
    preview: [
      { pais: 'Argentina', ocupacion: 'Analista de datos',    periodo: '2024', indicador: 'Demanda laboral', valor: 1240 },
      { pais: 'Argentina', ocupacion: 'Desarrollador web',    periodo: '2024', indicador: 'Demanda laboral', valor: 980  },
      { pais: 'Argentina', ocupacion: 'Enfermería',           periodo: '2023', indicador: 'Demanda laboral', valor: 760  },
      { pais: 'Argentina', ocupacion: 'Técnico en energía',   periodo: '2024', indicador: 'Demanda laboral', valor: 640  },
    ],
  };
}

export function useCargaDatos() {
  const [paso, setPaso] = useState<PasoCarga>(1);
  const [archivo, setArchivo] = useState<ArchivoSeleccionado | null>(null);
  const [origen, setOrigen] = useState<InfoOrigen>({ pais: '', fuente: '', fechaActualizacion: '' });
  const [validacion, setValidacion] = useState<ResultadoValidacion | null>(null);
  const [cargando, setCargando] = useState(false);

  function seleccionarArchivo(file: File) {
    const nombre = file.name.toLowerCase();
    const formato = nombre.endsWith('.csv') ? 'csv' : 'xlsx';
    setArchivo({ nombre: file.name, tamanio: file.size, formato, archivo: file });
  }

  function irAPaso(p: PasoCarga) {
    setPaso(p);
  }

  function continuar() {
    if (paso === 1 && archivo) {
      setPaso(2);
    } else if (paso === 2) {
      // Simula llamada al backend para validar
      setCargando(true);
      setTimeout(() => {
        setValidacion(validarMock(archivo!));
        setCargando(false);
        setPaso(3);
      }, 800);
    } else if (paso === 3) {
      // Simula confirmación de carga
      setCargando(true);
      setTimeout(() => {
        setCargando(false);
        setPaso(4);
      }, 600);
    }
  }

  function reiniciar() {
    setArchivo(null);
    setOrigen({ pais: '', fuente: '', fechaActualizacion: '' });
    setValidacion(null);
    setPaso(1);
  }

  return {
    paso,
    archivo,
    origen,
    validacion,
    cargando,
    seleccionarArchivo,
    setOrigen,
    continuar,
    irAPaso,
    reiniciar,
  };
}
