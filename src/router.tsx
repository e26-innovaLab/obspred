import { createBrowserRouter } from 'react-router-dom';
import { AppLayout } from './components/layout/AppLayout';
import { DashboardPage } from './features/dashboard/DashboardPage';
import { OcupacionesPage } from './features/ocupaciones/OcupacionesPage';
import { TendenciasPage } from './features/tendencias/TendenciasPage';
import { BrechasPage } from './features/brechas/BrechasPage';
import { TrazabilidadPage } from './features/trazabilidad/TrazabilidadPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: 'ocupaciones', element: <OcupacionesPage /> },
      { path: 'tendencias', element: <TendenciasPage /> },
      { path: 'brechas', element: <BrechasPage /> },
      { path: 'trazabilidad', element: <TrazabilidadPage /> },
    ],
  },
]);
