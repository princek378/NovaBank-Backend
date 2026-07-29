const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";

export function getApiUrl() {
  return API_URL;
}

export async function api(endpoint, options = {}) {
  const token = localStorage.getItem("token");
  const response = await fetch(API_URL + endpoint, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.message || data.error || "Request failed");
  }
  return data;
}

export default api;
