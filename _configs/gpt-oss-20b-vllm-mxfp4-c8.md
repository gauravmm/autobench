---
title: gpt-oss-20b · vLLM · MXFP4 · conc 8
model: openai/gpt-oss-20b
company: OpenAI
family: gpt-oss
params: 21B / 3.6B (MoE)
engine: vLLM
quant: MXFP4
quant_rationale: conc-8 base (non-spec) point of gpt-oss-20b — completes the matched no-spec baseline for the EAGLE3 conc-8 row alongside the existing conc-1/2/4/16 base points, filling the last gap in the base ladder. Same cu130-nightly recipe as the published conc-32 base; only --max-num-seqs differs.
source_repo: openai/gpt-oss-20b
download_url: https://huggingface.co/openai/gpt-oss-20b
context: 65536
modalities: [text]
mm_served: true
concurrency: 8
tags: [gpt-oss-20b, OpenAI, gpt-oss, MXFP4, 16-40B, Spark recipe, conc-8]
status: done
prefill_toks: 228.84
decode_toks: 212.52
mem_gb: 107.56
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85)
measured_on: 2026-07-02
completed_at: 2026-07-02 07:51 +0800
engine_image: vllm/vllm-openai:cu130-nightly@sha256:3dbe092ec5b2cef63b6104d33fa75d6ce53a7870962529ada69f78bbbc38e776
run_command: |
  # conc-8 base (no spec), cu130-nightly to match the gpt-oss-20b series. Harmony vocab via VOCAB_DIR override.
  VLLM_IMAGE=vllm/vllm-openai:cu130-nightly VOCAB_DIR=$HOME/tiktoken_encodings \
    scripts/bench-vllm-serving.sh openai/gpt-oss-20b 65536 8 1000 600 256
  # 509/1000 prompts (hit 600 s cap), 35 harmony errors. ready after 166 s.
---

**conc-8 base (no-spec) point of gpt-oss-20b MXFP4** — the last gap in the base ladder, pairing with the
EAGLE3 conc-8 row.

- **Result (conc 8):** prefill 228.84 / decode **212.52** tok/s aggregate; 509/1000 prompts (hit the 600 s
  cap), **35 harmony errors** (fits the batch-scaling pattern: 2→5→22→35→89→108 at c1→c2→c4→c8→c16→c32,
  all mid-reasoning 256-tok truncation); peak mem 107.56 GB.
- **Base line is now complete c1→c32:** decode 45.56 (c1) → 83.4 (c2) → 127.3 (c4) → **212.5 (c8)** →
  340.7 (c16) → 535.3 (c32) — clean monotone scaling.
- **The EAGLE3-vs-base pathology's worst point.** Against this base, EAGLE3 decode
  ([`-eagle3-c8`]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-eagle3-c8/) at 126.3) is **−40.6%** — the deepest loss in the
  sweep, right before the sign flip at c16. Full curve: −15.4% (c1) → −29.3% (c2) → −32.9% (c4) →
  **−40.6% (c8)** → +26.8% (c16) → +28.2% (c32). This confirms the post's "inverted" framing cleanly: the
  loss *deepens* monotonically through c8, then flips hard rather than gradually recovering — consistent
  with EAGLE3 draft acceptance being suppressed at low/mid batch (~5% at conc≤8) and jumping to ~44% only
  at conc≥16 (`notes/INCOMPATIBILITIES.md`).
- **TTFT/TPOT are buffered-reasoning artifacts** — aggregate decode tok/s is the valid metric.
- Base siblings: [`-c1`]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-c1/) · [`-c2`]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-c2/) ·
  [`-c4`]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-c4/) · [`-c16`]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-c16/) ·
  [`c32` (main)]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4/). EAGLE3 counterpart:
  [`-eagle3-c8`]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-eagle3-c8/).
