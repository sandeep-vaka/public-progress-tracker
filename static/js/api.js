const API_BASE = "/api";

function getToken() { return localStorage.getItem("token"); }
function setToken(t) { localStorage.setItem("token", t); }
function clearToken() { localStorage.removeItem("token"); localStorage.removeItem("user"); }
function getUser() { return JSON.parse(localStorage.getItem("user") || "null"); }
function setUser(u) { localStorage.setItem("user", JSON.stringify(u)); }

async function request(path, options = {}) {
  const token = getToken();
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Request failed");
  return data;
}

const api = {
  signup: (body) => request("/auth/signup", { method: "POST", body: JSON.stringify(body) }),
  login:  (body) => request("/auth/login",  { method: "POST", body: JSON.stringify(body) }),

  getMyProgress:    ()     => request("/progress/"),
  createProgress:   (body) => request("/progress/",    { method: "POST",   body: JSON.stringify(body) }),
  updateProgress:   (id, body) => request(`/progress/${id}`, { method: "PUT", body: JSON.stringify(body) }),
  deleteProgress:   (id)   => request(`/progress/${id}`, { method: "DELETE" }),
  getPublicProgress: ()    => request("/progress/public"),
};
