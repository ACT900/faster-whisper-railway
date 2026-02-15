"""Auth wrapper for Speaches — adds a login gate for Railway template users.

Wraps the Speaches FastAPI app with middleware that:
1. Serves a login page at /login for unauthenticated users
2. Validates API keys and sets auth cookies
3. Passes through API requests with Bearer tokens
4. Passes through health check and docs endpoints
"""

import hashlib
import json
import os

from fastapi import Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

API_KEY = os.environ.get("API_KEY", "")
COOKIE_NAME = "fw_auth"
COOKIE_VALUE = hashlib.sha256(f"fw:{API_KEY}".encode()).hexdigest()[:32] if API_KEY else ""
COOKIE_MAX_AGE = 30 * 24 * 60 * 60  # 30 days

# Paths that never require authentication
OPEN_PATHS = frozenset({
    "/login",
    "/auth/validate",
    "/auth/logout",
    "/health",
    "/docs",
    "/openapi.json",
    "/favicon.ico",
})


LOGIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Faster Whisper — Login</title>
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  background: #0d1117;
  color: #e6edf3;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  line-height: 1.5;
}

.card {
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 12px;
  padding: 2.5rem 2rem;
  max-width: 440px;
  width: 100%;
  box-shadow: 0 8px 24px rgba(0,0,0,0.4);
}

.icon {
  font-size: 2.5rem;
  margin-bottom: 0.75rem;
}

h1 {
  font-size: 1.375rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #f0f6fc;
}

.subtitle {
  color: #8b949e;
  font-size: 0.9rem;
  margin-bottom: 1.75rem;
}

.steps {
  background: #0d1117;
  border: 1px solid #30363d;
  border-radius: 8px;
  padding: 1rem 1.25rem;
  margin-bottom: 1.75rem;
}

.steps-title {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #8b949e;
  margin-bottom: 0.75rem;
}

.step {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.4rem 0;
}

.step-num {
  flex-shrink: 0;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #1f6feb;
  color: #fff;
  font-size: 0.7rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 1px;
}

.step-text {
  font-size: 0.85rem;
  color: #c9d1d9;
}

.step-text strong {
  color: #e6edf3;
}

.input-group {
  position: relative;
  margin-bottom: 1rem;
}

.input-group input {
  width: 100%;
  padding: 0.7rem 2.5rem 0.7rem 0.85rem;
  background: #0d1117;
  border: 1px solid #30363d;
  border-radius: 6px;
  color: #e6edf3;
  font-size: 0.9rem;
  font-family: inherit;
  outline: none;
  transition: border-color 0.15s;
}

.input-group input:focus {
  border-color: #1f6feb;
  box-shadow: 0 0 0 3px rgba(31,111,235,0.15);
}

.input-group input::placeholder {
  color: #484f58;
}

.toggle-vis {
  position: absolute;
  right: 0.6rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #8b949e;
  cursor: pointer;
  padding: 0.25rem;
  font-size: 1rem;
  line-height: 1;
}

