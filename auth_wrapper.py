"""Auth wrapper for Speaches — adds a login gate for Railway template users.

Wraps the Speaches FastAPI app with middleware that:
1. Serves a login page at /login for unauthenticated users
2. Validates API keys and sets auth cookies
3. Passes through API requests with Bearer tokens
4. Passes through health check and docs endpoints
5. Serves the custom frontend at / for authenticated users
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


APP_HTML = """<!DOCTYPE html>
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
  padding: 0;
  line-height: 1.6;
  position: relative;
  overflow-x: hidden;
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

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes cardIn {
  from { opacity: 0; transform: translateY(16px) scale(0.98); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

/* Layout */
.app-wrap {
  max-width: 720px;
  width: 100%;
  margin: 0 auto;
  padding: 2rem 1.5rem 3rem;
  position: relative;
  z-index: 1;
  animation: cardIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;
}

/* Header */
.app-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 1.75rem;
}

.app-header-left h1 {
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text-primary);
  margin-bottom: 0.125rem;
}

.app-header-left .app-subtitle {
  font-size: 0.8125rem;
  color: var(--text-secondary);
}

.sign-out-btn {
  background: none;
  border: 1px solid var(--border);
  color: var(--text-secondary);
  font-size: 0.75rem;
  font-family: inherit;
  font-weight: 500;
  padding: 0.375rem 0.75rem;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.375rem;
  transition: color 0.2s, border-color 0.2s, background 0.2s;
  flex-shrink: 0;
  margin-top: 0.25rem;
}

.sign-out-btn:hover {
  color: var(--text-primary);
  border-color: var(--text-muted);
  background: rgba(148,163,184,0.05);
}

.sign-out-btn:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.sign-out-btn svg {
  width: 14px;
  height: 14px;
}

/* Tabs */
.tab-bar {
  display: flex;
  gap: 0.25rem;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 0.25rem;
  margin-bottom: 1.5rem;
}

.tab-btn {
  flex: 1;
  background: none;
  border: none;
  color: var(--text-muted);
  font-family: inherit;
  font-size: 0.8125rem;
  font-weight: 500;
  padding: 0.5rem 0.75rem;
  border-radius: 7px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  transition: color 0.2s, background 0.2s;
}

.tab-btn:hover {
  color: var(--text-secondary);
}

.tab-btn:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: -2px;
}

.tab-btn[aria-selected="true"] {
  background: var(--bg-inset);
  color: var(--text-primary);
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}

.tab-btn svg {
  width: 15px;
  height: 15px;
  flex-shrink: 0;
}

.tab-panel {
  display: none;
}

.tab-panel.active {
  display: block;
}

/* Card sections */
.section-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1rem;
}

/* Drop zone */
.drop-zone {
  border: 2px dashed var(--border);
  border-radius: 10px;
  padding: 2.5rem 1.5rem;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
  position: relative;
}

.drop-zone:hover,
.drop-zone.dragover {
  border-color: var(--accent);
  background: rgba(59,130,246,0.05);
}

.drop-zone.has-file {
  border-style: solid;
  border-color: var(--border);
  padding: 1rem 1.5rem;
  cursor: default;
}

.drop-zone-icon {
  width: 48px;
  height: 48px;
  color: var(--text-muted);
  margin: 0 auto 1rem;
  transition: color 0.2s;
}

.drop-zone:hover .drop-zone-icon,
.drop-zone.dragover .drop-zone-icon {
  color: var(--accent);
}

.drop-zone-text {
  font-size: 0.9375rem;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 0.375rem;
}

