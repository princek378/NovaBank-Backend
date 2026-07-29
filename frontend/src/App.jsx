import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import Landing from "./pages/Landing";
import Login from "./auth/Login";
import Register from "./auth/Register";

import AdminLogin from "./admin/AdminLogin";
import AdminDashboard from "./admin/AdminDashboard";
import Customers from "./admin/Customers";
import CustomerProfile from "./admin/CustomerProfile";
import NewCustomer from "./admin/NewCustomer";
import Transactions from "./admin/Transactions";
import Reports from "./admin/Reports";
import Messages from "./admin/Messages";
import Settings from "./admin/Settings";

import CustomerDashboard from "./customer/CustomerDashboard";
import Transfer from "./customer/Transfer";
import Deposit from "./customer/Deposit";
import Withdraw from "./customer/Withdraw";
import Chat from "./customer/Chat";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public */}
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/admin/login" element={<AdminLogin />} />

        {/* Admin */}
        <Route path="/admin" element={<Navigate to="/admin/dashboard" replace />} />
        <Route path="/admin/dashboard" element={<AdminDashboard />} />
        <Route path="/admin/customers" element={<Customers />} />
        <Route path="/admin/customers/:id" element={<CustomerProfile />} />
        <Route path="/admin/new-customer" element={<NewCustomer />} />
        <Route path="/admin/transactions" element={<Transactions />} />
        <Route path="/admin/reports" element={<Reports />} />
        <Route path="/admin/messages" element={<Messages />} />
        <Route path="/admin/settings" element={<Settings />} />

        {/* Customer */}
        <Route path="/customer/dashboard" element={<CustomerDashboard />} />
        <Route path="/customer/transfer" element={<Transfer />} />
        <Route path="/customer/deposit" element={<Deposit />} />
        <Route path="/customer/withdraw" element={<Withdraw />} />
        <Route path="/customer/chat" element={<Chat />} />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
