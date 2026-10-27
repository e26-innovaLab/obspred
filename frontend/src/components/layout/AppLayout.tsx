import { useState } from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import logo from '../../assets/icons/logo2.png'
import inicioIcon from '../../assets/icons/inicio.png'
import tendenciasIcon from '../../assets/icons/tendencias.png'
import fuentesIcon from '../../assets/icons/fuentes.png'
import breachasIcon from '../../assets/icons/brechas.png'
import compararIcon from '../../assets/icons/comparar.png'
import ocupacionesIcon from '../../assets/icons/ocupaciones.png'

// Las etiquetas siguen el Figma ("Inicio") y van con inicial mayúscula.
const NAV_ITEMS = [
  { to: '/', label: 'Inicio', end: true, icon: inicioIcon},
  { to: '/ocupaciones', label: 'Ocupaciones', icon: ocupacionesIcon },
  { to: '/tendencias', label: 'Tendencias', icon: tendenciasIcon},
  { to: '/comparar', label: 'Comparar países', icon: compararIcon },
  { to: '/brechas', label: 'Brechas de habilidades', icon: breachasIcon },
  { to: '/trazabilidad', label: 'Trazabilidad y fuentes', icon: fuentesIcon },
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
          <img className="logo" src={logo} alt="Logo El Faro"/>
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
      <img src={item.icon} alt="" />
      <span>{item.label}</span>
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
