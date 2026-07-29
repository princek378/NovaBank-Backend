import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getApiUrl } from "../utils/api";
import "../styles/auth.css";

export default function AdminLogin() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleLogin(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await fetch(`${getApiUrl()}/api/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: username, password }),
      });
      const data = await response.json();

      if (!response.ok) {
        setError(data.message || "Invalid credentials");
        return;
      }

      if (data.user.role !== "Admin") {
        setError("This portal is for administrators only.");
        return;
      }

      localStorage.setItem("token", data.token);
      localStorage.setItem("user", JSON.stringify(data.user));
      localStorage.setItem("admin", "true");

      navigate("/admin/dashboard");
    } catch (err) {
      setError("Cannot connect to server. Please try again later.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <Link to="/" className="auth-back">← Back to home</Link>

        <div className="auth-header">
          <div className="logo">Nova<span>Bank</span></div>
          <span className="auth-badge">Administrator</span>
          <h1>Admin Portal</h1>
          <p>Sign in with your admin credentials</p>
        </div>

        {error && <div className="auth-error">{error}</div>}

        <form className="auth-form" onSubmit={handleLogin}>
          <div className="form-group">
            <label>Username or Email</label>
            <input
              type="text"
              placeholder="admin"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              autoComplete="username"
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
          </div>

          <button type="submit" className="auth-submit" disabled={loading}>
            {loading ? "Signing in..." : "Admin Sign In"}
          </button>
        </form>

        <div className="auth-footer">
          Default: <strong>admin</strong> / <strong>12345678</strong>
          <br />
          You can change these after login in Settings.
          <br />
          <br />
          <Link to="/login">Customer login</Link>
        </div>
      </div>
    </div>
  );
}
