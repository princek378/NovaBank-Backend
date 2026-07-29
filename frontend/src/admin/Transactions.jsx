import { useEffect, useState } from "react";
import { getApiUrl } from "../utils/api";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import "./Transactions.css";

export default function Transactions() {
  const [transactions, setTransactions] = useState([]);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("All");

  useEffect(() => {
    loadTransactions();
  }, []);

  async function loadTransactions() {
    try {
      const response = await fetch(`${getApiUrl()}/api/admin/transactions`);
      const data = await response.json();
      setTransactions(Array.isArray(data) ? data : []);
    } catch (err) {
      console.log(err);
      setTransactions([]);
    }
  }

  const filteredTransactions = transactions.filter((tx) => {
    const q = search.toLowerCase();
    const matchesSearch =
      (tx.customer || "").toLowerCase().includes(q) ||
      (tx.account_number || "").includes(search) ||
      (tx.reference || "").toLowerCase().includes(q);
    const matchesFilter = filter === "All" ? true : tx.type === filter;
    return matchesSearch && matchesFilter;
  });

  const totalDeposits = transactions
    .filter((t) => t.type === "Deposit")
    .reduce((sum, t) => sum + Number(t.amount || 0), 0);

  const totalWithdrawals = transactions
    .filter((t) => t.type === "Withdrawal")
    .reduce((sum, t) => sum + Number(t.amount || 0), 0);

  const totalTransfers = transactions
    .filter((t) => (t.type || "").includes("Transfer"))
    .reduce((sum, t) => sum + Number(t.amount || 0), 0);

  return (
    <div className="admin-layout">
      <Sidebar />

      <div className="main-content">
        <Topbar />

        <div className="transactions-header">
          <h1>Transaction Center</h1>
          <p>Monitor every banking transaction</p>
        </div>

        <div className="transaction-stats">
          <div className="stat-box">
            <h3>Total Deposits</h3>
            <h1>{'$' + totalDeposits.toFixed(2)}</h1>
          </div>

          <div className="stat-box">
            <h3>Total Withdrawals</h3>
            <h1>{'$' + totalWithdrawals.toFixed(2)}</h1>
          </div>

          <div className="stat-box">
            <h3>Total Transfers</h3>
            <h1>{'$' + totalTransfers.toFixed(2)}</h1>
          </div>

          <div className="stat-box">
            <h3>Total Transactions</h3>
            <h1>{transactions.length}</h1>
          </div>
        </div>

        <div className="toolbar">
          <input
            placeholder="Search customer, account or reference..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />

          <select value={filter} onChange={(e) => setFilter(e.target.value)}>
            <option>All</option>
            <option>Deposit</option>
            <option>Withdrawal</option>
            <option>Transfer In</option>
            <option>Transfer Out</option>
          </select>
        </div>

        <div className="transactions-table">
          <table>
            <thead>
              <tr>
                <th>Reference</th>
                <th>Customer</th>
                <th>Account</th>
                <th>Description</th>
                <th>Type</th>
                <th>Amount</th>
                <th>Status</th>
                <th>Date</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredTransactions.map((tx) => (
                <tr key={tx.id}>
                  <td>{tx.reference}</td>
                  <td>{tx.customer}</td>
                  <td>{tx.account_number}</td>
                  <td>{tx.description}</td>
                  <td>
                    <span
                      className={`type ${(tx.type || "").replace(/\s/g, "")}`}
                    >
                      {tx.type}
                    </span>
                  </td>
                  <td>{'$' + Number(tx.amount).toFixed(2)}</td>
                  <td>
                    <span className="status">{tx.status}</span>
                  </td>
                  <td>
                    {tx.date ? new Date(tx.date).toLocaleString() : "-"}
                  </td>
                  <td>
                    <button
                      className="view-btn"
                      onClick={() => alert(JSON.stringify(tx, null, 2))}
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
