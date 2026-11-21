export interface Notification {
  id: number;
  titulo: string;
  descripcion: string;
  fecha: string;
  nivel: "alto" | "medio" | "bajo";
  leida: boolean;
}


export const notifications: Notification[] = [
  {
    id: 1,
    titulo: "Variación significativa en empleo registrado",
    descripcion:
      "El indicador se movió más de 2 puntos respecto al período anterior.",
    fecha: "1/11/2026",
    nivel: "alto",
    leida: false,
  },
  {
    id: 2,
    titulo: "Nueva brecha de habilidades detectada",
    descripcion:
      "Se identificó una habilidad con alta demanda y baja cobertura formativa.",
    fecha: "1/11/2026",
    nivel: "medio",
    leida: false,
  },
  {
    id: 3,
    titulo: "Fuente desactualizada",
    descripcion:
      "Una de las fuentes utilizadas no publica datos nuevos hace más de 60 días.",
    fecha: "1/11/2026",
    nivel: "bajo",
    leida: false,
  },
];