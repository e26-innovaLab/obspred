import { lazy, Suspense } from 'react';
import { createBrowserRouter } from 'react-router-dom';
import { AppLayout } from './components/layout/AppLayout';
import NotFoundPage from './features/notfound/notfound';
import { DetailPage } from './features/detail/DetailPage';

// Cada vista se carga bajo demanda (lazy loading) para optimizar el bundle inicial de la aplicación.
const DashboardPage = lazy(() => import('./features/dashboard/DashboardPage').then((m) => ({ default: m.DashboardPage })));
const OcupacionesPage = lazy(() => import('./features/ocupaciones/OcupacionesPage').then((m) => ({ default: m.OcupacionesPage })));
const TendenciasPage = lazy(() => import('./features/tendencias/TendenciasPage').then((m) => ({ default: m.TendenciasPage })));
const BrechasPage = lazy(() => import('./features/brechas/BrechasPage').then((m) => ({ default: m.BrechasPage })));
const CompararPage = lazy(() => import('./features/comparar/CompararPage').then((m) => ({ default: m.CompararPage })));
const TrazabilidadPage = lazy(() =>
  import('./features/trazabilidad/TrazabilidadPage').then((m) => ({ default: m.TrazabilidadPage })),
);

// Componente helper para envolver las rutas hijas en Suspense y mostrar una pantalla de carga mientras se descargan los módulos.
function conSuspense(element: React.ReactNode) {
  return <Suspense fallback={<p className="page">Cargando…</p>}>{element}</Suspense>;
}

// Configuración principal de las rutas de la aplicación usando React Router.
export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    children: [
      // Ruta principal / Dashboard
      { index: true, element: conSuspense(<DashboardPage />) },
      
      // Rutas de las secciones de la aplicación
      { path: 'ocupaciones', element: conSuspense(<OcupacionesPage />) },
      { path: 'tendencias', element: conSuspense(<TendenciasPage />) },
      { path: 'comparar', element: conSuspense(<CompararPage />) },
      { path: 'brechas', element: conSuspense(<BrechasPage />) },
      { path: 'trazabilidad', element: conSuspense(<TrazabilidadPage />) },
      { path: 'detail', element: conSuspense(<DetailPage />) },
      
      // Ruta de captura (catch-all) para páginas no encontradas (404)
      { path: '*', element: conSuspense(<NotFoundPage />) },
    ],
  },
]);