.drop-zone-hint {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.drop-zone input[type="file"] {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
}

.drop-zone.has-file input[type="file"] {
  display: none;
}

/* File info */
.file-info {
  display: none;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
}

.file-info.visible {
  display: flex;
}

.file-info-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: rgba(59,130,246,0.1);
  border: 1px solid rgba(59,130,246,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.file-info-icon svg {
  width: 18px;
  height: 18px;
  color: var(--accent);
}

.file-info-details {
  flex: 1;
  min-width: 0;
}

.file-info-name {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-info-size {
  font-size: 0.6875rem;
  color: var(--text-muted);
}

.file-remove-btn {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0.375rem;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s, background 0.2s;
  flex-shrink: 0;
}

.file-remove-btn:hover {
  color: var(--error);
  background: var(--error-bg);
}

.file-remove-btn:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 1px;
}

.file-remove-btn svg {
  width: 16px;
  height: 16px;
}

/* Settings (collapsible) */
.settings-toggle {
  width: 100%;
  cursor: pointer;
  list-style: none;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--text-muted);
  padding: 0.75rem 0 0;
  display: flex;
  align-items: center;
  gap: 0.375rem;
  transition: color 0.2s;
  user-select: none;
}

.settings-toggle:hover {
  color: var(--text-secondary);
}

.settings-toggle::-webkit-details-marker {
  display: none;
}

.settings-toggle svg {
  width: 14px;
  height: 14px;
  transition: transform 0.2s;
}

details[open] .settings-toggle svg {
  transform: rotate(90deg);
}

.settings-body {
  padding: 0.75rem 0 0.25rem;
  display: flex;
  gap: 0.75rem;
}

.settings-field {
  flex: 1;
}

.settings-field label {
  display: block;
  font-size: 0.6875rem;
  font-weight: 500;
  color: var(--text-muted);
  margin-bottom: 0.375rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.settings-field select {
  width: 100%;
  padding: 0.5rem 0.625rem;
  background: var(--bg-inset);
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 0.8125rem;
  font-family: inherit;
  outline: none;
  cursor: pointer;
  transition: border-color 0.2s;
  -webkit-appearance: none;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2364748B' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.5rem center;
  padding-right: 1.75rem;
}

.settings-field select:focus {
  border-color: var(--border-focus);
}

.settings-field select option {
  background: var(--bg-card);
  color: var(--text-primary);
}

/* Primary action button */
.action-btn {
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
  margin-top: 1rem;
}

.action-btn:hover:not(:disabled) {
  background: var(--cta-hover);
  box-shadow: 0 0 20px rgba(34,197,94,0.2);
}

.action-btn:active:not(:disabled) {
  transform: scale(0.99);
}

.action-btn:focus-visible {
  outline: 2px solid var(--cta);
  outline-offset: 2px;
}

.action-btn:disabled {
  background: var(--border);
  color: var(--text-muted);
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}

.action-btn .btn-spinner {
  display: none;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

.action-btn .btn-spinner.visible {
  display: inline-block;
}

/* Error / status messages */
.status-msg {
  font-size: 0.8125rem;
  margin-top: 0.75rem;
  padding: 0.625rem 0.75rem;
  border-radius: 8px;
  display: none;
  line-height: 1.5;
}

.status-msg.error {
  display: block;
  background: var(--error-bg);
  border: 1px solid rgba(239,68,68,0.3);
  color: var(--error);
}

.status-msg.success {
  display: block;
  background: var(--success-bg);
  border: 1px solid rgba(34,197,94,0.3);
  color: var(--success);
}

/* Result area */
.result-area {
  display: none;
  margin-top: 1rem;
}

.result-area.visible {
  display: block;
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.result-label {
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-muted);
}

.result-actions {
  display: flex;
  gap: 0.375rem;
}

.result-action-btn {
  background: none;
  border: 1px solid var(--border);
  color: var(--text-secondary);
  font-size: 0.6875rem;
  font-family: inherit;
  font-weight: 500;
  padding: 0.25rem 0.5rem;
  border-radius: 5px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  transition: color 0.2s, border-color 0.2s, background 0.2s;
}

.result-action-btn:hover {
  color: var(--text-primary);
  border-color: var(--text-muted);
  background: rgba(148,163,184,0.05);
}

.result-action-btn:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 1px;
}

.result-action-btn svg {
  width: 12px;
  height: 12px;
}

.result-text {
  background: var(--bg-inset);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1rem;
  font-family: "SF Mono", "Fira Code", "Fira Mono", "Roboto Mono", "Courier New", monospace;
  font-size: 0.8125rem;
  line-height: 1.7;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 400px;
  overflow-y: auto;
}

/* TTS section */
.tts-textarea {
  width: 100%;
  min-height: 120px;
  padding: 0.875rem;
  background: var(--bg-inset);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.875rem;
  font-family: inherit;
  line-height: 1.6;
  outline: none;
  resize: vertical;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.tts-textarea:focus {
  border-color: var(--border-focus);
  box-shadow: 0 0 0 3px rgba(59,130,246,0.15);
}

.tts-textarea::placeholder {
  color: var(--text-muted);
}

.tts-settings {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.75rem;
}

.tts-settings .settings-field {
  flex: 1;
}

.tts-settings .settings-field.voice-field {
  flex: 2;
}

/* Speed slider */
.speed-wrap {
  display: flex;
  flex-direction: column;
}

.speed-label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.speed-value {
  font-size: 0.75rem;
  color: var(--text-secondary);
  font-weight: 500;
  font-variant-numeric: tabular-nums;
}

.speed-slider {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: var(--bg-inset);
  border: 1px solid var(--border);
  outline: none;
  cursor: pointer;
  margin-top: 0.25rem;
}

.speed-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--accent);
  border: 2px solid var(--bg-card);
  cursor: pointer;
  box-shadow: 0 1px 4px rgba(0,0,0,0.3);
  transition: transform 0.1s;
}

.speed-slider::-webkit-slider-thumb:hover {
  transform: scale(1.15);
}

.speed-slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--accent);
  border: 2px solid var(--bg-card);
  cursor: pointer;
  box-shadow: 0 1px 4px rgba(0,0,0,0.3);
}

