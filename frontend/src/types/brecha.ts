export interface HabilidadComparada {
  habilidad: string;
  demanda: number; // 0-100, intensidad de demanda del mercado
  ofertaFormativa: number; // 0-100, cobertura de la oferta educativa
  emergente: boolean;
}
