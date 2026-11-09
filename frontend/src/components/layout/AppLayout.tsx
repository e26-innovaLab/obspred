import { useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";
import logo from "../../assets/icons/logo2.png";
import inicioIcon from "../../assets/icons/inicio.png";
import tendenciasIcon from "../../assets/icons/tendencias.png";
import fuentesIcon from "../../assets/icons/fuentes.png";
import breachasIcon from "../../assets/icons/brechas.png";
import compararIcon from "../../assets/icons/comparar.png";
import ocupacionesIcon from "../../assets/icons/ocupaciones.png";
import colapsarIcon from "../../assets/icons/colapsar.png";

const NAV_ITEMS = [
  { to: "/", label: "Inicio", end: true, icon: inicioIcon },
  { to: "/ocupaciones", label: "Ocupaciones", icon: ocupacionesIcon },
  { to: "/tendencias", label: "Tendencias", icon: tendenciasIcon },
  { to: "/comparar", label: "Comparar países", icon: compararIcon },
  { to: "/brechas", label: "Brechas de habilidades", icon: breachasIcon },
  { to: "/trazabilidad", label: "Trazabilidad y fuentes", icon: fuentesIcon },
];

export function AppLayout() {
  const [menuAbierto, setMenuAbierto] = useState(false);
  const { pathname } = useLocation();
  const [rutaDelMenu, setRutaDelMenu] = useState(pathname);
  const abierto = menuAbierto && rutaDelMenu === pathname;
  const [isCollapsed, setIsCollapsed] = useState(false);

  const toggleSidebar = () => {
    setIsCollapsed((prev) => !prev);
  };

  return (
    <div className={`app-layout ${isCollapsed ? 'sidebar--collapsed' : ''}`}>
      <header className="app-header">
        <div className="app-header__barra">
          <img className="logo" src={logo} alt="Logo El Faro" />
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
            <span aria-hidden>{abierto ? "✕" : "☰"}</span> Menú
          </button>
        </div>
        <nav id="menu-principal" data-abierto={abierto} className={isCollapsed ? 'sidebar--collapsed' : ''}>
          {NAV_ITEMS.map((item) => (
            <NavLink key={item.to} to={item.to} end={item.end} title={isCollapsed ? item.label : undefined}>
              <img src={item.icon} alt="" />
              <span>{item.label}</span>
            </NavLink>
          ))}

          <NavLink to="/cargar-datos" className="sidebar__cargar-datos" title={isCollapsed ? 'Cargar datos' : undefined}>
            <span>↑</span>
            <span>Cargar datos</span>
          </NavLink>

          <button
            className={`sidebar__toggle ${isCollapsed ? 'active' : ''}`}
            title={isCollapsed ? 'Expandir menú' : 'Colapsar menú'}
            onClick={toggleSidebar}
          >
            <img src={colapsarIcon} alt="Colapsar"/>
            <span>Colapsar</span>
          </button>
        </nav>
      </header>
      <main className="app-content">
        <Outlet />
      </main>
    </div>
  );
}