.speed-slider:focus-visible {
  box-shadow: 0 0 0 3px rgba(59,130,246,0.3);
}

/* Audio player */
.audio-result {
  display: none;
  margin-top: 1rem;
}

.audio-result.visible {
  display: block;
}

.audio-result audio {
  width: 100%;
  border-radius: 8px;
  margin-bottom: 0.5rem;
}

.download-audio-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  background: none;
  border: 1px solid var(--border);
  color: var(--text-secondary);
  font-size: 0.75rem;
  font-family: inherit;
  font-weight: 500;
  padding: 0.375rem 0.75rem;
  border-radius: 6px;
  cursor: pointer;
  transition: color 0.2s, border-color 0.2s, background 0.2s;
}

.download-audio-btn:hover {
  color: var(--text-primary);
  border-color: var(--text-muted);
  background: rgba(148,163,184,0.05);
}

.download-audio-btn:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 1px;
}

.download-audio-btn svg {
  width: 14px;
  height: 14px;
}

/* Footer */
.app-footer {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  font-size: 0.6875rem;
  color: var(--text-muted);
  flex-wrap: wrap;
}

.app-footer a {
  color: var(--text-secondary);
  text-decoration: none;
  transition: color 0.2s;
}

.app-footer a:hover {
  color: var(--text-primary);
}

.app-footer .dot {
  margin: 0 0.125rem;
}

/* Responsive */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}

