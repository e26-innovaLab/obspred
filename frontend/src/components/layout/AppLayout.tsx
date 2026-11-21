
import { useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";
import { notifications as initialNotifications } from "../../services/mock/notifications";
import { NotificationBell } from "../notifications/NotificationBell";
import { NotificationDropdown } from "../notifications/NotificationDropdown";
import logo from "../../assets/icons/logo2.png";
import inicioIcon from "../../assets/icons/inicio.png";
import tendenciasIcon from "../../assets/icons/tendencias.png";
import fuentesIcon from "../../assets/icons/fuentes.png";
import breachasIcon from "../../assets/icons/brechas.png";
import compararIcon from "../../assets/icons/comparar.png";
import ocupacionesIcon from "../../assets/icons/ocupaciones.png";
import colapsarIcon from "../../assets/icons/colapsar.png";
import abrirIcon from "../../assets/icons/abrir.png";
import uploadIcon from "../../assets/icons/upload.png";
import miInformeIcon from "../../assets/icons/miInformeIcon.png";

// Las etiquetas siguen el Figma ("Inicio") y van con inicial mayúscula.
const NAV_ITEMS = [
  { to: "/", label: "Inicio", end: true, icon: inicioIcon },
  { to: "/ocupaciones", label: "Ocupaciones", icon: ocupacionesIcon },
  { to: "/tendencias", label: "Tendencias", icon: tendenciasIcon },
  { to: "/comparar", label: "Comparar países", icon: compararIcon },
  { to: "/brechas", label: "Brechas de habilidades", icon: breachasIcon },
  { to: "/trazabilidad", label: "Trazabilidad y fuentes", icon: fuentesIcon },
  { to: "/cargar-datos", label: "Cargar Datos", icon: uploadIcon },
  { to: "/mi-informe", label: "Mi informe", icon: miInformeIcon },
];

// En computadora el menú es una barra lateral fija. En celular y tablet
// (≤ 900px) pasa a una barra superior con botón "Menú" que despliega los links.
export function AppLayout() {
  const [menuAbierto, setMenuAbierto] = useState(false);
  const { pathname } = useLocation();

  // Al navegar se cierra el menú: se guarda la ruta en la que se abrió.
  const [rutaDelMenu, setRutaDelMenu] = useState(pathname);
  const abierto = menuAbierto && rutaDelMenu === pathname;

  // Estado del sidebar
  const [isCollapsed, setIsCollapsed] = useState(false);

  const [notifications, setNotifications] = useState(initialNotifications);
const [notificationsOpen, setNotificationsOpen] = useState(false);

const unreadCount = notifications.filter(
  (notification) => !notification.leida
).length;

const markAsRead = (id: number) => {
  setNotifications((prev) =>
    prev.map((notification) =>
      notification.id === id
        ? { ...notification, leida: true }
        : notification
    )
  );
};

  const toggleSidebar = () => {
    setIsCollapsed((prev) => !prev);
  };

  return (
    <div className={`app-layout ${isCollapsed ? "sidebar--collapsed" : ""}`}>
      <header className="app-header">
        <div className="app-header__barra">
          <img className="logo" src={logo} alt="Logo Faro" />
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

        <nav
          id="menu-principal"
          data-abierto={abierto}
          className={isCollapsed ? "sidebar--collapsed" : ""}
        >
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              title={isCollapsed ? item.label : undefined}
              className={
                item.to === "/cargar-datos"
                  ? "sidebar__cargar-datos"
                  : undefined
              }
            >
              <img src={item.icon} alt="" />
              <span>{item.label}</span>
            </NavLink>
          ))}

          <button
            className={`sidebar__toggle ${isCollapsed ? "active" : ""}`}
            title={isCollapsed ? "Expandir menú" : "Colapsar menú"}
            onClick={toggleSidebar}
          >
            <img
              src={isCollapsed ? abrirIcon : colapsarIcon}
              alt={isCollapsed ? "Expandir" : "Colapsar"}
            />
            <span>{isCollapsed ? "Abrir" : "Cerrar"}</span>
          </button>
        </nav>
      </header>

      <main className="app-content">
  <div className="notifications-container">
    <NotificationBell
      unreadCount={unreadCount}
      onClick={() => setNotificationsOpen((prev) => !prev)}
    />

    {notificationsOpen && (
      <NotificationDropdown
        notifications={notifications}
        onMarkAsRead={markAsRead}
      />
    )}
  </div>

  <Outlet />
</main>
    </div>
  );
}
