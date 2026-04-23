"""Codex-OAuth LLM for Hadron.

Implements `AsyncLLM` against OpenAI's Codex backend (the endpoint used
by ChatGPT Pro/Plus subscribers via the Codex CLI). Authenticates with
an OAuth access token from `scripts/codex_oauth.py`; refreshes
automatically. Uses the Responses API shape.

Differences from `OpenAILLM`:
  - Endpoint:        https://chatgpt.com/backend-api/codex/responses
  - Shape:           Responses API (input[], output[]) — not chat/completions
  - Auth:            Bearer <oauth-access-token> + ChatGPT-Account-Id header
  - System role:     mapped to 'developer' (Codex convention)
  - Reasoning:       captured from output[*].type == 'reasoning' items

Exposes `drain_reasoning()` so the Hadron tournament captures per-role
thinking into reasoning_trace exactly like the OpenRouter wrapper.
"""
from __future__ import annotations

import asyncio
import json
import os
import platform
import uuid
from typing import Any, Dict, List, Optional, Tuple

import httpx
from pydantic import Field, PrivateAttr

from hadron.models.llms.base import AsyncLLM

import sys
from pathlib import Path as _P
sys.path.insert(0, str(_P(__file__).parent))
from codex_oauth import (  # noqa: E402
    CODEX_RESPONSES_URL,
    CodexAuth,
    ensure_fresh,
    load_auth,
)