@media (max-width: 600px) {
  .app-wrap {
    padding: 1.25rem 1rem 2rem;
  }

  .app-header-left h1 {
    font-size: 1.25rem;
  }

  .section-card {
    padding: 1.125rem;
  }

  .settings-body {
    flex-direction: column;
    gap: 0.5rem;
  }

  .tts-settings {
    flex-direction: column;
    gap: 0.5rem;
  }

  .drop-zone {
    padding: 2rem 1rem;
  }
}
</style>
</head>
<body>
<div class="app-wrap">
  <!-- Header -->
  <header class="app-header">
    <div class="app-header-left">
      <h1>Faster Whisper</h1>
      <p class="app-subtitle">Speech-to-Text and Text-to-Speech</p>
    </div>
    <button type="button" class="sign-out-btn" id="signOutBtn" aria-label="Sign out">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" x2="9" y1="12" y2="12"/></svg>
      Sign out
    </button>
  </header>

  <!-- Tab bar -->
  <div class="tab-bar" role="tablist" aria-label="Features">
    <button type="button" class="tab-btn" role="tab" id="tabTranscribe" aria-selected="true" aria-controls="panelTranscribe">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/></svg>
      Transcribe
    </button>
    <button type="button" class="tab-btn" role="tab" id="tabTTS" aria-selected="false" aria-controls="panelTTS">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>
      Text-to-Speech
    </button>
  </div>

  <!-- Transcribe panel -->
  <div class="tab-panel active" role="tabpanel" id="panelTranscribe" aria-labelledby="tabTranscribe">
    <div class="section-card">
      <!-- Drop zone -->
      <div class="drop-zone" id="dropZone">
        <svg class="drop-zone-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" id="dropIcon"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/></svg>
        <div id="dropText">
          <p class="drop-zone-text">Drop an audio file here or click to browse</p>
          <p class="drop-zone-hint">MP3, WAV, M4A, FLAC, OGG, WEBM</p>
        </div>
        <div class="file-info" id="fileInfo">
          <div class="file-info-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
          </div>
          <div class="file-info-details">
            <div class="file-info-name" id="fileName"></div>
            <div class="file-info-size" id="fileSize"></div>
          </div>
          <button type="button" class="file-remove-btn" id="fileRemoveBtn" aria-label="Remove file">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" x2="6" y1="6" y2="18"/><line x1="6" x2="18" y1="6" y2="18"/></svg>
          </button>
        </div>
        <input type="file" id="fileInput" accept="audio/*,.mp3,.wav,.m4a,.flac,.ogg,.webm" aria-label="Choose audio file">
      </div>

      <!-- Settings -->
      <details>
        <summary class="settings-toggle">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="9 18 15 12 9 6"/></svg>
          Settings
        </summary>
        <div class="settings-body">
          <div class="settings-field">
            <label for="langSelect">Language</label>
            <select id="langSelect">
              <option value="">Auto-detect</option>
              <option value="en">English</option>
              <option value="es">Spanish</option>
              <option value="fr">French</option>
              <option value="de">German</option>
              <option value="it">Italian</option>
              <option value="pt">Portuguese</option>
              <option value="ja">Japanese</option>
              <option value="zh">Chinese</option>
              <option value="ko">Korean</option>
              <option value="ar">Arabic</option>
              <option value="hi">Hindi</option>
              <option value="ru">Russian</option>
              <option value="nl">Dutch</option>
              <option value="pl">Polish</option>
              <option value="tr">Turkish</option>
              <option value="vi">Vietnamese</option>
              <option value="th">Thai</option>
              <option value="uk">Ukrainian</option>
              <option value="sv">Swedish</option>
            </select>
          </div>
          <div class="settings-field">
            <label for="formatSelect">Format</label>
            <select id="formatSelect">
              <option value="text">Plain Text</option>
              <option value="srt">SRT Subtitles</option>
              <option value="vtt">VTT Subtitles</option>
              <option value="json">JSON</option>
              <option value="verbose_json">Verbose JSON</option>
            </select>
          </div>
        </div>
      </details>

      <!-- Transcribe button -->
      <button type="button" class="action-btn" id="transcribeBtn" disabled>
        <span class="btn-spinner" id="transcribeSpinner"></span>
        <span id="transcribeBtnText">Transcribe</span>
      </button>

      <!-- Status / error -->
      <div class="status-msg" id="transcribeStatus" role="alert" aria-live="polite"></div>

      <!-- Result -->
      <div class="result-area" id="transcribeResult">
        <div class="result-header">
          <span class="result-label">Transcription</span>
          <div class="result-actions">
            <button type="button" class="result-action-btn" id="copyBtn" aria-label="Copy to clipboard">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
              <span>Copy</span>
            </button>
            <button type="button" class="result-action-btn" id="downloadTextBtn" aria-label="Download file" style="display:none">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>
              <span>Download</span>
            </button>
          </div>
        </div>
        <div class="result-text" id="resultText"></div>
      </div>
    </div>
  </div>

  <!-- TTS panel -->
  <div class="tab-panel" role="tabpanel" id="panelTTS" aria-labelledby="tabTTS">
    <div class="section-card">
      <textarea class="tts-textarea" id="ttsInput" placeholder="Type or paste the text you want to hear spoken..." aria-label="Text to speak"></textarea>

      <div class="tts-settings">
        <div class="settings-field voice-field">
          <label for="voiceSelect">Voice</label>
          <select id="voiceSelect">
            <optgroup label="American English - Female">
              <option value="af_heart" selected>Heart</option>
              <option value="af_alloy">Alloy</option>
              <option value="af_aoede">Aoede</option>
              <option value="af_bella">Bella</option>
              <option value="af_jessica">Jessica</option>
              <option value="af_kore">Kore</option>
              <option value="af_nicole">Nicole</option>
              <option value="af_nova">Nova</option>
              <option value="af_river">River</option>
              <option value="af_sarah">Sarah</option>
              <option value="af_sky">Sky</option>
            </optgroup>
            <optgroup label="American English - Male">
              <option value="am_adam">Adam</option>
              <option value="am_echo">Echo</option>
              <option value="am_eric">Eric</option>
              <option value="am_fenrir">Fenrir</option>
              <option value="am_liam">Liam</option>
              <option value="am_michael">Michael</option>
              <option value="am_onyx">Onyx</option>
              <option value="am_puck">Puck</option>
              <option value="am_santa">Santa</option>
            </optgroup>
            <optgroup label="British English - Female">
              <option value="bf_alice">Alice</option>
              <option value="bf_emma">Emma</option>
              <option value="bf_isabella">Isabella</option>
              <option value="bf_lily">Lily</option>
            </optgroup>
            <optgroup label="British English - Male">
              <option value="bm_daniel">Daniel</option>
              <option value="bm_fable">Fable</option>
              <option value="bm_george">George</option>
              <option value="bm_lewis">Lewis</option>
            </optgroup>
            <optgroup label="Japanese - Female">
              <option value="jf_alpha">Alpha</option>
              <option value="jf_gongitsune">Gongitsune</option>
              <option value="jf_nezumi">Nezumi</option>
              <option value="jf_tebukuro">Tebukuro</option>
            </optgroup>
            <optgroup label="Japanese - Male">
              <option value="jm_kumo">Kumo</option>
            </optgroup>
            <optgroup label="Chinese - Female">
              <option value="zf_xiaobei">Xiaobei</option>
              <option value="zf_xiaoni">Xiaoni</option>
              <option value="zf_xiaoxiao">Xiaoxiao</option>
              <option value="zf_xiaoyi">Xiaoyi</option>
            </optgroup>
            <optgroup label="Chinese - Male">
              <option value="zm_yunjian">Yunjian</option>
              <option value="zm_yunxi">Yunxi</option>
              <option value="zm_yunxia">Yunxia</option>
              <option value="zm_yunyang">Yunyang</option>
            </optgroup>
            <optgroup label="Spanish">
              <option value="ef_dora">Dora</option>
              <option value="em_alex">Alex</option>
              <option value="em_santa">Santa</option>
            </optgroup>
            <optgroup label="French">
              <option value="ff_siwis">Siwis</option>
            </optgroup>
            <optgroup label="Hindi">
              <option value="hf_alpha">Alpha</option>
              <option value="hf_beta">Beta</option>
              <option value="hm_omega">Omega</option>
              <option value="hm_psi">Psi</option>
            </optgroup>
            <optgroup label="Italian">
              <option value="if_sara">Sara</option>
              <option value="im_nicola">Nicola</option>
            </optgroup>
            <optgroup label="Portuguese">
              <option value="pf_dora">Dora</option>
              <option value="pm_alex">Alex</option>
              <option value="pm_santa">Santa</option>
            </optgroup>
          </select>
        </div>
        <div class="settings-field speed-wrap">
          <div class="speed-label-row">
            <label for="speedSlider">Speed</label>
            <span class="speed-value" id="speedValue">1.0x</span>
          </div>
          <input type="range" class="speed-slider" id="speedSlider" min="0.5" max="2.0" step="0.1" value="1.0" aria-label="Speech speed">
        </div>
      </div>

      <!-- Generate button -->
      <button type="button" class="action-btn" id="ttsBtn" disabled>
        <span class="btn-spinner" id="ttsSpinner"></span>
        <span id="ttsBtnText">Generate Speech</span>
      </button>

      <!-- Status / error -->
      <div class="status-msg" id="ttsStatus" role="alert" aria-live="polite"></div>

      <!-- Audio result -->
      <div class="audio-result" id="ttsResult">
        <audio controls id="ttsAudio"></audio>
        <button type="button" class="download-audio-btn" id="downloadAudioBtn">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>
          Download MP3
        </button>
      </div>
    </div>
  </div>

  <!-- Footer -->
  <footer class="app-footer">
    <span>Powered by</span>
    <a href="https://github.com/SYSTRAN/faster-whisper" target="_blank" rel="noopener">Faster Whisper</a>
    <span class="dot">&middot;</span>
    <a href="https://github.com/speaches-ai/speaches" target="_blank" rel="noopener">Speaches</a>
    <span class="dot">&middot;</span>
    <a href="/docs">API Docs</a>
  </footer>
