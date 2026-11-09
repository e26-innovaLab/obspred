import { useNavigate } from 'react-router-dom';
import './cargar-datos.css';
import { useCargaDatos } from './hooks/useCargaDatos';
import { ProgresoPasos } from './components/ProgresoPasos';
import { Paso1Archivo } from './components/Paso1Archivo';
import { Paso2Origen } from './components/Paso2Origen';
import { Paso3Validacion } from './components/Paso3Validacion';
import { Paso4Exito } from './components/Paso4Exito';

// Vista "Cargar datos" — flujo de 4 pasos para incorporar un dataset al Observatorio.
// Ruta: /cargar-datos
// Por ahora opera en modo mock (sin llamada real al backend).
// Ver informe-frontend-para-backend.md para el contrato de la API esperado.
export function CargarDatosPage() {
  const navigate = useNavigate();
  const {
    paso,
    archivo,
    origen,
    validacion,
    cargando,
    seleccionarArchivo,
    setOrigen,
    continuar,
    irAPaso,
    reiniciar,
  } = useCargaDatos();

  return (
    <div className="page carga-datos-page">
      {paso < 4 && <ProgresoPasos pasoActual={paso} />}

      {paso === 1 && (
        <Paso1Archivo
          archivo={archivo}
          onSeleccionar={seleccionarArchivo}
          onContinuar={continuar}
          onCancelar={() => navigate('/')}
        />
      )}

      {paso === 2 && archivo && (
        <Paso2Origen
          archivo={archivo}
          origen={origen}
          onCambiar={setOrigen}
          onContinuar={continuar}
          onVolver={() => irAPaso(1)}
          cargando={cargando}
        />
      )}

      {paso === 3 && validacion && (
        <Paso3Validacion
          validacion={validacion}
          onConfirmar={continuar}
          onVolver={() => irAPaso(2)}
          cargando={cargando}
        />
      )}

      {paso === 4 && archivo && validacion && (
        <Paso4Exito
          archivo={archivo}
          origen={origen}
          totalRegistros={validacion.totalRegistros}
          onNuevaCarga={reiniciar}
        />
      )}
    </div>
  );
}
