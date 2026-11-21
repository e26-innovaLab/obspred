import { useRef, useState } from 'react';
import type { ArchivoSeleccionado } from '../types';

interface Props {
  archivo: ArchivoSeleccionado | null;
  onSeleccionar: (file: File) => void;
  onContinuar: () => void;
  onCancelar: () => void;
}

function formatoKB(bytes: number) {
  return `${(bytes / 1024).toFixed(0)} KB`;
}

// Paso 1: selección de archivo CSV o XLSX, con drag & drop.
export function Paso1Archivo({ archivo, onSeleccionar, onContinuar, onCancelar }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [arrastrando, setArrastrando] = useState(false);

  function manejarArchivo(file: File) {
    const nombre = file.name.toLowerCase();
    if (nombre.endsWith('.csv') || nombre.endsWith('.xlsx')) {
      onSeleccionar(file);
    }
  }

  return (
    <section className="carga-paso">
      <h2 className="carga-paso__titulo">Cargar datos</h2>
      <p className="carga-paso__descripcion">Incorporá un dataset al Observatorio. El archivo será revisado antes de integrarse.</p>

      <div className="carga-paso__bloque">
        <h3>Archivo de datos</h3>

        <div
          className={`carga-dropzone ${arrastrando ? 'carga-dropzone--activo' : ''}`}
          onDragOver={(e) => { e.preventDefault(); setArrastrando(true); }}
          onDragLeave={() => setArrastrando(false)}
          onDrop={(e) => {
            e.preventDefault();
            setArrastrando(false);
            const file = e.dataTransfer.files[0];
            if (file) manejarArchivo(file);
          }}
          onClick={() => inputRef.current?.click()}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => e.key === 'Enter' && inputRef.current?.click()}
          aria-label="Área de carga de archivo"
        >
          <span className="carga-dropzone__icono" aria-hidden>↑</span>
          <p className="carga-dropzone__titulo">Seleccioná un archivo CSV o Excel</p>
          <p className="carga-dropzone__formatos">Formatos admitidos: CSV y XLSX</p>
          <p className="carga-dropzone__drag">o arrastrá y soltá el archivo aquí</p>
          <button
            type="button"
            className="btn btn--primario"
            onClick={(e) => { e.stopPropagation(); inputRef.current?.click(); }}
          >
            Seleccionar archivo
          </button>
          <input
            ref={inputRef}
            type="file"
            accept=".csv,.xlsx"
            className="carga-dropzone__input"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) manejarArchivo(file);
            }}
          />
        </div>

        {archivo && (
          <div className="carga-archivo-seleccionado">
            <span className="carga-archivo-seleccionado__badge">{archivo.formato.toUpperCase()}</span>
            <div className="carga-archivo-seleccionado__info">
              <span className="carga-archivo-seleccionado__nombre">{archivo.nombre}</span>
              <span className="carga-archivo-seleccionado__meta">
                {archivo.formato.toUpperCase()} · {formatoKB(archivo.tamanio)}
              </span>
            </div>
            <button type="button" className="btn btn--secundario" onClick={() => inputRef.current?.click()}>
              Cambiar archivo
            </button>
          </div>
        )}

        <p className="carga-paso__nota">La información se validará antes de incorporarse a Faro.</p>
      </div>

      <div className="carga-paso__acciones">
        <button type="button" className="btn btn--secundario" onClick={onCancelar}>Cancelar</button>
        <button type="button" className="btn btn--primario" onClick={onContinuar} disabled={!archivo}>
          Continuar
        </button>
      </div>
    </section>
  );
}
