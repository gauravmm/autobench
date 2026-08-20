---
title: gpt-oss-20b · vLLM · MXFP4 · conc 4
model: openai/gpt-oss-20b
company: OpenAI
family: gpt-oss
params: 21B / 3.6B (MoE)
engine: vLLM
quant: MXFP4
quant_rationale: conc-4 base (non-spec) point of gpt-oss-20b — matched no-spec baseline for the EAGLE3 conc-4 row (EXPERIMENTS.md #15). Same cu130-nightly recipe as the published conc-32 base; only --max-num-seqs differs. Half of the EAGLE3-artifact test at conc-4.
source_repo: openai/gpt-oss-20b
download_url: https://huggingface.co/openai/gpt-oss-20b
context: 65536
modalities: [text]
mm_served: true
concurrency: 4
tags: [gpt-oss-20b, OpenAI, gpt-oss, MXFP4, 16-40B, Spark recipe, conc-4]
status: done
prefill_toks: 179.74
decode_toks: 127.26
mem_gb: 108.40
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85)
measured_on: 2026-07-01
completed_at: 2026-07-01 15:22 +0800
engine_image: vllm/vllm-openai:cu130-nightly@sha256:3dbe092ec5b2cef63b6104d33fa75d6ce53a7870962529ada69f78bbbc38e776
run_command: |
  # conc-4 base (no spec), cu130-nightly. Harmony vocab via VOCAB_DIR override.
  VLLM_IMAGE=vllm/vllm-openai:cu130-nightly VOCAB_DIR=$HOME/tiktoken_encodings \
    scripts/bench-vllm-serving.sh openai/gpt-oss-20b 65536 4 1000 600 256
  # 313/1000 prompts (hit 600 s cap), 22 harmony errors.
---

**conc-4 base (no-spec) point of gpt-oss-20b MXFP4** — matched baseline for the EAGLE3 conc-4 row
(EXPERIMENTS.md #15). Same cu130-nightly recipe as the published conc-32 base.

- **Result (conc 4):** prefill 179.74 / decode **127.26** tok/s aggregate; 313/1000 prompts (hit the 600 s
  cap), **22 harmony errors** (rising with batch — 5 at c2 → 22 at c4, mid-reasoning 256-tok truncation);
  peak mem 108.4 GB.
- Anchors the base line for the EAGLE3 artifact test at conc-4. Base line so far: 83.4 (c2) → 127.3 (c4).
- **TTFT/TPOT are buffered-reasoning artifacts** — aggregate decode tok/s is the valid metric.
- Base siblings: [`-c2`]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-c2/) · [`-c16`]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-c16/) ·
  [`c32` (main)]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4/). EAGLE3 counterpart: [`-eagle3-c4`]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-eagle3-c4/).
