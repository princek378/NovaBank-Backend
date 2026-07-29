import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import { getApiUrl } from "../utils/api";
import "./Customers.css";

export default function Customers() {
  const [customers, setCustomers] = useState([]);
  const [search, setSearch] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    loadCustomers();
  }, []);

  function loadCustomers() {
    fetch(`${getApiUrl()}/api/admin/customers`)
      .then((res) => res.json())
      .then((data) => {
        setCustomers(Array.isArray(data) ? data : []);
      })
      .catch((err) => {
        console.log(err);
        setCustomers([]);
      });
  }

  async function freezeCustomer(id) {
    try {
      await fetch(`${getApiUrl()}/api/admin/customers/${id}/freeze`, {
        method: "PUT",
      });
      loadCustomers();
    } catch (err) {
      console.log(err);
      alert("Failed to freeze customer");
    }
  }

  async function unfreezeCustomer(id) {
    try {
      await fetch(`${getApiUrl()}/api/admin/customers/${id}/unfreeze`, {
        method: "PUT",
      });
      loadCustomers();
    } catch (err) {
      console.log(err);
      alert("Failed to unfreeze customer");
    }
  }

  async function deleteCustomer(id) {
    const confirmDelete = window.confirm(
      "Delete this customer? This cannot be undone."
    );
    if (!confirmDelete) return;

    try {
      const token = localStorage.getItem("token");
      const response = await fetch(
        `${getApiUrl()}/api/admin/customers/${id}`,
        {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
        }
      );

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        alert(
          data.message ||
            data.error ||
            `Delete failed (${response.status})`
        );
        return;
      }

      alert(data.message || "Customer deleted");
      loadCustomers();
    } catch (err) {
      console.log(err);
      alert("Could not connect to server to delete customer");
    }
  }

  const filteredCustomers = customers.filter((customer) =>
    (customer.name || "")
      .toLowerCase()
      .includes(search.toLowerCase())
  );

  return (
    <div className="admin-layout">
      <Sidebar />

      <div className="main-content">
        <Topbar />

        <div className="customers-header">
          <h1>Customer Management</h1>
          <p>Manage all NovaBank customers</p>

          <input
            type="text"
            placeholder="Search customer..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />

          <button
            className="view-btn"
            style={{ marginLeft: 12 }}
            onClick={() => navigate("/admin/new-customer")}
          >
            + New Customer
          </button>
        </div>

        <div className="customers-card">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Account Number</th>
                <th>Phone</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredCustomers.length === 0 ? (
                <tr>
                  <td colSpan="6" style={{ textAlign: "center", padding: 24 }}>
                    No customers found
                  </td>
                </tr>
              ) : (
                filteredCustomers.map((customer) => (
                  <tr key={customer.id}>
                    <td>
                      <div className="customer-name">
                        {customer.name}
                      </div>
                    </td>
                    <td>{customer.email}</td>
                    <td>
                      {customer.account_number ||
                        customer.account?.account_number ||
                        "N/A"}
                    </td>
                    <td>{customer.phone || "—"}</td>
                    <td>
                      <span
                        className={
                          customer.status === "Active"
                            ? "status-active"
                            : "status-frozen"
                        }
                      >
                        {customer.status || "Active"}
                      </span>
                    </td>
                    <td>
                      <button
                        className="view-btn"
                        onClick={() =>
                          navigate(`/admin/customers/${customer.id}`)
                        }
                      >
                        View
                      </button>

                      {customer.status === "Active" ? (
                        <button
                          className="freeze-btn"
                          onClick={() => freezeCustomer(customer.id)}
                        >
                          Freeze
                        </button>
                      ) : (
                        <button
                          className="unfreeze-btn"
                          onClick={() => unfreezeCustomer(customer.id)}
                        >
                          Unfreeze
                        </button>
                      )}

                      <button
                        className="delete-btn"
                        onClick={() => deleteCustomer(customer.id)}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
