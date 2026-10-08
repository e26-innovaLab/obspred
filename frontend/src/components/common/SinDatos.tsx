// Principio 04 del roadmap: "Si un dato no está disponible, se muestra
// 'sin datos' — nunca un número inventado." Componente compartido para
// ese estado en cualquier vista.
export function SinDatos({ mensaje = 'Sin datos suficientes para mostrar este indicador.' }: { mensaje?: string }) {
  return <p className="sin-datos">{mensaje}</p>;
}
