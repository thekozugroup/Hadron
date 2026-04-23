# Copyright 2026-present, thekozugroup
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Unit tests for the Codex OAuth + LLM wrappers.

These never hit the real Codex endpoint or OpenAI auth servers — all
network calls are mocked. We verify:

  * codex_oauth.load_auth() reads both our auth file and ~/.codex/auth.json
  * save_auth / ensure_fresh round-trip correctly (refresh-only path)
  * codex_llm._messages_to_input maps roles and text correctly
  * codex_llm._extract_output_text / _extract_reasoning parse Responses API
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest

SCRIPTS = Path(__file__).resolve().parents[5] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from codex_oauth import (  # noqa: E402
    CodexAuth, HADRON_AUTH_PATH, _parse_jwt_claims,
    _extract_account_id, load_auth, save_auth, clear_auth, ensure_fresh,
)
from codex_llm import (  # noqa: E402
    CodexOAuthLLM, _extract_output_text, _extract_reasoning,
)


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_hadron_home(tmp_path, monkeypatch):
    """Redirect auth storage to a temp dir so tests don't touch ~/.hadron."""
    auth_path = tmp_path / "codex_auth.json"
    monkeypatch.setattr("codex_oauth.HADRON_AUTH_PATH", auth_path)
    monkeypatch.setattr("codex_oauth.CODEX_CLI_AUTH_PATH", tmp_path / "codex_cli_auth.json")
    return auth_path


# ---------------------------------------------------------------------------
# auth file I/O
# ---------------------------------------------------------------------------

def test_save_and_load_roundtrip(tmp_hadron_home):
    auth = CodexAuth(
        access_token="a.b.c",
        refresh_token="refresh-xyz",
        id_token="",
        account_id="acc_123",
        expires_at=time.time() + 3600,
    )
    save_auth(auth)
    assert tmp_hadron_home.exists()
    assert oct(tmp_hadron_home.stat().st_mode)[-3:] == "600"

    loaded = load_auth()
    assert loaded is not None
    assert loaded.access_token == "a.b.c"
    assert loaded.refresh_token == "refresh-xyz"
    assert loaded.account_id == "acc_123"


def test_load_falls_back_to_codex_cli_auth(tmp_path, monkeypatch):
    hadron_path = tmp_path / "hadron_auth.json"
    cli_path = tmp_path / "codex_cli_auth.json"
    monkeypatch.setattr("codex_oauth.HADRON_AUTH_PATH", hadron_path)
    monkeypatch.setattr("codex_oauth.CODEX_CLI_AUTH_PATH", cli_path)

    cli_path.write_text(json.dumps({
        "tokens": {
            "access_token": "aa.bb.cc",
            "refresh_token": "refresh-cli",
            "id_token": "",
        },
        "accountId": "acc_from_cli",
        "expires": (time.time() + 3600) * 1000,  # CLI stores ms
    }))
    auth = load_auth()
    assert auth is not None
    assert auth.refresh_token == "refresh-cli"
    assert auth.account_id == "acc_from_cli"


def test_clear_auth_is_idempotent(tmp_hadron_home):
    # works even when nothing stored
    clear_auth()
    save_auth(CodexAuth(access_token="x", refresh_token="y", expires_at=0))
    assert tmp_hadron_home.exists()
    clear_auth()
    assert not tmp_hadron_home.exists()


def test_ensure_fresh_skips_refresh_when_not_needed(tmp_hadron_home):
    auth = CodexAuth(
        access_token="fresh",
        refresh_token="r",
        expires_at=time.time() + 3600,  # well-within lifetime
    )
    save_auth(auth)

    with patch("codex_oauth._refresh") as m:
        got = ensure_fresh(auth)
        m.assert_not_called()
    assert got.access_token == "fresh"


def test_ensure_fresh_triggers_refresh_when_near_expiry(tmp_hadron_home):
    auth = CodexAuth(
        access_token="stale",
        refresh_token="old-refresh",
        expires_at=time.time() + 60,  # <5 min → needs refresh
    )
    with patch("codex_oauth._refresh", return_value={
        "access_token": "new-access",
        "refresh_token": "new-refresh",
        "id_token": "",
        "expires_in": 3600,
    }) as m:
        got = ensure_fresh(auth)
    m.assert_called_once_with("old-refresh")
    assert got.access_token == "new-access"
    assert got.refresh_token == "new-refresh"
    assert got.expires_at > time.time() + 60  # pushed well into the future


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------

def test_extract_account_id_from_id_token():
    import base64
    payload = {"chatgpt_account_id": "acc_direct", "organizations": [{"id": "org_x"}]}
    enc = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    jwt = f"header.{enc}.sig"
    assert _extract_account_id(jwt) == "acc_direct"


def test_extract_account_id_falls_back_to_organizations():
    import base64
    payload = {"organizations": [{"id": "org_first"}, {"id": "org_second"}]}
    enc = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    assert _extract_account_id(f"h.{enc}.s") == "org_first"


def test_parse_jwt_claims_tolerates_bad_tokens():
    assert _parse_jwt_claims("") == {}
    assert _parse_jwt_claims("onepart") == {}
    assert _parse_jwt_claims("a.notbase64.b") == {}


# ---------------------------------------------------------------------------
# message → Responses API adapter
# ---------------------------------------------------------------------------

def test_messages_to_input_maps_system_to_developer():
    msgs = [
        {"role": "system", "content": "be terse"},
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hello"},
    ]
    out = CodexOAuthLLM._messages_to_input(msgs)
    assert [m["role"] for m in out] == ["developer", "user", "assistant"]
    assert out[0]["content"][0]["type"] == "input_text"
    assert out[1]["content"][0]["type"] == "input_text"
    assert out[2]["content"][0]["type"] == "output_text"
    assert out[0]["content"][0]["text"] == "be terse"


def test_messages_to_input_handles_missing_content():
    out = CodexOAuthLLM._messages_to_input([{"role": "user"}])
    assert out[0]["content"][0]["text"] == ""


# ---------------------------------------------------------------------------
# response parsers
# ---------------------------------------------------------------------------

def test_extract_output_text_from_message_items():
    data = {
        "output": [
            {"type": "reasoning", "summary": [{"type": "summary_text", "text": "rx"}]},
            {"type": "message",
             "content": [
                 {"type": "output_text", "text": "hello "},
                 {"type": "output_text", "text": "world"},
             ]},
        ],
    }
    assert _extract_output_text(data) == "hello \nworld"
    assert _extract_reasoning(data) == "rx"


def test_extract_output_text_falls_back_to_output_text_field():
    assert _extract_output_text({"output": [], "output_text": "hi"}) == "hi"


def test_extract_reasoning_joins_multiple_items():
    data = {
        "output": [
            {"type": "reasoning", "summary": [{"type": "summary_text", "text": "a"}]},
            {"type": "reasoning", "summary": [{"type": "summary_text", "text": "b"}]},
            {"type": "message", "content": [{"type": "output_text", "text": "final"}]},
        ],
    }
    assert _extract_reasoning(data) == "a\n\nb"
