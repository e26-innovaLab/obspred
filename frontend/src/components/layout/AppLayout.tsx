import { useState } from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';

// Las etiquetas siguen el Figma ("Inicio") y van con inicial mayúscula.
const NAV_ITEMS = [
  { to: '/', label: 'Inicio', end: true },
  { to: '/ocupaciones', label: 'Ocupaciones' },
  { to: '/tendencias', label: 'Tendencias' },
  { to: '/comparar', label: 'Comparar países' },
  { to: '/brechas', label: 'Brechas de habilidades' },
  { to: '/trazabilidad', label: 'Trazabilidad y fuentes' },
];

// En computadora el menú es una barra lateral fija. En celular y tablet
// (≤ 900px) pasa a una barra superior con botón "Menú" que despliega los links.
export function AppLayout() {
  const [menuAbierto, setMenuAbierto] = useState(false);
  const { pathname } = useLocation();
  // Al navegar se cierra el menú: se guarda la ruta en la que se abrió.
  const [rutaDelMenu, setRutaDelMenu] = useState(pathname);
  const abierto = menuAbierto && rutaDelMenu === pathname;

  return (
    <div className="app-layout">
      <header className="app-header">
        <div className="app-header__barra">
          <h1>Observatorio Predictivo</h1>
          <button
            type="button"
            className="app-header__menu-btn"
            aria-expanded={abierto}
            aria-controls="menu-principal"
            onClick={() => {
              setRutaDelMenu(pathname);
              setMenuAbierto(!abierto);
            }}
          >
            <span aria-hidden>{abierto ? '✕' : '☰'}</span> Menú
          </button>
        </div>
        <nav id="menu-principal" data-abierto={abierto}>
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
