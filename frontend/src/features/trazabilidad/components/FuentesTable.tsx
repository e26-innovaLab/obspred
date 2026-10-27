import type { FuenteTrazable } from "../../../services/mock/trazabilidad";

const ESTADO_LABEL: Record<FuenteTrazable["estado"], string> = {
  activa: "Activa",
  desactualizada: "Desactualizada",
  "no-disponible": "No disponible",
};

export function FuentesTable({ fuentes }: { fuentes: FuenteTrazable[] }) {
  return (
    <table className="fuentes-table">
      <thead>
        <tr>
          <th>Fuente/Organismo</th>
          <th>País</th>
          <th>Cobertura</th>
          <th>Actualización</th>
          <th>Validación</th>
          <th>Acceso</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Datos Argentina · Series de Tiempo</td>
          <td>Argentina</td>
          <td>Indicadores económicos y sociales</td>
          <td>Por fuente</td>
          <td>
            <span className="estado-validacion">Por validar</span>
          </td>
          <td>
            <a href="#">Consultar API</a>
          </td>
        </tr>

        <tr>
          <td>CEPALSTAT · ILOSTAT · Banco Mundial</td>
          <td>Uruguay</td>
          <td>Empleo, educación y población</td>
          <td>Por fuente</td>
          <td>
            <span className="estado-validacion">Por validar</span>
          </td>
          <td>
            <a href="#">Consultar APIs</a>
          </td>
        </tr>

        <tr>
          <td>SIMEL Chile · INE</td>
          <td>Chile</td>
          <td>Empleo y remuneraciones</td>
          <td>Por fuente</td>
          <td>
            <span className="estado-validacion">Por validar</span>
          </td>
          <td>
            <a href="#">Consultar API</a>
          </td>
        </tr>
      </tbody>
    </table>
  );
}
