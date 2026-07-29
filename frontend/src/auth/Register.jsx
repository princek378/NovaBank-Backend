import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getApiUrl } from "../utils/api";
import "../styles/auth.css";

export default function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    email: "",
    password: "",
    phone: "",
    address: "",
  });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);

    try {
      const response = await fetch(`${getApiUrl()}/api/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const data = await response.json();

      if (!response.ok) {
        setError(data.message || "Registration failed");
        return;
      }

      setSuccess(
        `Account created! Your account number is ${data.account_number}. You can now log in.`
      );
      setTimeout(() => navigate("/login"), 2500);
    } catch (err) {
      setError("Cannot connect to server. Please try again later.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card wide">
        <Link to="/" className="auth-back">← Back to home</Link>

        <div className="auth-header">
          <div className="logo">Nova<span>Bank</span></div>
          <span className="auth-badge">New Customer</span>
          <h1>Create your account</h1>
          <p>Open a NovaBank account in under a minute</p>
        </div>

        {error && <div className="auth-error">{error}</div>}
        {success && <div className="auth-success">{success}</div>}

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label>First name</label>
              <input
                name="first_name"
                placeholder="John"
                value={form.first_name}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <label>Last name</label>
              <input
                name="last_name"
                placeholder="Doe"
                value={form.last_name}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label>Email</label>
            <input
              name="email"
              type="email"
              placeholder="you@example.com"
              value={form.email}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              name="password"
              type="password"
              placeholder="At least 6 characters"
              value={form.password}
              onChange={handleChange}
              required
              minLength={6}
            />
          </div>

          <div className="form-group">
            <label>Phone (optional)</label>
            <input
              name="phone"
              placeholder="+1 555 000 0000"
              value={form.phone}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label>Address (optional)</label>
            <input
              name="address"
              placeholder="Street, City"
              value={form.address}
              onChange={handleChange}
            />
          </div>

          <button type="submit" className="auth-submit" disabled={loading}>
            {loading ? "Creating account..." : "Create Account"}
          </button>
        </form>

        <div className="auth-footer">
          Already have an account? <Link to="/login">Sign in</Link>
        </div>
      </div>
    </div>
  );
}
