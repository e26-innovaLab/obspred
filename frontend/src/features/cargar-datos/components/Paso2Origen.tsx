import type { ArchivoSeleccionado, InfoOrigen, PaisId } from '../types';

interface Props {
  archivo: ArchivoSeleccionado;
  origen: InfoOrigen;
  onCambiar: (o: InfoOrigen) => void;
  onContinuar: () => void;
  onVolver: () => void;
  cargando: boolean;
}

const PAISES: { id: PaisId; label: string }[] = [
  { id: 'ARG', label: 'Argentina' },
  { id: 'URY', label: 'Uruguay' },
  { id: 'CHL', label: 'Chile' },
];

function formatoKB(bytes: number) {
  return `${(bytes / 1024).toFixed(0)} KB`;
}

// Paso 2: información de origen del dataset (país, fuente, fecha).
export function Paso2Origen({ archivo, origen, onCambiar, onContinuar, onVolver, cargando }: Props) {
  const valido = origen.pais !== '' && origen.fuente.trim() !== '';

  return (
    <section className="carga-paso">
      <h2 className="carga-paso__titulo">Datos del archivo</h2>
      <p className="carga-paso__descripcion">Completá el contexto de origen para registrar correctamente el dataset.</p>

      <div className="carga-paso__bloque">
        <h3>Archivo seleccionado</h3>
        <div className="carga-archivo-seleccionado">
          <span className="carga-archivo-seleccionado__badge">{archivo.formato.toUpperCase()}</span>
          <div className="carga-archivo-seleccionado__info">
            <span className="carga-archivo-seleccionado__nombre">{archivo.nombre}</span>
            <span className="carga-archivo-seleccionado__meta">
              {archivo.formato.toUpperCase()} · {formatoKB(archivo.tamanio)}
            </span>
          </div>
        </div>
      </div>

      <div className="carga-paso__bloque">
        <h3>Información de origen</h3>
        <div className="carga-formulario">
          <div className="carga-formulario__fila">
            <div className="carga-formulario__campo">
              <label htmlFor="carga-pais">País</label>
              <select
                id="carga-pais"
                value={origen.pais}
                onChange={(e) => onCambiar({ ...origen, pais: e.target.value as PaisId })}
              >
                <option value="" disabled>Seleccioná un país</option>
                {PAISES.map((p) => (
                  <option key={p.id} value={p.id}>{p.label}</option>
                ))}
              </select>
            </div>

            <div className="carga-formulario__campo">
              <label htmlFor="carga-fuente">Fuente de información</label>
              <input
                id="carga-fuente"
                type="text"
                placeholder="Organismo / dataset oficial"
                value={origen.fuente}
                onChange={(e) => onCambiar({ ...origen, fuente: e.target.value })}
              />
            </div>
          </div>

          <div className="carga-formulario__campo carga-formulario__campo--mitad">
            <label htmlFor="carga-fecha">Fecha de actualización</label>
            <input
              id="carga-fecha"
              type="text"
              placeholder="DD / MM / AAAA"
              value={origen.fechaActualizacion}
              onChange={(e) => onCambiar({ ...origen, fechaActualizacion: e.target.value })}
            />
          </div>
        </div>
      </div>

      <div className="carga-paso__acciones">
        <button type="button" className="btn btn--secundario" onClick={onVolver}>Volver</button>
        <button type="button" className="btn btn--primario" onClick={onContinuar} disabled={!valido || cargando}>
          {cargando ? 'Validando…' : 'Continuar'}
        </button>
      </div>
    </section>
  );
}
