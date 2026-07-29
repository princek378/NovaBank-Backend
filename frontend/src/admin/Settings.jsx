import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import { getApiUrl } from "../utils/api";
import "./Settings.css";

export default function Settings() {
  const [settings, setSettings] = useState({
    admin_name: "",
    email: "",
    bank_name: "",
    currency: "",
  });
  const [creds, setCreds] = useState({
    name: "",
    email: "",
    current_password: "",
    password: "",
  });
  const [message, setMessage] = useState("");
  const [credMessage, setCredMessage] = useState("");

  useEffect(() => {
    loadSettings();
  }, []);

  async function loadSettings() {
    try {
      const response = await fetch(`${getApiUrl()}/api/settings`);
      const data = await response.json();
      setSettings(data);
    } catch (error) {
      console.log(error);
    }
  }

  function handleChange(e) {
    setSettings({ ...settings, [e.target.name]: e.target.value });
  }

  function handleCredChange(e) {
    setCreds({ ...creds, [e.target.name]: e.target.value });
  }

  async function saveSettings() {
    try {
      const response = await fetch(`${getApiUrl()}/api/settings`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(settings),
      });
      const data = await response.json();
      setMessage(data.message || "Settings saved");
    } catch (error) {
      setMessage("Failed to save settings");
    }
  }

  async function saveCredentials(e) {
    e.preventDefault();
    setCredMessage("");
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`${getApiUrl()}/api/admin/change-credentials`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(creds),
      });
      const data = await response.json();
      if (!response.ok) {
        setCredMessage(data.message || "Failed to update credentials");
        return;
      }
      setCredMessage("Credentials updated successfully. Use the new details next time you log in.");
      setCreds({ name: "", email: "", current_password: "", password: "" });
    } catch (error) {
      setCredMessage("Server error while updating credentials");
    }
  }

  return (
    <div className="admin-layout">
      <Sidebar />
      <div className="main-content">
        <Topbar />

        <div className="settings-header" style={{ marginTop: 24, marginBottom: 24 }}>
          <h1>⚙️ Bank Settings</h1>
          <p>Update bank identity and administrator login</p>
        </div>

        <div className="settings-card" style={{ background: "rgba(15,23,42,.85)", padding: 28, borderRadius: 20, marginBottom: 28 }}>
          <h2 style={{ marginBottom: 16 }}>General</h2>
          <div style={{ display: "grid", gap: 14, maxWidth: 420 }}>
            <input name="admin_name" placeholder="Admin display name" value={settings.admin_name} onChange={handleChange} />
            <input name="email" placeholder="Contact email" value={settings.email} onChange={handleChange} />
            <input name="bank_name" placeholder="Bank name" value={settings.bank_name} onChange={handleChange} />
            <input name="currency" placeholder="Currency" value={settings.currency} onChange={handleChange} />
            <button onClick={saveSettings} className="btn btn-primary" style={{ maxWidth: 180 }}>
              Save Settings
            </button>
            {message && <p style={{ color: "#86efac" }}>{message}</p>}
          </div>
        </div>

        <div className="settings-card" style={{ background: "rgba(15,23,42,.85)", padding: 28, borderRadius: 20 }}>
          <h2 style={{ marginBottom: 8 }}>Change Admin Login</h2>
          <p style={{ color: "#94a3b8", marginBottom: 16, fontSize: 14 }}>
            Default is username <strong>admin</strong> and password <strong>12345678</strong>. You can change name, email and password here.
          </p>
          <form onSubmit={saveCredentials} style={{ display: "grid", gap: 14, maxWidth: 420 }}>
            <input name="name" placeholder="New display name (optional)" value={creds.name} onChange={handleCredChange} />
            <input name="email" type="email" placeholder="New login email (optional)" value={creds.email} onChange={handleCredChange} />
            <input name="current_password" type="password" placeholder="Current password (required)" value={creds.current_password} onChange={handleCredChange} required />
            <input name="password" type="password" placeholder="New password (optional)" value={creds.password} onChange={handleCredChange} />
            <button type="submit" className="btn btn-primary" style={{ maxWidth: 220 }}>
              Update Credentials
            </button>
            {credMessage && (
              <p style={{ color: credMessage.includes("success") ? "#86efac" : "#fca5a5" }}>
                {credMessage}
              </p>
            )}
          </form>
        </div>
      </div>
    </div>
  );
}
