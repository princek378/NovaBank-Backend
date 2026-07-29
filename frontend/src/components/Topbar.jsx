import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getApiUrl } from "../utils/api";
import "./Topbar.css";

export default function Topbar() {
  const navigate = useNavigate();

  const [settings, setSettings] = useState({
    admin_name: "Administrator",
    bank_name: "NovaBank",
  });
  const [unread, setUnread] = useState(0);

  useEffect(() => {
    loadSettings();
    loadUnread();

    // Refresh unread count every 5 seconds
    const timer = setInterval(loadUnread, 5000);
    return () => clearInterval(timer);
  }, []);

  async function loadSettings() {
    try {
      const response = await fetch(`${getApiUrl()}/api/settings`);
      const data = await response.json();
      setSettings({
        admin_name: data.admin_name || "Administrator",
        bank_name: data.bank_name || "NovaBank",
      });
    } catch (error) {
      console.log("Settings loading error:", error);
    }
  }

  async function loadUnread() {
    try {
      const response = await fetch(`${getApiUrl()}/api/chat/unread`);
      const data = await response.json();
      if (typeof data.unread === "number") {
        setUnread(data.unread);
      }
    } catch (error) {
      // keep last known count
    }
  }

  const initial =
    settings.admin_name && settings.admin_name.length > 0
      ? settings.admin_name.charAt(0).toUpperCase()
      : "A";

  return (
    <div className="topbar">
      <div className="topbar-left">
        <h2>{settings.bank_name}</h2>
      </div>

      <div className="topbar-right">
        <div
          className="notification"
          onClick={() => navigate("/admin/messages")}
          title={unread > 0 ? `${unread} unread message(s)` : "Messages"}
        >
          🔔
          <span className={unread > 0 ? "has-unread" : ""}>
            {unread > 99 ? "99+" : unread}
          </span>
        </div>

        <div className="admin-profile">
          <div className="avatar">{initial}</div>
          <div>
            <h4>{settings.admin_name}</h4>
            <p>Online</p>
          </div>
        </div>
      </div>
    </div>
  );
}
