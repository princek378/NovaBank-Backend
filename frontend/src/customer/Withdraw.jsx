import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { getApiUrl } from "../utils/api";
import "./customer-forms.css";

export default function Withdraw() {
  const navigate = useNavigate();
  const [amount, setAmount] = useState("");
  const [message, setMessage] = useState("");
  const [ok, setOk] = useState(false);
  const [loading, setLoading] = useState(false);

  async function withdrawMoney() {
    if (!amount || Number(amount) <= 0) {
      setOk(false);
      setMessage("Enter a valid amount");
      return;
    }
    setLoading(true);
    setMessage("");
    try {
      const response = await fetch(`${getApiUrl()}/api/transactions/withdraw`, {
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
        setMessage(data.message || "Withdrawal successful");
        setAmount("");
      } else {
        setOk(false);
        setMessage(data.message || "Withdrawal failed");
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
        <h1>Withdraw money</h1>
        <p>Take funds out of your NovaBank account</p>
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
        <button className="cf-submit" onClick={withdrawMoney} disabled={loading}>
          {loading ? "Processing…" : "Withdraw"}
        </button>
        {message && (
          <div className={`cf-msg ${ok ? "ok" : "err"}`}>{message}</div>
        )}
      </div>
    </div>
  );
}
