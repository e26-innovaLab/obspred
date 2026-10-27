import type { HabilidadComparada } from '../../../types/brecha';
import { SinDatos } from '../../../components/common/SinDatos';

export function HabilidadesEmergentesList({ emergentes }: { emergentes: HabilidadComparada[] }) {
  if (emergentes.length === 0) return <SinDatos mensaje="No se detectaron habilidades emergentes en este recorte." />;

  return (
    <ul className="habilidades-emergentes">
      {emergentes.map((h) => (
        <li key={h.habilidad}>
          {h.habilidad} <span>— demanda {h.demanda} / cobertura {h.ofertaFormativa}</span>
        </li>
      ))}
    </ul>
  );
}
