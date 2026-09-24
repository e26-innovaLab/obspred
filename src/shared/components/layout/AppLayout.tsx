import { NavLink, Outlet } from 'react-router-dom';

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', end: true },
  { to: '/ocupaciones', label: 'Ocupaciones' },
  { to: '/tendencias', label: 'Tendencias' },
  { to: '/brechas', label: 'Brechas de habilidades' },
  { to: '/trazabilidad', label: 'Trazabilidad y fuentes' },
];

export function AppLayout() {
  return (
    <div className="app-layout">
      <header className="app-header">
        <h1>Observatorio Predictivo</h1>
        <nav>
          {NAV_ITEMS.map((item) => (
            <NavLink key={item.to} to={item.to} end={item.end}>
              {item.label}
            </NavLink>
          ))}
        </nav>
      </header>
      <main className="app-content">
        <Outlet />
      </main>
    </div>
  );
}
