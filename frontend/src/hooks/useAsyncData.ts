import { useCallback, useEffect, useRef, useState } from 'react';

// Estado de carga uniforme para cualquier gráfico o panel.
// "empty" es distinto de "error": la consulta salió bien pero no hay datos
// (principio 04: se muestra "Sin datos", nunca un valor inventado).
export type AsyncState<T> =
  | { status: 'loading' }
  | { status: 'error'; error: string }
  | { status: 'empty' }
  | { status: 'success'; data: T };

export interface UseAsyncData<T> {
  state: AsyncState<T>;
  retry: () => void;
}

/**
 * Ejecuta `fetcher` cada vez que cambia `key` (serializá ahí los filtros).
 * Cancela la petición anterior con AbortController para que una respuesta
 * vieja no pise a una nueva cuando el usuario cambia filtros rápido.
 */
export function useAsyncData<T>(
  key: string,
  fetcher: (signal: AbortSignal) => Promise<T>,
  isEmpty: (data: T) => boolean = () => false,
): UseAsyncData<T> {
  const [intento, setIntento] = useState(0);
  const [resultado, setResultado] = useState<{ clave: string; state: AsyncState<T> } | null>(null);
  const clave = `${key}#${intento}`;

  // `fetcher` e `isEmpty` cambian de identidad en cada render; se guardan en
  // refs para que la única dependencia real del efecto sea la clave.
  const fetcherRef = useRef(fetcher);
  const isEmptyRef = useRef(isEmpty);
  useEffect(() => {
    fetcherRef.current = fetcher;
    isEmptyRef.current = isEmpty;
  });

  useEffect(() => {
    const controller = new AbortController();
    fetcherRef
      .current(controller.signal)
      .then((data) => {
        if (controller.signal.aborted) return;
        setResultado({ clave, state: isEmptyRef.current(data) ? { status: 'empty' } : { status: 'success', data } });
      })
      .catch((err: unknown) => {
        if (controller.signal.aborted) return;
        const error = err instanceof Error ? err.message : 'Ocurrió un error inesperado.';
        setResultado({ clave, state: { status: 'error', error } });
      });
    return () => controller.abort();
  }, [clave]);

  const retry = useCallback(() => setIntento((n) => n + 1), []);
  // Mientras el resultado guardado sea de otra clave, se está cargando la nueva.
  const state: AsyncState<T> = resultado?.clave === clave ? resultado.state : { status: 'loading' };
  return { state, retry };
}
