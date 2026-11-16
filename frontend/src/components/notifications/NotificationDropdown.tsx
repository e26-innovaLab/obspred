import type { Notification } from "../../services/mock/notifications";

interface NotificationDropdownProps {
  notifications: Notification[];
  onMarkAsRead: (id: number) => void;
}

export function NotificationDropdown({
  notifications,
  onMarkAsRead,
}: NotificationDropdownProps) {
  return (
    <div className="notification-dropdown">
      <div className="notification-dropdown__header">
        <h3>Notificaciones</h3>
        <span>{notifications.filter((n) => !n.leida).length} sin leer</span>
      </div>

      {notifications.length === 0 ? (
        <p className="notification-dropdown__empty">
          No tenés notificaciones.
        </p>
      ) : (
        <ul>
          {notifications.map((notification) => (
            <li
              key={notification.id}
              className={`notification-item ${
                notification.leida ? "notification-item--read" : ""
              }`}
              data-nivel={notification.nivel}
            >
              <div className="notification-item__content">
                <strong>{notification.titulo}</strong>
                <p>{notification.descripcion}</p>
                <time>{notification.fecha}</time>
              </div>

              {!notification.leida && (
                <button
                  type="button"
                  onClick={() => onMarkAsRead(notification.id)}
                >
                  Marcar como leída
                </button>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}