</div>

<script>
/* =============================================
   Auth
   ============================================= */
var apiKey = '';
try { apiKey = localStorage.getItem('speaches_api_key') || ''; } catch(e) {}

function authHeaders() {
  var h = {};
  if (apiKey) { h['Authorization'] = 'Bearer ' + apiKey; }
  return h;
}

function handleAuthError(res) {
  if (res.status === 401) {
    try { localStorage.removeItem('speaches_api_key'); } catch(e) {}
    window.location.href = '/login';
    return true;
  }
  return false;
}

document.getElementById('signOutBtn').addEventListener('click', function() {
  fetch('/auth/logout', { method: 'POST' }).finally(function() {
    try { localStorage.removeItem('speaches_api_key'); } catch(e) {}
    window.location.href = '/login';
  });
});

/* =============================================
   Tabs
   ============================================= */
var tabBtns = [document.getElementById('tabTranscribe'), document.getElementById('tabTTS')];
var panels = [document.getElementById('panelTranscribe'), document.getElementById('panelTTS')];

function switchTab(index) {
  for (var i = 0; i < tabBtns.length; i++) {
    tabBtns[i].setAttribute('aria-selected', i === index ? 'true' : 'false');
    if (i === index) {
      panels[i].classList.add('active');
    } else {
      panels[i].classList.remove('active');
    }
  }
}

