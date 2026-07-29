import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getApiUrl } from "../utils/api";
import "../styles/auth.css";

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
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
        body: JSON.stringify({ email, password }),
      });
      const data = await response.json();

      if (!response.ok) {
        setError(data.message || "Login failed");
        return;
      }

      if (data.user.role === "Admin") {
        setError("Please use the Admin Login portal for administrator access.");
        return;
      }

      localStorage.setItem("token", data.token);
      localStorage.setItem("user", JSON.stringify(data.user));
      if (data.user.account_number) {
        localStorage.setItem("account_number", data.user.account_number);
      }

      navigate("/customer/dashboard");
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
          <span className="auth-badge">Customer</span>
          <h1>Welcome back</h1>
          <p>Sign in to your NovaBank account</p>
        </div>

        {error && <div className="auth-error">{error}</div>}

        <form className="auth-form" onSubmit={handleLogin}>
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              placeholder="Your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
          </div>

          <button type="submit" className="auth-submit" disabled={loading}>
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        <div className="auth-footer">
          Don’t have an account? <Link to="/register">Create one</Link>
          <br />
          <br />
          Administrator? <Link to="/admin/login">Admin login</Link>
        </div>
      </div>
    </div>
  );
}
