import { useMemo } from 'react';
import { useFiltros } from '../../../store/useFiltros';
import { getHabilidadesComparadas } from '../../../services/mock/brechas';

export function useBrechasData() {
  const { filtros } = useFiltros();

  const habilidades = useMemo(() => getHabilidadesComparadas(filtros), [filtros]);
  const emergentes = useMemo(() => habilidades.filter((h) => h.emergente), [habilidades]);

  return { habilidades, emergentes };
}