tabBtns[0].addEventListener('click', function() { switchTab(0); });
tabBtns[1].addEventListener('click', function() { switchTab(1); });

/* =============================================
   Utilities
   ============================================= */
function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function showStatus(el, text, type) {
  el.textContent = text;
  el.className = 'status-msg ' + type;
}

function hideStatus(el) {
  el.className = 'status-msg';
  el.textContent = '';
}

function friendlyError(err) {
  if (!err) return 'Something went wrong. Please try again.';
  var msg = String(err.message || err);
  if (msg.indexOf('Failed to fetch') !== -1 || msg.indexOf('NetworkError') !== -1) {
    return 'Could not connect to the server. Please check your connection and try again.';
  }
  return msg;
}

function triggerDownload(blob, filename) {
  var url = URL.createObjectURL(blob);
  var a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  setTimeout(function() { URL.revokeObjectURL(url); }, 5000);
}

function copyToClipboard(text, btnSpan) {
  var originalText = btnSpan.textContent;
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(function() {
      btnSpan.textContent = 'Copied';
      setTimeout(function() { btnSpan.textContent = originalText; }, 2000);
    }).catch(function() {
      fallbackCopy(text, btnSpan, originalText);
    });
  } else {
    fallbackCopy(text, btnSpan, originalText);
  }
}

function fallbackCopy(text, btnSpan, originalText) {
  var ta = document.createElement('textarea');
  ta.value = text;
  ta.style.position = 'fixed';
  ta.style.opacity = '0';
  document.body.appendChild(ta);
  ta.select();
  try {
    document.execCommand('copy');
    btnSpan.textContent = 'Copied';
    setTimeout(function() { btnSpan.textContent = originalText; }, 2000);
  } catch(e) {}
  document.body.removeChild(ta);
}

/* =============================================
   Transcribe — File handling
   ============================================= */
var dropZone = document.getElementById('dropZone');
var dropIcon = document.getElementById('dropIcon');
var dropText = document.getElementById('dropText');
var fileInfo = document.getElementById('fileInfo');
var fileInput = document.getElementById('fileInput');
var fileNameEl = document.getElementById('fileName');
var fileSizeEl = document.getElementById('fileSize');
var fileRemoveBtn = document.getElementById('fileRemoveBtn');
var transcribeBtn = document.getElementById('transcribeBtn');
var transcribeSpinner = document.getElementById('transcribeSpinner');
var transcribeBtnText = document.getElementById('transcribeBtnText');
var transcribeStatus = document.getElementById('transcribeStatus');
var transcribeResult = document.getElementById('transcribeResult');
var resultText = document.getElementById('resultText');
var copyBtn = document.getElementById('copyBtn');
var downloadTextBtn = document.getElementById('downloadTextBtn');
var langSelect = document.getElementById('langSelect');
var formatSelect = document.getElementById('formatSelect');

var selectedFile = null;
var transcriptionText = '';