.toggle-vis:hover { color: #c9d1d9; }

button.submit {
  width: 100%;
  padding: 0.7rem;
  background: #238636;
  color: #fff;
  border: 1px solid rgba(240,246,252,0.1);
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: background 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
}

button.submit:hover { background: #2ea043; }
button.submit:active { background: #238636; }
button.submit:disabled {
  background: #21262d;
  color: #484f58;
  cursor: not-allowed;
  border-color: #30363d;
}

.btn-spinner {
  display: none;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

.btn-spinner.visible { display: inline-block; }

.msg {
  font-size: 0.8rem;
  margin-top: 0.75rem;
  padding: 0.6rem 0.75rem;
  border-radius: 6px;
  display: none;
}

.msg.error {
  display: block;
  background: rgba(248,81,73,0.1);
  border: 1px solid rgba(248,81,73,0.4);
  color: #f85149;
}

.msg.success {
  display: block;
  background: rgba(63,185,80,0.1);
  border: 1px solid rgba(63,185,80,0.4);
  color: #3fb950;
}

.footer {
  margin-top: 1.5rem;
  text-align: center;
  font-size: 0.75rem;
  color: #484f58;
}

.footer a {
  color: #58a6ff;
  text-decoration: none;
}

.footer a:hover { text-decoration: underline; }

@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 480px) {
  .card { padding: 1.75rem 1.25rem; }
  h1 { font-size: 1.2rem; }
}
</style>
</head>
<body>
<div class="card">
  <div class="icon">&#127908;</div>
  <h1>Your Speech-to-Text API is Ready</h1>
  <p class="subtitle">Enter your API key to access the transcription playground.</p>

  <div class="steps">
    <div class="steps-title">Where to find your API key</div>
    <div class="step">
      <span class="step-num">1</span>
      <span class="step-text">Open your <strong>Railway dashboard</strong></span>
    </div>
    <div class="step">
      <span class="step-num">2</span>
      <span class="step-text">Click the <strong>Faster Whisper</strong> service</span>
    </div>
    <div class="step">
      <span class="step-num">3</span>
      <span class="step-text">Go to <strong>Variables</strong> tab &rarr; copy <strong>API_KEY</strong></span>
    </div>
  </div>

  <form id="loginForm" autocomplete="off">
    <div class="input-group">
      <input type="password" id="keyInput" placeholder="Paste your API key here" autofocus required>
      <button type="button" class="toggle-vis" id="toggleBtn" title="Show/hide key">&#128065;</button>
    </div>
    <button type="submit" class="submit" id="submitBtn">
      <span class="btn-spinner" id="spinner"></span>
      <span id="btnText">Sign in</span>
    </button>
  </form>

  <div id="msg" class="msg"></div>

  <div class="footer">
    Powered by <a href="https://github.com/SYSTRAN/faster-whisper" target="_blank" rel="noopener">Faster Whisper</a>
    &middot; <a href="https://github.com/speaches-ai/speaches" target="_blank" rel="noopener">Speaches</a>
  </div>
</div>

<script>
var form = document.getElementById('loginForm');
var input = document.getElementById('keyInput');
var btn = document.getElementById('submitBtn');
var btnText = document.getElementById('btnText');
var spinner = document.getElementById('spinner');
var msg = document.getElementById('msg');

document.getElementById('toggleBtn').addEventListener('click', function() {
  input.type = input.type === 'password' ? 'text' : 'password';
});

function showMsg(text, type) {
  msg.textContent = text;
  msg.className = 'msg ' + type;
}

function hideMsg() {
  msg.className = 'msg';
  msg.textContent = '';
}

function setLoading(loading) {
  btn.disabled = loading;
  spinner.className = loading ? 'btn-spinner visible' : 'btn-spinner';
  btnText.textContent = loading ? 'Checking\u2026' : 'Sign in';
}

form.addEventListener('submit', function(e) {
  e.preventDefault();
  var key = input.value.trim();
  if (!key) return;

  setLoading(true);
  hideMsg();

  fetch('/auth/validate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ key: key })
  })
  .then(function(res) {
    if (res.ok) {
      try { localStorage.setItem('speaches_api_key', key); } catch (_) {}
      showMsg('Authenticated! Redirecting\u2026', 'success');
      setTimeout(function() { window.location.href = '/'; }, 600);
    } else {
      showMsg('Invalid API key. Check your Railway Variables tab and try again.', 'error');
      setLoading(false);
    }
  })
  .catch(function() {
    showMsg('Connection error. Please try again.', 'error');
    setLoading(false);
  });
});
</script>
</body>
</html>"""


class AuthGateMiddleware(BaseHTTPMiddleware):
    """Redirects unauthenticated browser requests to the login page.

    Passes through:
    - Requests to open paths (login, health, docs)
    - Requests with a valid auth cookie
    - Requests with an Authorization header (API clients)
    - All requests when API_KEY is not configured
    """

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Always allow open paths
        if path in OPEN_PATHS:
            return await self._handle_auth_routes(request, path, call_next)

        # No API key configured — skip auth entirely
        if not API_KEY:
            return await call_next(request)

        # API clients using Bearer token — let Speaches handle auth
        if request.headers.get("authorization", "").startswith("Bearer "):
            return await call_next(request)

        # Valid auth cookie — pass through
        if request.cookies.get(COOKIE_NAME) == COOKIE_VALUE:
            return await call_next(request)

        # Unauthenticated — redirect to login
        return RedirectResponse("/login", status_code=302)

    async def _handle_auth_routes(self, request: Request, path: str, call_next):
        """Handle login page and auth endpoints directly in middleware."""
        if path == "/login":
            # If already authenticated, redirect to app
            if API_KEY and request.cookies.get(COOKIE_NAME) == COOKIE_VALUE:
                return RedirectResponse("/", status_code=302)
            if not API_KEY:
                return RedirectResponse("/", status_code=302)
            return HTMLResponse(LOGIN_HTML)

        if path == "/auth/validate" and request.method == "POST":
            try:
                body = await request.body()
                data = json.loads(body)
            except (json.JSONDecodeError, UnicodeDecodeError):
                return JSONResponse(
                    {"valid": False, "error": "Invalid request"}, status_code=400
                )

            if data.get("key") == API_KEY:
                response = JSONResponse({"valid": True})
                response.set_cookie(
                    COOKIE_NAME,
                    COOKIE_VALUE,
                    max_age=COOKIE_MAX_AGE,
                    httponly=True,
                    samesite="lax",
                    secure=True,
                )
                return response
            return JSONResponse(
                {"valid": False, "error": "Invalid API key"}, status_code=401
            )

        if path == "/auth/logout" and request.method == "POST":
            response = JSONResponse({"success": True})
            response.delete_cookie(COOKIE_NAME)
            return response

        # All other open paths — pass through to Speaches
        return await call_next(request)


def create_app():
    """Factory function that wraps Speaches with auth middleware."""
    from speaches.main import create_app as create_speaches_app

    app = create_speaches_app()
    app.add_middleware(AuthGateMiddleware)
    return app
