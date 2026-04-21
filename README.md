DistilAgent fuses [distilabel](https://github.com/argilla-io/distilabel) with [NousResearch's AutoReason](https://github.com/NousResearch/autoreason) tournament refinement so a single teacher model produces distillation labels that are measurably better than its own single-shot output. Each prompt is answered, critiqued, adversarially revised, synthesized, and ranked by a blind Borda panel — all from the same model — until "do nothing" wins twice. Full reasoning traces are captured per role for process-supervision fine-tuning.

## Screenshots

![DistilAgent tournament loop — live per-sample progress from a 69-row pilot on Gemma 4 26B-A4B with thinking mode on](./docs/screenshot.png)

## How it works

A new `AutoReasonedGeneration` Task drops into any distilabel pipeline. For each instruction, the teacher produces an incumbent draft **A**. A fresh-context critic finds concrete flaws (or says NO FLAWS). Two fresh agents produce competing revisions: an adversarial **B** and a conservative synthesis **AB**. A panel of N blind judges ranks all three under randomised labels; Borda count picks the winner. If A defends twice in a row, the loop converges; otherwise the winner is promoted and the tournament repeats.

Every LLM call is rate-limited and retry-wrapped: 429s, 503s, Metal working-set rejections, and httpx timeouts all backoff-and-retry instead of dropping votes. A per-model `AsyncTokenBucket` enforces RPM and RPD so free-tier OpenRouter models and memory-tight local MLX servers are safe.

The dataset row carries the refined answer, the full tournament trace, every iteration's Borda vote, and per-role reasoning traces split by critic / author / synthesizer / judge — enough to train SFT, DPO, or chain-of-thought students without regenerating.

A 69-sample pilot on Gemma 4 26B-A4B (local vMLX, thinking on) produced rich traces at ~8 min/sample with zero unrecovered failures. Blind external-judge evals on the prior m2.7 pilot picked AutoReason over single-shot baseline on all 3 randomised runs.

## Stack

- Python 3.11, asyncio, pydantic v2
- distilabel (forked from develop branch) as the pipeline runtime
- AutoReason tournament method (A / B / AB + blind Borda) adapted from the NousResearch paper
- OpenAI async SDK for OpenRouter, local vMLX, and any OpenAI-compatible endpoint
- MLX-LM for on-device Apple Silicon inference (Gemma 4, Qwen3)
- pytest + pytest-asyncio (61 tests across borda, rate-limit, roles, tournament, and end-to-end task)
- Hugging Face datasets for source prompts (`ianncity/General-Distillation-Prompts-1M`)

## Status

Active