function setFile(file) {
  if (!file) { clearFile(); return; }
  selectedFile = file;
  fileNameEl.textContent = file.name;
  fileSizeEl.textContent = formatFileSize(file.size);
  dropZone.classList.add('has-file');
  dropIcon.style.display = 'none';
  dropText.style.display = 'none';
  fileInfo.classList.add('visible');
  transcribeBtn.disabled = false;
  hideStatus(transcribeStatus);
}

function clearFile() {
  selectedFile = null;
  fileInput.value = '';
  dropZone.classList.remove('has-file');
  dropIcon.style.display = '';
  dropText.style.display = '';
  fileInfo.classList.remove('visible');
  transcribeBtn.disabled = true;
}

fileInput.addEventListener('change', function() {
  if (this.files && this.files[0]) setFile(this.files[0]);
});

fileRemoveBtn.addEventListener('click', function(e) {
  e.stopPropagation();
  clearFile();
});

/* Drag and drop */
dropZone.addEventListener('dragover', function(e) {
  e.preventDefault();
  e.stopPropagation();
  if (!dropZone.classList.contains('has-file')) {
    dropZone.classList.add('dragover');
  }
});

dropZone.addEventListener('dragleave', function(e) {
  e.preventDefault();
  e.stopPropagation();
  dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', function(e) {
  e.preventDefault();
  e.stopPropagation();
  dropZone.classList.remove('dragover');
  if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0]) {
    setFile(e.dataTransfer.files[0]);
  }
});

/* =============================================
   Transcribe — API call
   ============================================= */
transcribeBtn.addEventListener('click', function() {
  if (!selectedFile || transcribeBtn.disabled) return;

  var format = formatSelect.value;
  var lang = langSelect.value;

  /* Clear previous */
  transcribeResult.classList.remove('visible');
  resultText.textContent = '';
  hideStatus(transcribeStatus);
  transcriptionText = '';

  /* Loading state */
  transcribeBtn.disabled = true;
  transcribeSpinner.className = 'btn-spinner visible';
  transcribeBtnText.textContent = 'Transcribing...';

  var formData = new FormData();
  formData.append('file', selectedFile);
  formData.append('model', 'Systran/faster-whisper-base');
  if (lang) formData.append('language', lang);
  formData.append('response_format', format);

  fetch('/v1/audio/transcriptions', {
    method: 'POST',
    headers: authHeaders(),
    body: formData
  })
  .then(function(res) {
    if (handleAuthError(res)) return;
    if (!res.ok) {
      return res.text().then(function(t) {
        var detail = '';
        try { detail = JSON.parse(t).detail || JSON.parse(t).message || t; } catch(e) { detail = t; }
        throw new Error(detail || 'Transcription failed (status ' + res.status + ')');
      });
    }
    if (format === 'json' || format === 'verbose_json') {
      return res.json().then(function(data) { return { parsed: data, format: format }; });
    }
    return res.text().then(function(t) { return { text: t, format: format }; });
  })
  .then(function(result) {
    if (!result) return;

    var output = '';
    if (result.parsed) {
      if (result.format === 'json') {
        output = result.parsed.text || JSON.stringify(result.parsed, null, 2);
      } else {
        output = JSON.stringify(result.parsed, null, 2);
      }
    } else {
      output = result.text;
    }

    transcriptionText = output;
    resultText.textContent = output;
    transcribeResult.classList.add('visible');

    /* Show download button for structured formats */
    if (format === 'srt' || format === 'vtt' || format === 'json' || format === 'verbose_json') {
      downloadTextBtn.style.display = '';
    } else {
      downloadTextBtn.style.display = 'none';
    }

    /* Reset button */
    transcribeBtn.disabled = false;
    transcribeSpinner.className = 'btn-spinner';
    transcribeBtnText.textContent = 'Transcribe';
  })
  .catch(function(err) {
    showStatus(transcribeStatus, friendlyError(err), 'error');
    transcribeBtn.disabled = false;
    transcribeSpinner.className = 'btn-spinner';
    transcribeBtnText.textContent = 'Transcribe';
  });
});

/* Copy button */
copyBtn.addEventListener('click', function() {
  if (transcriptionText) {
    var span = copyBtn.querySelector('span');
    copyToClipboard(transcriptionText, span);
  }
});

