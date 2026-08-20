---
title: gpt-oss-20b · vLLM · MXFP4 · conc 1
model: openai/gpt-oss-20b
company: OpenAI
family: gpt-oss
params: 21B / 3.6B (MoE)
engine: vLLM
quant: MXFP4
quant_rationale: conc-1 base (non-spec) point of gpt-oss-20b — completes the matched no-spec baseline for the EAGLE3 conc-1 row alongside the existing conc-2/4/16 base points. Same cu130-nightly recipe as the published conc-32 base; only --max-num-seqs differs.
source_repo: openai/gpt-oss-20b
download_url: https://huggingface.co/openai/gpt-oss-20b
context: 65536
modalities: [text]
mm_served: true
concurrency: 1
tags: [gpt-oss-20b, OpenAI, gpt-oss, MXFP4, 16-40B, Spark recipe, conc-1]
status: done
prefill_toks: 64.57
decode_toks: 45.56
mem_gb: 108.06
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85)
measured_on: 2026-07-02
completed_at: 2026-07-02 07:51 +0800
engine_image: vllm/vllm-openai:cu130-nightly@sha256:3dbe092ec5b2cef63b6104d33fa75d6ce53a7870962529ada69f78bbbc38e776
run_command: |
  # conc-1 base (no spec), cu130-nightly to match the gpt-oss-20b series. Harmony vocab via VOCAB_DIR override.
  VLLM_IMAGE=vllm/vllm-openai:cu130-nightly VOCAB_DIR=$HOME/tiktoken_encodings \
    scripts/bench-vllm-serving.sh openai/gpt-oss-20b 65536 1 1000 600 256
  # 115/1000 prompts (hit 600 s cap), 2 harmony errors. ready after 151 s.
---

**conc-1 base (no-spec) point of gpt-oss-20b MXFP4** — completes the base line down to single-stream,
pairing with the EAGLE3 conc-1 row for the low-batch loss comparison.

- **Result (conc 1):** prefill 64.57 / decode **45.56** tok/s single-stream aggregate; 115/1000 prompts
  (hit the 600 s cap), **2 harmony errors** (fewest in the series — errors scale with batch: 2→5→22→35→89→108
  at c1→c2→c4→c8→c16→c32); peak mem 108.06 GB; TTFT median 5507.8 ms.
- **Full base line now complete c1→c32:** decode 45.56 (c1) → 83.4 (c2) → 127.3 (c4) → 212.5 (c8) →
  340.7 (c16) → 535.3 (c32) — clean monotone scaling, no dip.
- **The EAGLE3-vs-base "inverted" pathology now has a gap-free curve.** Against this base, EAGLE3 decode
  ([`-eagle3-c1`]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-eagle3-c1/) at 38.55) is **−15.4%** at conc-1 — a real loss even
  single-stream, not the neutral/break-even point one might expect from a bandwidth-bound regime. Full
  curve: **−15.4% (c1) → −29.3% (c2) → −32.9% (c4) → −40.6% (c8) → +26.8% (c16) → +28.2% (c32)** — EAGLE3
  is a loss at every batch size up to c8, and only turns positive at c16/c32, tracking the acceptance
  jump documented in `notes/INCOMPATIBILITIES.md` (~5% accept at conc≤8 vs ~44% at conc≥16).
- **TTFT/TPOT are buffered-reasoning artifacts** — aggregate decode tok/s is the valid metric.
- Base siblings: [`-c2`]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-c2/) · [`-c4`]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-c4/) ·
  [`-c8`]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-c8/) · [`-c16`]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-c16/) ·
  [`c32` (main)]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4/). EAGLE3 counterpart:
  [`-eagle3-c1`]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-eagle3-c1/).
