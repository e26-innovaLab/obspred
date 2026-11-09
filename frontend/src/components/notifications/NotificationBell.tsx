import bellIcon from "../../assets/icons/bell.svg";

interface NotificationBellProps {
  unreadCount: number;
  onClick: () => void;
}

export function NotificationBell({
  unreadCount,
  onClick,
}: NotificationBellProps) {
  return (
    <button
      type="button"
      className="notification-bell"
      onClick={onClick}
      aria-label={`Notificaciones: ${unreadCount} sin leer`}
    >
      <img src={bellIcon} alt="" />

      {unreadCount > 0 && (
        <span className="notification-bell__badge">
          {unreadCount}
        </span>
      )}
    </button>
  );
}