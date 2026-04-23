"""Codex (ChatGPT Pro/Plus) OAuth client.

Logs into OpenAI's Codex backend — the same endpoint the Codex CLI /
opencode use to consume ChatGPT subscription credits instead of API
credits. Supports both:

  * browser flow  — PKCE + local callback on port 1455 (default)
  * device flow   — for headless environments; shows a user_code to
                    enter at auth.openai.com/codex/device

Storage:
  ~/.hadron/codex_auth.json   {
      "access_token": "...",
      "refresh_token": "...",
      "id_token": "...",
      "account_id": "...",
      "expires_at": <epoch seconds>
  }

Also reads ~/.codex/auth.json (Codex CLI's own store) as a fallback
so users already logged in via `codex login` don't need to repeat it.

CLI:
    python scripts/codex_oauth.py login            # browser flow
    python scripts/codex_oauth.py login --device   # device flow
    python scripts/codex_oauth.py status
    python scripts/codex_oauth.py logout
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import hashlib
import http.server
import json
import os
import secrets
import sys
import threading
import time
import urllib.parse
import urllib.request
import webbrowser
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

ISSUER = "https://auth.openai.com"
CLIENT_ID = "app_EMoamEEZ73f0CkXaXp7hrann"  # public — same id Codex CLI + opencode use
CODEX_API_BASE = "https://chatgpt.com/backend-api/codex"
CODEX_RESPONSES_URL = f"{CODEX_API_BASE}/responses"
DEFAULT_PORT = 1455
DEFAULT_SCOPES = "openid profile email offline_access"
TOKEN_LIFETIME_SAFETY_S = 300  # refresh if <5 min remaining

HADRON_HOME = Path(os.environ.get("HADRON_HOME", Path.home() / ".hadron"))
HADRON_AUTH_PATH = Path(os.environ.get("CODEX_AUTH_PATH", HADRON_HOME / "codex_auth.json"))
CODEX_CLI_AUTH_PATH = Path.home() / ".codex" / "auth.json"


# ---------------------------------------------------------------------------
# auth file
# ---------------------------------------------------------------------------

@dataclass
class CodexAuth:
    access_token: str
    refresh_token: str
    id_token: str = ""
    account_id: Optional[str] = None
    expires_at: float = 0.0

    def needs_refresh(self) -> bool:
        return time.time() > (self.expires_at - TOKEN_LIFETIME_SAFETY_S)

    def to_json(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}


def load_auth() -> Optional[CodexAuth]:
    # Prefer our own store.
    if HADRON_AUTH_PATH.exists():
        data = json.loads(HADRON_AUTH_PATH.read_text())
        return CodexAuth(**data)
    # Fallback: Codex CLI's auth.json.
    if CODEX_CLI_AUTH_PATH.exists():
        raw = json.loads(CODEX_CLI_AUTH_PATH.read_text())
        tokens = raw.get("tokens") or raw
        access = tokens.get("access_token") or raw.get("access")
        refresh = tokens.get("refresh_token") or raw.get("refresh")
        id_tok = tokens.get("id_token") or ""
        if not (access and refresh):
            return None
        account = raw.get("accountId") or _extract_account_id(id_tok or access)
        raw_expires = raw.get("expires") or raw.get("last_refresh") or 0
        # Codex CLI may store 'expires' as a number (epoch ms) OR as an ISO
        # string. Accept both; fall back to 0 if unparseable.
        expires: float = 0.0
        try:
            if isinstance(raw_expires, (int, float)):
                expires = float(raw_expires)
            elif isinstance(raw_expires, str) and raw_expires:
                # Try numeric string first.
                try:
                    expires = float(raw_expires)
                except ValueError:
                    import datetime as _dt
                    iso = raw_expires.replace("Z", "+00:00")
                    expires = _dt.datetime.fromisoformat(iso).timestamp()
        except Exception:  # noqa: BLE001
            expires = 0.0
        if expires > 10**11:   # epoch ms → seconds
            expires /= 1000.0
        return CodexAuth(
            access_token=access,
            refresh_token=refresh,
            id_token=id_tok,
            account_id=account,
            expires_at=float(expires or 0),
        )
    return None


def save_auth(auth: CodexAuth) -> None:
    HADRON_AUTH_PATH.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    HADRON_AUTH_PATH.write_text(json.dumps(auth.to_json(), indent=2))
    os.chmod(HADRON_AUTH_PATH, 0o600)


def clear_auth() -> None:
    if HADRON_AUTH_PATH.exists():
        HADRON_AUTH_PATH.unlink()


# ---------------------------------------------------------------------------
# JWT helpers (account_id extraction)
# ---------------------------------------------------------------------------

def _b64url_decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


def _parse_jwt_claims(token: str) -> dict:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return {}
        return json.loads(_b64url_decode(parts[1]))
    except Exception:  # noqa: BLE001
        return {}


def _extract_account_id(token: str) -> Optional[str]:
    claims = _parse_jwt_claims(token)
    if not claims:
        return None
    acc = claims.get("chatgpt_account_id")
    if acc:
        return acc
    nested = claims.get("https://api.openai.com/auth") or {}
    if isinstance(nested, dict) and nested.get("chatgpt_account_id"):
        return nested["chatgpt_account_id"]
    orgs = claims.get("organizations") or []
    if orgs and isinstance(orgs, list):
        return orgs[0].get("id")
    return None


# ---------------------------------------------------------------------------
# PKCE
# ---------------------------------------------------------------------------

def _gen_verifier(n: int = 64) -> str:
    return secrets.token_urlsafe(n)[:96]


def _challenge_for(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


# ---------------------------------------------------------------------------
# token endpoint
# ---------------------------------------------------------------------------

def _post_token(body: dict) -> dict:
    req = urllib.request.Request(
        f"{ISSUER}/oauth/token",
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=urllib.parse.urlencode(body).encode(),
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def _exchange_code(code: str, redirect_uri: str, verifier: str) -> dict:
    return _post_token({
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": CLIENT_ID,
        "code_verifier": verifier,
    })


def _refresh(refresh_token: str) -> dict:
    return _post_token({
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": CLIENT_ID,
    })


def _tokens_to_auth(tokens: dict, prior: Optional[CodexAuth] = None) -> CodexAuth:
    access = tokens.get("access_token") or ""
    refresh = tokens.get("refresh_token") or (prior.refresh_token if prior else "")
    id_token = tokens.get("id_token") or (prior.id_token if prior else "")
    account = _extract_account_id(id_token) or _extract_account_id(access) \
              or (prior.account_id if prior else None)
    expires_in = int(tokens.get("expires_in") or 3600)
    return CodexAuth(
        access_token=access,
        refresh_token=refresh,
        id_token=id_token,
        account_id=account,
        expires_at=time.time() + expires_in,
    )


def ensure_fresh(auth: CodexAuth) -> CodexAuth:
    """Refresh the access token if it's expired/near-expiry, persist, return."""
    if not auth.needs_refresh():
        return auth
    tokens = _refresh(auth.refresh_token)
    new = _tokens_to_auth(tokens, prior=auth)
    save_auth(new)
    return new


