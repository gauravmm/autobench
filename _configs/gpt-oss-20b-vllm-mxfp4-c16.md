---
title: gpt-oss-20b · vLLM · MXFP4 · conc 16
model: openai/gpt-oss-20b
company: OpenAI
family: gpt-oss
params: 21B / 3.6B (MoE)
engine: vLLM
quant: MXFP4
quant_rationale: conc-16 base (non-spec) point of gpt-oss-20b — matched no-spec baseline for the EAGLE3 conc-16 row (EXPERIMENTS.md #15). Same cu130-nightly recipe as the published conc-32 base; only --max-num-seqs differs. Completes the base line for the EAGLE3-artifact test.
source_repo: openai/gpt-oss-20b
download_url: https://huggingface.co/openai/gpt-oss-20b
context: 65536
modalities: [text]
mm_served: true
concurrency: 16
tags: [gpt-oss-20b, OpenAI, gpt-oss, MXFP4, 16-40B, Spark recipe, conc-16]
status: done
prefill_toks: 403.31
decode_toks: 340.69
mem_gb: 107.83
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85)
measured_on: 2026-07-01
completed_at: 2026-07-01 15:35 +0800
engine_image: vllm/vllm-openai:cu130-nightly@sha256:3dbe092ec5b2cef63b6104d33fa75d6ce53a7870962529ada69f78bbbc38e776
run_command: |
  # conc-16 base (no spec), cu130-nightly. Harmony vocab via VOCAB_DIR override.
  VLLM_IMAGE=vllm/vllm-openai:cu130-nightly VOCAB_DIR=$HOME/tiktoken_encodings \
    scripts/bench-vllm-serving.sh openai/gpt-oss-20b 65536 16 1000 600 256
  # 837/1000 prompts (hit 600 s cap), 89 harmony errors.
---

**conc-16 base (no-spec) point of gpt-oss-20b MXFP4** — completes the matched base line for the EAGLE3
artifact test (EXPERIMENTS.md #15). Same cu130-nightly recipe as the published conc-32 base.

- **Result (conc 16):** prefill 403.31 / decode **340.69** tok/s aggregate; 837/1000 prompts (hit the 600 s
  cap), **89 harmony errors** (error count scales cleanly with batch: 5→22→89 at c2→c4→c16, all mid-reasoning
  256-tok truncation — a vLLM harmony-finalizer robustness cost, not a config fault); peak mem 107.8 GB.
- **Base line for the artifact test is now:** decode 83.4 (c2) → 127.3 (c4) → **340.7 (c16)** → 535.3 (c32).
  Pair each against the EAGLE3 row to see whether spec-decode helps at all before conc-32.
- **TTFT/TPOT are buffered-reasoning artifacts** — aggregate decode tok/s is the valid metric.
- Base siblings: [`-c2`]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-c2/) · [`-c4`]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-c4/) ·
  [`c32` (main)]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4/). EAGLE3 counterpart: [`-eagle3-c16`]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-eagle3-c16/).
