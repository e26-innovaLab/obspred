// Paleta oficial — Manual de Marca GCBA 2026, sección "Color".
// Usada en los gráficos (Recharts no lee variables CSS directamente).
import type { Pais, TipoIndicador } from '../types/kpi';

export const PALETA_MARCA = {
  azulOscuro: '#1D3343',
  azulClaro: '#035C80',
  amarillo: '#FFCD02',
  blanco: '#FCFCFC',
  gris: '#9CA6AC',
} as const;

// Contraste contra #FCFCFC (WCAG 1.4.11 pide ≥ 3:1 en gráficos):
// azulClaro 7.2:1 · azulOscuro 12.7:1 · amarillo de marca 1.5:1.
// El amarillo de marca sirve para rellenos y realces, no para líneas:
// para líneas se usa esta variante más profunda (3.2:1).
export const AMARILLO_PROFUNDO = '#B08800';

/** Color + forma de marcador por país: el color nunca es la única pista. */
export const SERIE_PAIS: Record<Pais, { color: string; marcador: 'circulo' | 'cuadrado' | 'triangulo' }> = {
  AR: { color: PALETA_MARCA.azulClaro, marcador: 'circulo' },
  UY: { color: AMARILLO_PROFUNDO, marcador: 'cuadrado' },
  CL: { color: PALETA_MARCA.azulOscuro, marcador: 'triangulo' },
};

/** Trazo según tipo de dato (principio 03): proyectado ≠ observado a simple vista. */
export const TRAZO_TIPO: Record<TipoIndicador, string | undefined> = {
  observado: undefined,
  calculado: '2 3',
  proyeccion: '6 4',
};

export const CHART_THEME = {
  texto: '#445561',
  grilla: '#E3E8EB',
  eje: PALETA_MARCA.gris,
  bandaConfianza: PALETA_MARCA.azulClaro,
  bandaOpacidad: 0.14,
  tamanoTexto: 12,
} as const;

export const EJE_PROPS = {
  stroke: CHART_THEME.eje,
  tick: { fill: CHART_THEME.texto, fontSize: CHART_THEME.tamanoTexto },
  tickLine: false,
} as const;
