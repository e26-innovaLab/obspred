import type { ResultadoValidacion } from '../types';

interface Props {
  validacion: ResultadoValidacion;
  onConfirmar: () => void;
  onVolver: () => void;
  cargando: boolean;
}

// Paso 3: revisión y validación — muestra estructura y preview de los datos.
export function Paso3Validacion({ validacion, onConfirmar, onVolver, cargando }: Props) {
  return (
    <section className="carga-paso">
      <h2 className="carga-paso__titulo">Revisión y validación</h2>
      <p className="carga-paso__descripcion">Revisá la estructura del archivo y los registros detectados antes de confirmar.</p>

      <div className={`carga-validacion-estado ${validacion.valido ? 'carga-validacion-estado--ok' : 'carga-validacion-estado--error'}`}>
        <span className="carga-validacion-estado__titulo">
          {validacion.valido ? 'Estructura válida' : 'Errores detectados'}
        </span>
        <span>
          Se detectaron {validacion.totalRegistros.toLocaleString()} registros y los campos obligatorios están presentes.
        </span>
      </div>

      <div className="carga-paso__bloque">
        <h3>Vista previa de datos</h3>
        <p className="carga-paso__nota">Primeros registros del archivo</p>
        <div className="carga-tabla-preview">
          <table>
            <thead>
              <tr>
                <th>País</th>
                <th>Ocupación</th>
                <th>Período</th>
                <th>Indicador</th>
                <th>Valor</th>
              </tr>
            </thead>
            <tbody>
              {validacion.preview.map((row, i) => (
                <tr key={i}>
                  <td>{row.pais}</td>
                  <td>{row.ocupacion}</td>
                  <td>{row.periodo}</td>
                  <td>{row.indicador}</td>
                  <td>{row.valor.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="carga-validacion-resumen">
          <span className="carga-validacion-resumen__ok">
            {validacion.totalRegistros.toLocaleString()} registros válidos
          </span>
          <span className="carga-validacion-resumen__errores">
            {validacion.erroresEstructura} errores de estructura
          </span>
        </div>
      </div>

      <div className="carga-paso__acciones">
        <button type="button" className="btn btn--secundario" onClick={onVolver}>Volver</button>
        <button
          type="button"
          className="btn btn--primario"
          onClick={onConfirmar}
          disabled={!validacion.valido || cargando}
        >
          {cargando ? 'Cargando…' : 'Confirmar carga'}
        </button>
      </div>
    </section>
  );
}