/* Download text button */
downloadTextBtn.addEventListener('click', function() {
  if (!transcriptionText) return;
  var format = formatSelect.value;
  var ext = format;
  if (format === 'verbose_json') ext = 'json';
  var mime = 'text/plain';
  if (ext === 'json') mime = 'application/json';
  if (ext === 'srt') mime = 'text/srt';
  if (ext === 'vtt') mime = 'text/vtt';
  var baseName = selectedFile ? selectedFile.name.replace(/\\.[^.]+$/, '') : 'transcription';
  triggerDownload(new Blob([transcriptionText], { type: mime }), baseName + '.' + ext);
});

/* =============================================
   TTS — Controls
   ============================================= */
var ttsInput = document.getElementById('ttsInput');
var voiceSelect = document.getElementById('voiceSelect');
var speedSlider = document.getElementById('speedSlider');
var speedValue = document.getElementById('speedValue');
var ttsBtn = document.getElementById('ttsBtn');
var ttsSpinner = document.getElementById('ttsSpinner');
var ttsBtnText = document.getElementById('ttsBtnText');
var ttsStatus = document.getElementById('ttsStatus');
var ttsResult = document.getElementById('ttsResult');
var ttsAudio = document.getElementById('ttsAudio');
var downloadAudioBtn = document.getElementById('downloadAudioBtn');

var ttsAudioBlob = null;
var ttsAudioUrl = null;

speedSlider.addEventListener('input', function() {
  speedValue.textContent = parseFloat(this.value).toFixed(1) + 'x';
});

ttsInput.addEventListener('input', function() {
  ttsBtn.disabled = !this.value.trim();
});

/* =============================================
   TTS — API call
   ============================================= */
ttsBtn.addEventListener('click', function() {
  var text = ttsInput.value.trim();
  if (!text || ttsBtn.disabled) return;

  /* Clear previous */
  hideStatus(ttsStatus);
  ttsResult.classList.remove('visible');
  if (ttsAudioUrl) { URL.revokeObjectURL(ttsAudioUrl); ttsAudioUrl = null; }
  ttsAudioBlob = null;

  /* Loading state */
  ttsBtn.disabled = true;
  ttsSpinner.className = 'btn-spinner visible';
  ttsBtnText.textContent = 'Generating...';

  var headers = authHeaders();
  headers['Content-Type'] = 'application/json';

  fetch('/v1/audio/speech', {
    method: 'POST',
    headers: headers,
    body: JSON.stringify({
      input: text,
      model: 'tts-1',
      voice: voiceSelect.value,
      speed: parseFloat(speedSlider.value),
      response_format: 'mp3'
    })
  })
  .then(function(res) {
    if (handleAuthError(res)) return;
    if (!res.ok) {
      return res.text().then(function(t) {
        var detail = '';
        try { detail = JSON.parse(t).detail || JSON.parse(t).message || t; } catch(e) { detail = t; }
        throw new Error(detail || 'Speech generation failed (status ' + res.status + ')');
      });
    }
    return res.blob();
  })
  .then(function(blob) {
    if (!blob) return;
    ttsAudioBlob = blob;
    ttsAudioUrl = URL.createObjectURL(blob);
    ttsAudio.src = ttsAudioUrl;
    ttsResult.classList.add('visible');

    /* Reset button */
    ttsBtn.disabled = false;
    ttsSpinner.className = 'btn-spinner';
    ttsBtnText.textContent = 'Generate Speech';
  })
  .catch(function(err) {
    showStatus(ttsStatus, friendlyError(err), 'error');
    ttsBtn.disabled = false;
    ttsSpinner.className = 'btn-spinner';
    ttsBtnText.textContent = 'Generate Speech';
  });
});

/* Download audio */
downloadAudioBtn.addEventListener('click', function() {
  if (!ttsAudioBlob) return;
  triggerDownload(ttsAudioBlob, 'speech.mp3');
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

        # No API key configured — skip auth, serve app at root
        if not API_KEY:
            if path == "/":
                return HTMLResponse(APP_HTML)
            return await call_next(request)

        # API clients using Bearer token — let Speaches handle auth
        if request.headers.get("authorization", "").startswith("Bearer "):
            return await call_next(request)

        # Valid auth cookie — serve app at root, pass through API calls
        if request.cookies.get(COOKIE_NAME) == COOKIE_VALUE:
            if path == "/":
                return HTMLResponse(APP_HTML)
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
