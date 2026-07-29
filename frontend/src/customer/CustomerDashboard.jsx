import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getApiUrl } from "../utils/api";
import "./CustomerDashboard.css";

function CustomerDashboard() {
  const [customer, setCustomer] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function loadProfile() {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        navigate("/login");
        return;
      }

      const response = await fetch(`${getApiUrl()}/api/customer/profile`, {
        method: "GET",
        headers: { Authorization: `Bearer ${token}` },
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.message || "Failed to load profile");
      }
      setCustomer(data);
    } catch (err) {
      console.log(err);
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadProfile();
  }, []);

  function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    localStorage.removeItem("account_number");
    navigate("/login");
  }

  function txIconClass(type) {
    const t = (type || "").toLowerCase();
    if (t.includes("deposit")) return "deposit";
    if (t.includes("withdraw")) return "withdrawal";
    if (t.includes("transfer")) return "transfer";
    return "other";
  }

  function txEmoji(type) {
    const t = (type || "").toLowerCase();
    if (t.includes("deposit")) return "↓";
    if (t.includes("withdraw")) return "↑";
    if (t.includes("transfer")) return "↔";
    return "•";
  }

  function isCredit(type) {
    const t = (type || "").toLowerCase();
    return t.includes("deposit") || t.includes("transfer in");
  }

  if (loading) {
    return (
      <div className="cd-center">
        <div className="cd-spinner" />
        <p>Loading your dashboard…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="cd-center">
        <h2>Couldn’t load dashboard</h2>
        <p style={{ color: "#94a3b8" }}>{error}</p>
        <button className="cd-btn cd-btn-primary" onClick={logout}>
          Back to Login
        </button>
      </div>
    );
  }

  const balance = Number(customer?.account?.balance || 0);
  const accountNumber = customer?.account?.account_number || "—";
  const accountType = customer?.account?.account_type || "Savings";
  const currency = customer?.account?.currency || "USD";
  const transactions = customer?.transactions || [];

  return (
    <div className="cd-page">
      <header className="cd-topbar">
        <div className="cd-brand">
          Nova<span>Bank</span>
        </div>
        <div className="cd-top-actions">
          <span className="cd-chip">● Online</span>
          <button
            className="cd-btn cd-btn-ghost"
            onClick={() => navigate("/customer/chat")}
          >
            Support
          </button>
          <button className="cd-btn cd-btn-danger" onClick={logout}>
            Logout
          </button>
        </div>
      </header>

      <main className="cd-main">
        <div className="cd-greeting">
          <h1>Welcome back, {customer?.name?.split(" ")[0] || "Customer"}</h1>
          <p>Here’s an overview of your NovaBank account</p>
        </div>

        <div className="cd-balance-card">
          <div className="cd-balance-label">Available balance</div>
          <div className="cd-balance-amount">
            ${balance.toLocaleString(undefined, {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}
          </div>
          <div className="cd-balance-meta">
            <div className="cd-meta-item">
              <span>Account number</span>
              <span>{accountNumber}</span>
            </div>
            <div className="cd-meta-item">
              <span>Account type</span>
              <span>{accountType}</span>
            </div>
            <div className="cd-meta-item">
              <span>Currency</span>
              <span>{currency}</span>
            </div>
            <div className="cd-meta-item">
              <span>Status</span>
              <span>{customer?.status || "Active"}</span>
            </div>
          </div>
        </div>

        <div className="cd-actions">
          <button
            className="cd-action"
            onClick={() => navigate("/customer/transfer")}
          >
            <div className="cd-action-icon">↗</div>
            <span>Transfer</span>
          </button>
          <button
            className="cd-action"
            onClick={() => navigate("/customer/deposit")}
          >
            <div className="cd-action-icon">↓</div>
            <span>Deposit</span>
          </button>
          <button
            className="cd-action"
            onClick={() => navigate("/customer/withdraw")}
          >
            <div className="cd-action-icon">↑</div>
            <span>Withdraw</span>
          </button>
          <button
            className="cd-action"
            onClick={() => navigate("/customer/chat")}
          >
            <div className="cd-action-icon">💬</div>
            <span>Chat</span>
          </button>
        </div>

        <div className="cd-info-grid">
          <div className="cd-info-card">
            <h4>Email</h4>
            <p>{customer?.email || "—"}</p>
          </div>
          <div className="cd-info-card">
            <h4>Phone</h4>
            <p>{customer?.phone || "Not set"}</p>
          </div>
          <div className="cd-info-card">
            <h4>Member since</h4>
            <p>NovaBank Customer</p>
          </div>
        </div>

        <section className="cd-section">
          <div className="cd-section-header">
            <h2>Recent transactions</h2>
            <span>{transactions.length} shown</span>
          </div>

          {transactions.length === 0 ? (
            <div className="cd-empty">
              <div className="cd-empty-icon">📭</div>
              <p>No transactions yet. Make a deposit or transfer to get started.</p>
            </div>
          ) : (
            <div className="cd-tx-list">
              {transactions.map((tx) => {
                const credit = isCredit(tx.type || tx.transaction_type);
                const amount = Number(tx.amount || 0);
                return (
                  <div className="cd-tx" key={tx.id}>
                    <div
                      className={`cd-tx-icon ${txIconClass(
                        tx.type || tx.transaction_type
                      )}`}
                    >
                      {txEmoji(tx.type || tx.transaction_type)}
                    </div>
                    <div className="cd-tx-body">
                      <h4>{tx.description || tx.type || "Transaction"}</h4>
                      <p>
                        {tx.type || tx.transaction_type || "—"}
                        {tx.date
                          ? ` · ${new Date(tx.date).toLocaleString()}`
                          : ""}
                      </p>
                    </div>
                    <div className="cd-tx-amount">
                      <strong className={credit ? "pos" : "neg"}>
                        {credit ? "+" : "−"}$
                        {amount.toLocaleString(undefined, {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        })}
                      </strong>
                      <span>{tx.status || "Completed"}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default CustomerDashboard;