class CodexOAuthLLM(AsyncLLM):
    """Codex (ChatGPT Pro/Plus) LLM via OAuth — speaks the Responses API."""

    model: str = Field(
        default="gpt-5-codex",
        description="Codex model id. Examples: gpt-5-codex, gpt-5-codex-mini, o4-mini.",
    )
    reasoning_effort: str = Field(
        default="high",
        description="Reasoning effort: 'high' | 'medium' | 'low' | 'minimal'.",
    )
    timeout_s: float = Field(default=900.0, description="HTTP client timeout.")
    store: bool = Field(default=False, description="Responses API 'store' flag.")

    # Private state
    _auth: Optional[CodexAuth] = PrivateAttr(default=None)
    _client: Optional[httpx.AsyncClient] = PrivateAttr(default=None)
    _refresh_lock: asyncio.Lock = PrivateAttr(default=None)
    _reasoning_buffer: List[Tuple[str, str, str]] = PrivateAttr(default_factory=list)
    _session_id: str = PrivateAttr(default_factory=lambda: uuid.uuid4().hex)

    # -- lifecycle ----------------------------------------------------------

    def load(self) -> None:
        super().load()
        auth = load_auth()
        if auth is None:
            raise RuntimeError(
                "No Codex auth found. Run: python scripts/codex_oauth.py login "
                "(or `codex login` via the Codex CLI)."
            )
        self._auth = auth
        self._refresh_lock = asyncio.Lock()
        self._client = httpx.AsyncClient(timeout=self.timeout_s)

    @property
    def model_name(self) -> str:
        return f"codex/{self.model}"

    def drain_reasoning(self) -> List[Tuple[str, str, str]]:
        out = list(self._reasoning_buffer)
        self._reasoning_buffer.clear()
        return out

    # -- role hint (for reasoning tags) ------------------------------------

    def _role_hint(self, input_msgs) -> str:
        try:
            first = (input_msgs[0].get("content") or "")[:120].lower()
        except Exception:  # noqa: BLE001
            return "unknown"
        if "rigorous critic" in first:
            return "critic"
        if "adversarial reviser" in first:
            return "author_b"
        if "conservative synthesizer" in first:
            return "synthesizer"
        if "impartial judge" in first:
            return "judge"
        if "expert assistant" in first:
            return "teacher"
        return "unknown"

    # -- message-shape adapter: chat/completions → Responses API ----------

    @staticmethod
    def _messages_to_input(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert OpenAI chat-style messages to Responses-API `input` items.

        Role mapping:  system → developer, user → user, assistant → assistant.
        Content is wrapped as [{type: input_text | output_text, text}].
        """
        items = []
        for m in messages:
            role = m.get("role", "user")
            text = m.get("content") or ""
            if role == "system":
                role = "developer"
            if role == "assistant":
                items.append({
                    "role": "assistant",
                    "content": [{"type": "output_text", "text": text}],
                })
            else:
                items.append({
                    "role": role,
                    "content": [{"type": "input_text", "text": text}],
                })
        return items

    # -- request -----------------------------------------------------------

    async def _ensure_fresh(self) -> CodexAuth:
        async with self._refresh_lock:
            # `ensure_fresh` is sync; run in a thread since it may block on HTTP.
            self._auth = await asyncio.to_thread(ensure_fresh, self._auth)
            return self._auth

    def _headers(self, auth: CodexAuth) -> Dict[str, str]:
        h = {
            "Authorization": f"Bearer {auth.access_token}",
            "Content-Type": "application/json",
            "originator": "hadron",
            "User-Agent": (
                f"hadron/0.1 ({platform.system()} {platform.release()}; "
                f"{platform.machine()})"
            ),
            "session_id": self._session_id,
            "Openai-Beta": "responses=v1",
        }
        if auth.account_id:
            h["ChatGPT-Account-Id"] = auth.account_id
        return h

    async def agenerate(  # type: ignore[override]
        self,
        input: Any,
        num_generations: int = 1,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        if num_generations != 1:
            raise ValueError("CodexOAuthLLM supports num_generations=1 only")

        auth = await self._ensure_fresh()
        body: Dict[str, Any] = {
            "model": self.model,
            "input": self._messages_to_input(input),
            "reasoning": {"effort": self.reasoning_effort},
            "store": self.store,
            "stream": False,
        }
        # Pass through any generation_kwargs from pydantic.
        gen = dict(self.generation_kwargs or {})  # type: ignore[arg-type]
        for k in ("temperature", "top_p", "max_output_tokens"):
            if k in gen:
                body[k] = gen[k]
        # Allow callers to override reasoning or other fields via extra_body.
        extra = {**(gen.get("extra_body") or {}), **(kwargs.pop("extra_body", None) or {})}
        body.update(extra)

        role_hint = self._role_hint(input)
        resp = await self._client.post(CODEX_RESPONSES_URL,
                                        headers=self._headers(auth),
                                        content=json.dumps(body))
        if resp.status_code == 401:
            # Token may have expired between refresh and call; retry once.
            self._auth = await asyncio.to_thread(ensure_fresh, self._auth)
            resp = await self._client.post(CODEX_RESPONSES_URL,
                                            headers=self._headers(self._auth),
                                            content=json.dumps(body))
        if resp.status_code >= 400:
            raise RuntimeError(
                f"Codex HTTP {resp.status_code}: {resp.text[:400]}"
            )
        data = resp.json()

        text = _extract_output_text(data)
        reasoning = _extract_reasoning(data)
        self._reasoning_buffer.append((role_hint, reasoning, text))

        usage = data.get("usage") or {}
        return {
            "generations": [text],
            "statistics": {
                "input_tokens": [int(usage.get("input_tokens") or 0)],
                "output_tokens": [int(usage.get("output_tokens") or 0)],
            },
        }


# ---------------------------------------------------------------------------
# response parsers
# ---------------------------------------------------------------------------

def _walk_items(data: Dict[str, Any]):
    # Responses API can surface outputs under either `output` (list) or
    # `output_text` (shortcut). Support both plus any nested message items.
    out = data.get("output") or []
    if isinstance(out, list):
        yield from out
    msg = data.get("output_text")
    if isinstance(msg, str) and msg:
        yield {"type": "message", "content": [{"type": "output_text", "text": msg}]}


def _extract_output_text(data: Dict[str, Any]) -> str:
    # Preferred: concatenate all assistant output_text blocks in order.
    pieces: List[str] = []
    for item in _walk_items(data):
        if item.get("type") == "message":
            for c in item.get("content") or []:
                if c.get("type") in ("output_text", "text"):
                    t = c.get("text") or ""
                    if t:
                        pieces.append(t)
    if pieces:
        return "\n".join(pieces)
    # Fallback: shortcut field.
    if isinstance(data.get("output_text"), str):
        return data["output_text"]
    return ""


def _extract_reasoning(data: Dict[str, Any]) -> str:
    pieces: List[str] = []
    for item in _walk_items(data):
        if item.get("type") != "reasoning":
            continue
        # Newer shape: summary = [{type:"summary_text", text:"..."}]
        for s in item.get("summary") or []:
            t = s.get("text") if isinstance(s, dict) else None
            if t:
                pieces.append(t)
        for c in item.get("content") or []:
            if isinstance(c, dict):
                t = c.get("text") or ""
                if t:
                    pieces.append(t)
    return "\n\n".join(pieces)
