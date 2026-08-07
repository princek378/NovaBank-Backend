import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import Landing from "./pages/Landing";
import Login from "./auth/Login";
import Register from "./auth/Register";
import ForgotPassword from "./auth/ForgotPassword";
import GuestSupport from "./pages/GuestSupport";
import SupportDesk from "./pages/SupportDesk";

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

import ProtectedRoute from "./components/ProtectedRoute";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public */}
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/support" element={<GuestSupport />} />
        <Route path="/support-desk" element={<SupportDesk />} />

        {/* Secret Admin Login */}
        <Route path="/secure-admin-portal" element={<AdminLogin />} />

        {/* Block old admin login path */}
        <Route path="/admin/login" element={<Navigate to="/" replace />} />

        {/* Block bare /admin path */}
        <Route path="/admin" element={<Navigate to="/" replace />} />

        {/* Protected Admin pages */}
        <Route
          path="/admin/dashboard"
          element={
            <ProtectedRoute role="Admin">
              <AdminDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/customers"
          element={
            <ProtectedRoute role="Admin">
              <Customers />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/customers/:id"
          element={
            <ProtectedRoute role="Admin">
              <CustomerProfile />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/new-customer"
          element={
            <ProtectedRoute role="Admin">
              <NewCustomer />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/transactions"
          element={
            <ProtectedRoute role="Admin">
              <Transactions />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/reports"
          element={
            <ProtectedRoute role="Admin">
              <Reports />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/messages"
          element={
            <ProtectedRoute role="Admin">
              <Messages />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/settings"
          element={
            <ProtectedRoute role="Admin">
              <Settings />
            </ProtectedRoute>
          }
        />

        {/* Customer pages */}
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
