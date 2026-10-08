import { useMemo, useState } from 'react';
import { useFiltros } from '../../../store/useFiltros';
import { getRankingOcupaciones, getDimensionesIndice, getEvolucionIndice } from '../../../services/mock/ocupaciones';
import type { Fuente, Pais } from '../../../types/kpi';
import { PAISES, PERIODOS } from '../../../services/mock/catalogo';

const ORDEN_PAISES = PAISES.map((p) => p.id);

export interface FilaOcupacion {
  ocupacionId: string;
  nombre: string;
  porPais: Partial<Record<Pais, { puestos: number; indice: number; fuente: Fuente }>>;
}

/** Fila para gráficos agrupados: { nombre, AR: 70, UY: 64, CL: 81 }. */
export type FilaPorPais = { nombre: string } & Partial<Record<Pais, number>>;

// Vista Ocupaciones con comparación entre países: el país pasa a ser
// selección múltiple (casillas). Sector y período siguen siendo globales.
export function useOcupacionesData() {
  const { filtros } = useFiltros();
  const [paises, setPaises] = useState<Pais[]>(ORDEN_PAISES);
  const [elegidaId, setSeleccionadaId] = useState<string | undefined>();

  const togglePais = (pais: Pais) =>
    setPaises((prev) => {
      const nuevos = prev.includes(pais) ? prev.filter((p) => p !== pais) : [...prev, pais];
      return ORDEN_PAISES.filter((p) => nuevos.includes(p)); // orden fijo AR, UY, CL
    });

  // Una fila por ocupación con los datos de cada país marcado, ordenada por
  // los puestos del primer país elegido.
  const filas = useMemo<FilaOcupacion[]>(() => {
    const porOcupacion = new Map<string, FilaOcupacion>();
    for (const pais of paises) {
      for (const r of getRankingOcupaciones({ ...filtros, pais })) {
        const fila = porOcupacion.get(r.ocupacionId) ?? { ocupacionId: r.ocupacionId, nombre: r.nombre, porPais: {} };
        fila.porPais[pais] = { puestos: r.puestosDisponibles, indice: r.indiceEmpleabilidad, fuente: r.fuente };
        porOcupacion.set(r.ocupacionId, fila);
      }
    }
    const referencia = paises[0];
    return [...porOcupacion.values()].sort(
      (a, b) => (b.porPais[referencia]?.puestos ?? 0) - (a.porPais[referencia]?.puestos ?? 0),
    );
  }, [filtros, paises]);

  // Si la ocupación elegida ya no está (cambió el sector), se usa la primera.
  const seleccionadaId = filas.some((f) => f.ocupacionId === elegidaId) ? elegidaId : filas[0]?.ocupacionId;
  const seleccionada = filas.find((f) => f.ocupacionId === seleccionadaId);

  // Índice total + sus dimensiones, un valor por país (barras agrupadas).
  const dimensiones = useMemo<FilaPorPais[]>(() => {
    if (!seleccionada) return [];
    const total: FilaPorPais = { nombre: 'Índice total' };
    for (const p of paises) total[p] = seleccionada.porPais[p]?.indice;
    const filasDim = new Map<string, FilaPorPais>();
    for (const pais of paises) {
      for (const d of getDimensionesIndice({ ...filtros, pais }, seleccionada.ocupacionId)) {
        const fila = filasDim.get(d.nombre) ?? { nombre: d.nombre };
        fila[pais] = d.valor;
        filasDim.set(d.nombre, fila);
      }
    }
    return [total, ...filasDim.values()];
  }, [filtros, paises, seleccionada]);

  // Evolución del índice: una línea por país.
  const evolucion = useMemo<FilaPorPais[]>(() => {
    if (!seleccionada) return [];
    const periodos = PERIODOS.map((p) => p.id);
    const filasEvo: FilaPorPais[] = periodos.map((periodo) => ({ nombre: periodo }));
    for (const pais of paises) {
      getEvolucionIndice({ ...filtros, pais }, seleccionada.ocupacionId, periodos).forEach((punto, i) => {
        filasEvo[i][pais] = punto.indice;
      });
    }
    return filasEvo;
  }, [filtros, paises, seleccionada]);

  return { paises, togglePais, filas, seleccionada, seleccionadaId, setSeleccionadaId, dimensiones, evolucion };
}
