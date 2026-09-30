import { lazy, Suspense } from 'react';
import { createBrowserRouter } from 'react-router-dom';
import { AppLayout } from './components/layout/AppLayout';

// Cada vista se carga bajo demanda: reduce el bundle inicial, algo
// relevante acá porque Recharts es una dependencia pesada.
const DashboardPage = lazy(() => import('./features/dashboard/DashboardPage').then((m) => ({ default: m.DashboardPage })));
const OcupacionesPage = lazy(() => import('./features/ocupaciones/OcupacionesPage').then((m) => ({ default: m.OcupacionesPage })));
const TendenciasPage = lazy(() => import('./features/tendencias/TendenciasPage').then((m) => ({ default: m.TendenciasPage })));
const BrechasPage = lazy(() => import('./features/brechas/BrechasPage').then((m) => ({ default: m.BrechasPage })));
const TrazabilidadPage = lazy(() =>
  import('./features/trazabilidad/TrazabilidadPage').then((m) => ({ default: m.TrazabilidadPage })),
);
const DetailPage = lazy(() => import('./features/detail/DetailPage').then((m) => ({ default: m.DetailPage })),);

function conSuspense(element: React.ReactNode) {
  return <Suspense fallback={<p className="page">Cargando…</p>}>{element}</Suspense>;
}

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { index: true, element: conSuspense(<DashboardPage />) },
      { path: 'ocupaciones', element: conSuspense(<OcupacionesPage />) },
      { path: 'tendencias', element: conSuspense(<TendenciasPage />) },
      { path: 'brechas', element: conSuspense(<BrechasPage />) },
      { path: 'trazabilidad', element: conSuspense(<TrazabilidadPage />) },
      { path: 'detail', element: conSuspense(<DetailPage />) },
    ],
  },
]);
