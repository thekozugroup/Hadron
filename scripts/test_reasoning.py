"""Fast iteration harness for caveman-reasoning prompt tuning.

Fires a tiny set of fixed prompts through ONLY the teacher-seed role,
captures `reasoning_content`, then scores each reasoning trace for
caveman-violation patterns. Prints compact side-by-side stats.

Usage:
    OPENROUTER_API_KEY=... python scripts/test_reasoning.py
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from reasoning_llm import ReasoningOpenRouterLLM  # noqa: E402

from distilabel.steps.tasks.autoreason.roles import (  # noqa: E402
    TEACHER_SEED_SYSTEM, render_teacher_seed,
)

# -- fixed test prompts picked to REQUIRE some reasoning (so the thinking
#    stream is non-trivial and we can actually observe caveman compliance)
TEST_PROMPTS = [
    "Explain why two’s complement is used for signed integers in CPUs. 3 sentences.",
    "Given list [3,1,4,1,5,9,2,6], write a Python one-liner that returns the second-largest unique value.",
    "A 0.5 kg block slides on ice with µ=0.02 at 4 m/s. How far before it stops? Show the formula.",
]

# -- caveman-violation regexes (case-insensitive, word-bounded where it matters)
VIOLATIONS = {
    "let_me":          re.compile(r"\blet me\b", re.I),
    "i_will":          re.compile(r"\b(i'?ll|i will)\b", re.I),
    "i_should":        re.compile(r"\bi (should|need to|want to|must|can)\b", re.I),
    "first_next":      re.compile(r"\b(first|next|then|finally)[,:]", re.I),
    "perhaps_maybe":   re.compile(r"\b(perhaps|maybe|might be|it seems|it appears)\b", re.I),
    "filler":          re.compile(r"\b(just|really|basically|actually|literally|essentially)\b", re.I),
    "wait_hmm":        re.compile(r"\b(wait|hmm|on second thought|let me reconsider|let me think again)\b", re.I),
    "user_wants":      re.compile(r"\bthe user (wants|is asking|asked|needs|wants me|asks)\b", re.I),
    "i_think":         re.compile(r"\b(i think|i believe|in my opinion)\b", re.I),
}

BAD_START = re.compile(
    r"^\s*(okay[,.]|ok[,.]|so[,.]|well[,.]|alright[,.]|right[,.]|let me|let's|let's see|first[,.]|the user)",
    re.I,
)


def score(reasoning: str) -> dict:
    d = {"chars": len(reasoning), "tokens_est": len(reasoning) // 4}
    for name, rx in VIOLATIONS.items():
        d[name] = len(rx.findall(reasoning))
    d["bad_start"] = bool(BAD_START.match(reasoning or ""))
    d["total_violations"] = sum(v for k, v in d.items() if k not in ("chars", "tokens_est", "bad_start"))
    return d


async def one_call(llm, user_text: str) -> tuple[str, str, float]:
    messages = [
        {"role": "system", "content": TEACHER_SEED_SYSTEM},
        {"role": "user", "content": user_text},
    ]
    t0 = time.monotonic()
    out = await llm.agenerate(input=messages, num_generations=1)
    dt = time.monotonic() - t0
    buf = llm.drain_reasoning()
    if not buf:
        return "", out["generations"][0], dt
    _role, reasoning, text = buf[-1]
    return reasoning, text, dt


async def main():
    llm = ReasoningOpenRouterLLM(
        model=os.environ.get("TEST_MODEL", "minimax/minimax-m2.5:free"),
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENROUTER_API_KEY"],
        reasoning_effort=os.environ.get("REASONING_EFFORT", "high"),
        generation_kwargs={
            "temperature": 0.5,
            "top_p": 0.95,
            "max_tokens": 2048,
            "extra_body": {"repetition_penalty": 1.2},
        },
        timeout=300,
    )
    llm.load()

    print(f"TEACHER_SEED_SYSTEM ({len(TEACHER_SEED_SYSTEM)} chars)")
    print("---")
    print(TEACHER_SEED_SYSTEM)
    print("=" * 80)

    tasks = [one_call(llm, p) for p in TEST_PROMPTS]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    total = {}
    for p, r in zip(TEST_PROMPTS, results):
        if isinstance(r, BaseException):
            print(f"\n✗ FAIL: {p[:60]} -- {type(r).__name__}: {r}")
            continue
        reasoning, text, dt = r
        s = score(reasoning)
        for k, v in s.items():
            if isinstance(v, (int, float, bool)):
                total[k] = total.get(k, 0) + int(v)
        print(f"\n▸ {p[:60]}")
        print(f"  reasoning: {s['chars']} chars ≈{s['tokens_est']} tok   output: {len(text)} chars   {dt:.1f}s")
        flags = [k for k in VIOLATIONS if s[k] > 0]
        if flags:
            print(f"  violations: " + " ".join(f"{k}={s[k]}" for k in flags))
        if s["bad_start"]:
            print(f"  BAD_START: reasoning begins with a forbidden opener")
        print(f"  reasoning HEAD: {(reasoning[:180]).replace(chr(10), ' ⏎ ')!r}")

    print("\n=== TOTALS across test prompts ===")
    print(f"  reasoning chars total: {total.get('chars', 0)}  ({total.get('tokens_est', 0)} tok)")
    print(f"  TOTAL VIOLATIONS:      {total.get('total_violations', 0)}")
    for k in VIOLATIONS:
        if total.get(k, 0) > 0:
            print(f"    {k:15s} {total[k]}")
    print(f"  bad-start count: {total.get('bad_start', 0)} / {len(TEST_PROMPTS)}")


if __name__ == "__main__":
    asyncio.run(main())