# ---------------------------------------------------------------------------
# browser flow (localhost callback)
# ---------------------------------------------------------------------------

class _CallbackHandler(http.server.BaseHTTPRequestHandler):
    received: dict = {}

    def log_message(self, *args, **kwargs):  # silence stdout noise
        pass

    def do_GET(self):  # noqa: N802
        url = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(url.query)
        if url.path == "/auth/callback":
            _CallbackHandler.received = {
                "code": (qs.get("code") or [""])[0],
                "state": (qs.get("state") or [""])[0],
                "error": (qs.get("error") or [""])[0],
                "error_description": (qs.get("error_description") or [""])[0],
            }
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                b"<!doctype html><meta charset=utf-8>"
                b"<title>Hadron \xe2\x80\x94 Codex sign-in</title>"
                b"<style>body{font-family:system-ui;display:flex;align-items:center;"
                b"justify-content:center;height:100vh;margin:0;background:#0b0e14;color:#e6e7ea}"
                b"div{text-align:center}</style>"
                b"<div><h1>Signed in.</h1><p>You can close this tab and return "
                b"to the terminal.</p></div>"
            )
        else:
            self.send_response(404)
            self.end_headers()


def login_browser(port: int = DEFAULT_PORT, timeout_s: int = 300) -> CodexAuth:
    verifier = _gen_verifier()
    challenge = _challenge_for(verifier)
    state = secrets.token_urlsafe(32)
    redirect_uri = f"http://localhost:{port}/auth/callback"
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": redirect_uri,
        "scope": DEFAULT_SCOPES,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "id_token_add_organizations": "true",
        "codex_cli_simplified_flow": "true",
        "originator": "hadron",
        "state": state,
    }
    auth_url = f"{ISSUER}/oauth/authorize?{urllib.parse.urlencode(params)}"

    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), _CallbackHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        print(f"\nOpening browser to sign in to ChatGPT…\n\n{auth_url}\n")
        try:
            webbrowser.open(auth_url)
        except Exception:  # noqa: BLE001
            print("Could not open browser automatically. Visit the URL above.")
        deadline = time.time() + timeout_s
        while not _CallbackHandler.received and time.time() < deadline:
            time.sleep(0.3)
    finally:
        server.shutdown()
        server.server_close()

    if not _CallbackHandler.received:
        raise TimeoutError("OAuth login timed out — no callback received")
    got = _CallbackHandler.received
    _CallbackHandler.received = {}
    if got.get("error"):
        raise RuntimeError(f"OAuth error: {got['error']}  {got.get('error_description','')}")
    if got.get("state") != state:
        raise RuntimeError("OAuth state mismatch — potential CSRF; aborting")
    if not got.get("code"):
        raise RuntimeError("OAuth callback missing authorization code")

    tokens = _exchange_code(got["code"], redirect_uri, verifier)
    auth = _tokens_to_auth(tokens)
    save_auth(auth)
    return auth


