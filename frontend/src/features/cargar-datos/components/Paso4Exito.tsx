import { useNavigate } from 'react-router-dom';
import type { ArchivoSeleccionado, InfoOrigen } from '../types';

interface Props {
  archivo: ArchivoSeleccionado;
  origen: InfoOrigen;
  totalRegistros: number;
  onNuevaCarga: () => void;
}

const PAIS_LABEL: Record<string, string> = {
  ARG: 'Argentina',
  URY: 'Uruguay',
  CHL: 'Chile',
};

// Paso 4: confirmación de carga exitosa.
export function Paso4Exito({ archivo, origen, totalRegistros, onNuevaCarga }: Props) {
  const navigate = useNavigate();

  return (
    <section className="carga-paso">
      <h2 className="carga-paso__titulo">Carga completada</h2>
      <p className="carga-paso__descripcion">El dataset se incorporó correctamente a la base de datos utilizada por Faro.</p>

      <div className="carga-exito">
        <div className="carga-exito__icono" aria-hidden>✓</div>
        <h3 className="carga-exito__titulo">¡Datos incorporados!</h3>
        <p className="carga-exito__archivo">{archivo.nombre}</p>
        <p className="carga-exito__meta">
          {totalRegistros.toLocaleString()} registros procesados
          {origen.fuente ? ` · Fuente: ${origen.fuente}` : ''}
          {origen.pais ? ` · País: ${PAIS_LABEL[origen.pais] ?? origen.pais}` : ''}
        </p>

        <div className="carga-exito__acciones">
          <button type="button" className="btn btn--primario" onClick={() => navigate('/')}>
            Volver a Faro
          </button>
          <button type="button" className="btn btn--secundario" onClick={onNuevaCarga}>
            Cargar otro dataset
          </button>
        </div>
      </div>

      <p className="carga-paso__nota carga-paso__nota--centrada">
        Los indicadores podrán utilizar estos datos una vez procesados.
      </p>
    </section>
  );
}
