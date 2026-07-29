import { useEffect, useState } from "react";
import { getApiUrl } from "../utils/api";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import "./Messages.css";

export default function Messages() {
  const [users, setUsers] = useState([]);
  const [messages, setMessages] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [reply, setReply] = useState("");
  const [loading, setLoading] = useState(false);
  const [unreadByUser, setUnreadByUser] = useState({});

  useEffect(() => {
    loadUsers();
    // light refresh of customer list every 15s
    const t = setInterval(loadUsers, 15000);
    return () => clearInterval(t);
  }, []);

  async function loadUsers() {
    try {
      const response = await fetch(`${getApiUrl()}/api/admin/customers`);
      const data = await response.json();
      setUsers(Array.isArray(data) ? data : []);
    } catch (error) {
      console.log(error);
    }
  }

  async function markRead(userId) {
    try {
      await fetch(`${getApiUrl()}/api/chat/read/${userId}`, {
        method: "PUT",
      });
    } catch (error) {
      console.log(error);
    }
  }

  async function loadMessages(user) {
    setSelectedUser(user.id);
    setSelectedCustomer(user);
    setLoading(true);

    try {
      const response = await fetch(`${getApiUrl()}/api/chat/${user.id}`);
      const data = await response.json();
      setMessages(Array.isArray(data) ? data : []);

      // Mark customer messages as read so the bell count drops
      await markRead(user.id);
      setUnreadByUser((prev) => ({ ...prev, [user.id]: 0 }));
    } catch (error) {
      console.log(error);
      setMessages([]);
    } finally {
      setLoading(false);
    }
  }

  async function sendReply() {
    if (!reply.trim() || !selectedUser) return;

    try {
      await fetch(`${getApiUrl()}/api/chat/send`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: selectedUser,
          sender: "Admin",
          message: reply,
        }),
      });
      setReply("");
      if (selectedCustomer) {
        loadMessages(selectedCustomer);
      }
    } catch (error) {
      console.log(error);
      alert("Failed to send reply");
    }
  }

  return (
    <div className="admin-layout">
      <Sidebar />

      <div className="main-content">
        <Topbar />

        <div className="messages-page">
          <h1>Customer Messages</h1>

          <div className="messages-layout">
            <div className="customers-list">
              <h2>Customers</h2>

              {users.length === 0 ? (
                <p style={{ color: "#94a3b8", padding: 12 }}>No customers yet</p>
              ) : (
                users.map((user) => (
                  <div
                    key={user.id}
                    className={
                      selectedUser === user.id
                        ? "customer-item active-chat"
                        : "customer-item"
                    }
                    onClick={() => loadMessages(user)}
                  >
                    <h3>
                      {user.name}
                      {unreadByUser[user.id] > 0 ? (
                        <span
                          style={{
                            marginLeft: 8,
                            background: "#ef4444",
                            color: "white",
                            borderRadius: 999,
                            padding: "2px 8px",
                            fontSize: 12,
                          }}
                        >
                          {unreadByUser[user.id]}
                        </span>
                      ) : null}
                    </h3>
                    <p>{user.email}</p>
                  </div>
                ))
              )}
            </div>

            <div className="conversation">
              {selectedUser ? (
                <>
                  <div className="chat-header">
                    <h2>{selectedCustomer?.name}</h2>
                    <p>Customer conversation</p>
                  </div>

                  <div className="conversation-box">
                    {loading ? (
                      <h3>Loading messages...</h3>
                    ) : messages.length === 0 ? (
                      <p>No messages yet</p>
                    ) : (
                      messages.map((msg) => (
                        <div
                          key={msg.id}
                          className={
                            msg.sender === "Admin" ? "admin-msg" : "customer-msg"
                          }
                        >
                          <p>{msg.message}</p>
                          <span>
                            {msg.sender}
                            {msg.time ? ` · ${msg.time}` : ""}
                          </span>
                        </div>
                      ))
                    )}
                  </div>

                  <div className="reply-box">
                    <input
                      placeholder="Reply to customer..."
                      value={reply}
                      onChange={(e) => setReply(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") sendReply();
                      }}
                    />
                    <button onClick={sendReply}>Send</button>
                  </div>
                </>
              ) : (
                <div className="empty-chat">
                  <h2>Select a customer to view messages</h2>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