# ---------------------------------------------------------------------------
# device flow (headless)
# ---------------------------------------------------------------------------

def login_device(poll_s: int = 5, timeout_s: int = 900) -> CodexAuth:
    resp = _http_post_json(
        f"{ISSUER}/api/accounts/deviceauth/usercode",
        {"client_id": CLIENT_ID},
    )
    device_auth_id = resp["device_auth_id"]
    user_code = resp["user_code"]
    interval = max(int(resp.get("interval") or poll_s), 1) + 3  # +3s safety

    print("\nGo to: " + f"{ISSUER}/codex/device")
    print(f"Enter code: {user_code}\n")

    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            r = _http_post_json(
                f"{ISSUER}/api/accounts/deviceauth/token",
                {"device_auth_id": device_auth_id, "user_code": user_code},
            )
            # 200 = success payload with authorization_code + code_verifier
            tokens = _exchange_code(r["authorization_code"],
                                    f"{ISSUER}/deviceauth/callback",
                                    r["code_verifier"])
            auth = _tokens_to_auth(tokens)
            save_auth(auth)
            return auth
        except urllib.error.HTTPError as e:  # noqa: PERF203
            if e.code not in (403, 404):  # pending = 403/404
                raise
        time.sleep(interval)
    raise TimeoutError("Device-code OAuth timed out")


def _http_post_json(url: str, body: dict) -> dict:
    req = urllib.request.Request(
        url, method="POST",
        headers={"Content-Type": "application/json",
                 "User-Agent": "hadron/0.1"},
        data=json.dumps(body).encode(),
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cmd_login(args):
    if args.device:
        login_device()
    else:
        login_browser()
    auth = load_auth()
    if auth:
        print(f"✓ signed in  account={auth.account_id or '(unknown)'}  "
              f"expires in {int(auth.expires_at - time.time())}s")


def _cmd_status(_):
    auth = load_auth()
    if not auth:
        print("✗ not signed in")
        return 2
    fresh_in = int(auth.expires_at - time.time())
    src = HADRON_AUTH_PATH if HADRON_AUTH_PATH.exists() else CODEX_CLI_AUTH_PATH
    print(f"✓ signed in")
    print(f"  source:     {src}")
    print(f"  account_id: {auth.account_id or '(unknown)'}")
    print(f"  expires in: {fresh_in}s ({'needs refresh' if auth.needs_refresh() else 'fresh'})")


def _cmd_logout(_):
    clear_auth()
    print("✓ local auth cleared (note: ~/.codex/auth.json is NOT touched)")


def main(argv=None):
    p = argparse.ArgumentParser(description="Hadron Codex OAuth client")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_login = sub.add_parser("login", help="sign in to ChatGPT")
    p_login.add_argument("--device", action="store_true",
                         help="use device flow instead of browser (for headless)")
    p_login.set_defaults(func=_cmd_login)

    sub.add_parser("status", help="show current auth status").set_defaults(func=_cmd_status)
    sub.add_parser("logout", help="remove local auth").set_defaults(func=_cmd_logout)

    args = p.parse_args(argv)
    return args.func(args) or 0


if __name__ == "__main__":
    sys.exit(main())
