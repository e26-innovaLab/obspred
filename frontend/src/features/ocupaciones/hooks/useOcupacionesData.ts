import { useMemo, useState, useEffect } from 'react';
import { useFiltros } from '../../../store/useFiltros';
import { getRankingOcupaciones, getDimensionesIndice, getEvolucionIndice } from '../../../services/mock/ocupaciones';
import { PERIODOS } from '../../../services/mock/catalogo';

export function useOcupacionesData() {
  const { filtros } = useFiltros();
  const ranking = useMemo(() => getRankingOcupaciones(filtros), [filtros]);

  const [seleccionadaId, setSeleccionadaId] = useState<string | undefined>(ranking[0]?.ocupacionId);

  // Si cambian los filtros y la ocupación seleccionada deja de estar
  // disponible en el ranking, se selecciona la primera disponible.
  useEffect(() => {
    if (!ranking.some((r) => r.ocupacionId === seleccionadaId)) {
      setSeleccionadaId(ranking[0]?.ocupacionId);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ranking]);

  const dimensiones = useMemo(
    () => (seleccionadaId ? getDimensionesIndice(filtros, seleccionadaId) : []),
    [filtros, seleccionadaId],
  );

  const evolucion = useMemo(
    () =>
      seleccionadaId
        ? getEvolucionIndice(
            filtros,
            seleccionadaId,
            PERIODOS.map((p) => p.id),
          )
        : [],
    [filtros, seleccionadaId],
  );

  return { ranking, seleccionadaId, setSeleccionadaId, dimensiones, evolucion };
}
