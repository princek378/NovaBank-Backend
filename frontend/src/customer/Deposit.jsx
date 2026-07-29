import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { getApiUrl } from "../utils/api";
import "./customer-forms.css";

export default function Deposit() {
  const navigate = useNavigate();
  const [amount, setAmount] = useState("");
  const [message, setMessage] = useState("");
  const [ok, setOk] = useState(false);
  const [loading, setLoading] = useState(false);

  async function depositMoney() {
    if (!amount || Number(amount) <= 0) {
      setOk(false);
      setMessage("Enter a valid amount");
      return;
    }
    setLoading(true);
    setMessage("");
    try {
      const response = await fetch(`${getApiUrl()}/api/transactions/deposit`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token") || ""}`,
        },
        body: JSON.stringify({
          account_number: localStorage.getItem("account_number"),
          amount: amount,
        }),
      });
      const data = await response.json();
      if (response.ok) {
        setOk(true);
        setMessage(data.message || "Deposit successful");
        setAmount("");
      } else {
        setOk(false);
        setMessage(data.message || "Deposit failed");
      }
    } catch {
      setOk(false);
      setMessage("Server error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="cf-page">
      <button className="cf-back" onClick={() => navigate("/customer/dashboard")}>
        ← Back to dashboard
      </button>
      <div className="cf-card">
        <h1>Deposit money</h1>
        <p>Add funds to your NovaBank account</p>
        <div className="cf-field">
          <label>Amount (USD)</label>
          <input
            type="number"
            min="0"
            step="0.01"
            placeholder="0.00"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
          />
        </div>
        <button className="cf-submit" onClick={depositMoney} disabled={loading}>
          {loading ? "Processing…" : "Deposit"}
        </button>
        {message && (
          <div className={`cf-msg ${ok ? "ok" : "err"}`}>{message}</div>
        )}
      </div>
    </div>
  );
}
