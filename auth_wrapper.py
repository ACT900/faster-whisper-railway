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
<title>Faster Whisper</title>
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg-deep: #0F172A;
  --bg-card: #1E293B;
  --bg-inset: #0F172A;
  --border: #334155;
  --border-focus: #3B82F6;
  --text-primary: #F8FAFC;
  --text-secondary: #94A3B8;
  --text-muted: #64748B;
  --cta: #22C55E;
  --cta-hover: #16A34A;
  --accent: #3B82F6;
  --error: #EF4444;
  --error-bg: rgba(239,68,68,0.1);
  --success: #22C55E;
  --success-bg: rgba(34,197,94,0.1);
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  background: var(--bg-deep);
  color: var(--text-primary);
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  line-height: 1.6;
  position: relative;
  overflow: hidden;
}

/* Subtle animated gradient orbs */
body::before, body::after {
  content: "";
  position: fixed;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.15;
  pointer-events: none;
  animation: drift 20s ease-in-out infinite alternate;
}
body::before {
  width: 600px; height: 600px;
  background: var(--accent);
  top: -200px; right: -100px;
}
body::after {
  width: 500px; height: 500px;
  background: #8B5CF6;
  bottom: -200px; left: -100px;
  animation-delay: -10s;
  animation-direction: alternate-reverse;
}

@keyframes drift {
  0% { transform: translate(0, 0) scale(1); }
  100% { transform: translate(40px, 30px) scale(1.1); }
}

.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 2.5rem 2rem 2rem;
  max-width: 420px;
  width: 100%;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1), 0 24px 48px rgba(0,0,0,0.3);
  position: relative;
  z-index: 1;
  animation: cardIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;
}

@keyframes cardIn {
  from { opacity: 0; transform: translateY(16px) scale(0.98); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

/* SVG icon container */
.icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(59,130,246,0.1);
  border: 1px solid rgba(59,130,246,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.25rem;
}

.icon-wrap svg {
  width: 24px;
  height: 24px;
  color: var(--accent);
}

h1 {
  font-size: 1.375rem;
  font-weight: 700;
  margin-bottom: 0.375rem;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}

.subtitle {
  color: var(--text-secondary);
  font-size: 0.875rem;
  margin-bottom: 1.5rem;
}

.steps {
  background: var(--bg-inset);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1rem 1.125rem;
  margin-bottom: 1.5rem;
}

.steps-label {
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-muted);
  margin-bottom: 0.625rem;
}

.step {
  display: flex;
  align-items: flex-start;
  gap: 0.625rem;
  padding: 0.3rem 0;
}

.step-num {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--accent);
  color: #fff;
  font-size: 0.6875rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 2px;
}

.step-text {
  font-size: 0.8125rem;
  color: var(--text-secondary);
  line-height: 1.5;
}

.step-text strong {
  color: var(--text-primary);
  font-weight: 600;
}

/* Input with lock icon */
.input-wrap {
  position: relative;
  margin-bottom: 0.875rem;
}

.input-wrap svg.lock {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  color: var(--text-muted);
  pointer-events: none;
  transition: color 0.2s;
}

