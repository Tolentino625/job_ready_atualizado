const AUTH_TOKEN_KEY = "jobready_token";
const AUTH_USER_KEY = "jobready_user";

function getAuthToken() {
  return localStorage.getItem(AUTH_TOKEN_KEY);
}

function getAuthUser() {
  try {
    return JSON.parse(localStorage.getItem(AUTH_USER_KEY) || "null");
  } catch (_) {
    return null;
  }
}

function authHeaders(extra = {}) {
  const headers = { ...extra };
  const token = getAuthToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  return headers;
}

function salvarSessao(payload) {
  localStorage.setItem(AUTH_TOKEN_KEY, payload.token);
  localStorage.setItem(AUTH_USER_KEY, JSON.stringify(payload.usuario));
}

function limparSessao() {
  localStorage.removeItem(AUTH_TOKEN_KEY);
  localStorage.removeItem(AUTH_USER_KEY);
}

function exigirLogin() {
  if (!getAuthToken()) {
    window.location.replace("login.html");
    return false;
  }
  return true;
}

async function logout() {
  try {
    await fetch(`${API_BASE_URL}/api/auth/logout`, {
      method: "POST",
      headers: authHeaders(),
    });
  } catch (_) {
    // Mesmo se a API estiver desligada, a sessão local será encerrada.
  } finally {
    limparSessao();
    window.location.replace("login.html");
  }
}

document.addEventListener("DOMContentLoaded", exigirLogin);
