import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { getApiUrl } from "../utils/api";
import "./customer-forms.css";

export default function Transfer() {
  const navigate = useNavigate();
  const [receiver, setReceiver] = useState("");
  const [amount, setAmount] = useState("");
  const [message, setMessage] = useState("");
  const [ok, setOk] = useState(false);
  const [loading, setLoading] = useState(false);

  async function makeTransfer() {
    if (!receiver || !amount || Number(amount) <= 0) {
      setOk(false);
      setMessage("Fill in receiver account and a valid amount");
      return;
    }
    setLoading(true);
    setMessage("");
    try {
      const response = await fetch(`${getApiUrl()}/api/transactions/transfer`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token") || ""}`,
        },
        body: JSON.stringify({
          from_account: localStorage.getItem("account_number"),
          to_account: receiver,
          amount: amount,
        }),
      });
      const data = await response.json();
      if (response.ok) {
        setOk(true);
        setMessage(data.message || "Transfer successful");
        setReceiver("");
        setAmount("");
      } else {
        setOk(false);
        setMessage(data.message || "Transfer failed");
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
        <h1>Transfer money</h1>
        <p>Send funds to another NovaBank account</p>
        <div className="cf-field">
          <label>Receiver account number</label>
          <input
            type="text"
            placeholder="e.g. NB1234567890"
            value={receiver}
            onChange={(e) => setReceiver(e.target.value)}
          />
        </div>
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
        <button className="cf-submit" onClick={makeTransfer} disabled={loading}>
          {loading ? "Sending…" : "Send money"}
        </button>
        {message && (
          <div className={`cf-msg ${ok ? "ok" : "err"}`}>{message}</div>
        )}
      </div>
    </div>
  );
}