.input-wrap input {
  width: 100%;
  padding: 0.75rem 2.5rem 0.75rem 2.25rem;
  background: var(--bg-inset);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.875rem;
  font-family: inherit;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.input-wrap input:focus {
  border-color: var(--border-focus);
  box-shadow: 0 0 0 3px rgba(59,130,246,0.15);
}

.input-wrap input:focus ~ svg.lock { color: var(--accent); }

.input-wrap input::placeholder { color: var(--text-muted); }

.toggle-vis {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0.375rem;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s, background 0.2s;
}

.toggle-vis:hover { color: var(--text-secondary); background: rgba(148,163,184,0.1); }
.toggle-vis:focus-visible { outline: 2px solid var(--accent); outline-offset: 1px; }
.toggle-vis svg { width: 16px; height: 16px; }

button.submit {
  width: 100%;
  padding: 0.75rem;
  background: var(--cta);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: background 0.2s, box-shadow 0.2s, transform 0.1s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

button.submit:hover { background: var(--cta-hover); box-shadow: 0 0 20px rgba(34,197,94,0.2); }
button.submit:active { transform: scale(0.99); }
button.submit:focus-visible { outline: 2px solid var(--cta); outline-offset: 2px; }
button.submit:disabled {
  background: var(--border);
  color: var(--text-muted);
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}

.btn-spinner {
  display: none;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

.btn-spinner.visible { display: inline-block; }

.msg {
  font-size: 0.8125rem;
  margin-top: 0.75rem;
  padding: 0.625rem 0.75rem;
  border-radius: 8px;
  display: none;
  line-height: 1.5;
}

.msg.error {
  display: block;
  background: var(--error-bg);
  border: 1px solid rgba(239,68,68,0.3);
  color: var(--error);
}

.msg.success {
  display: block;
  background: var(--success-bg);
  border: 1px solid rgba(34,197,94,0.3);
  color: var(--success);
}

.footer {
  margin-top: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  font-size: 0.6875rem;
  color: var(--text-muted);
}

.footer svg { width: 12px; height: 12px; flex-shrink: 0; }

.footer a {
  color: var(--text-secondary);
  text-decoration: none;
  transition: color 0.2s;
}

.footer a:hover { color: var(--text-primary); }

@keyframes spin { to { transform: rotate(360deg); } }

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}

@media (max-width: 480px) {
  .card { padding: 2rem 1.25rem 1.5rem; border-radius: 12px; }
  h1 { font-size: 1.25rem; }
}
</style>
</head>
<body>
<div class="card" role="main">
  <div class="icon-wrap">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/>
      <path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/>
    </svg>
  </div>
  <h1>Your Speech-to-Text API is Ready</h1>
  <p class="subtitle">Enter your API key to access the transcription playground.</p>

  <div class="steps">
    <div class="steps-label">Where to find your API key</div>
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
    <div class="input-wrap">
      <svg class="lock" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>
      </svg>
      <input type="password" id="keyInput" placeholder="Paste your API key" autofocus required aria-label="API key">
      <button type="button" class="toggle-vis" id="toggleBtn" title="Show or hide key" aria-label="Toggle key visibility">
        <svg id="eyeIcon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"/>
          <circle cx="12" cy="12" r="3"/>
        </svg>
      </button>
    </div>
    <button type="submit" class="submit" id="submitBtn">
      <span class="btn-spinner" id="spinner"></span>
      <span id="btnText">Sign in</span>
    </button>
  </form>

  <div id="msg" class="msg" role="alert" aria-live="polite"></div>

  <div class="footer">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
    </svg>
    <span>Private &amp; encrypted</span>
    <span style="margin: 0 0.125rem">&middot;</span>
    <a href="https://github.com/SYSTRAN/faster-whisper" target="_blank" rel="noopener">Faster Whisper</a>
    <span style="margin: 0 0.125rem">&middot;</span>
    <a href="https://github.com/speaches-ai/speaches" target="_blank" rel="noopener">Speaches</a>
  </div>
</div>

<script>
var form = document.getElementById('loginForm');
var input = document.getElementById('keyInput');
var btn = document.getElementById('submitBtn');
var btnText = document.getElementById('btnText');
var spinner = document.getElementById('spinner');
var msg = document.getElementById('msg');
var eyeIcon = document.getElementById('eyeIcon');

document.getElementById('toggleBtn').addEventListener('click', function() {
  var isPassword = input.type === 'password';
  input.type = isPassword ? 'text' : 'password';
  this.setAttribute('aria-label', isPassword ? 'Hide key' : 'Show key');
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
  btnText.textContent = loading ? 'Verifying\u2026' : 'Sign in';
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
