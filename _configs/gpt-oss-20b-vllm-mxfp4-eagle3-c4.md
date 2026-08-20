---
title: gpt-oss-20b · vLLM · MXFP4 + EAGLE3 · conc 4
model: openai/gpt-oss-20b
company: OpenAI
family: gpt-oss
params: 21B / 3.6B (MoE)
engine: vLLM
speculative: EAGLE3
quant: MXFP4
quant_rationale: conc-4 point of the EAGLE3 fine-grained sweep (EXPERIMENTS.md #15) — testing whether the conc-32 "+28%" is a scheduling artifact. Same cu130-nightly + RedHatAI EAGLE3 recipe as the conc-1/8/32 rows; measured against the matched conc-4 base.
source_repo: openai/gpt-oss-20b
download_url: https://huggingface.co/openai/gpt-oss-20b
context: 65536
modalities: [text]
mm_served: true
concurrency: 4
tags: [gpt-oss-20b, OpenAI, gpt-oss, MXFP4, 16-40B, Spark recipe, conc-4]
status: done
prefill_toks: 127.09
decode_toks: 85.36
mem_gb: 109.15
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85) + EAGLE3 head
spec_acceptance: mean acceptance length ~1.13–1.20 (centered ~1.15) · avg draft acceptance ~4–7% (centered ~5%) · per-position ~0.09–0.13 / 0.03–0.05 / 0.005–0.02
measured_on: 2026-07-01
completed_at: 2026-07-01 16:15 +0800
engine_image: vllm/vllm-openai:cu130-nightly@sha256:3dbe092ec5b2cef63b6104d33fa75d6ce53a7870962529ada69f78bbbc38e776
run_command: |
  # conc-4 EAGLE3, cu130-nightly + RedHatAI speculator. Harmony vocab via VOCAB_DIR override.
  VLLM_IMAGE=vllm/vllm-openai:cu130-nightly VOCAB_DIR=$HOME/tiktoken_encodings \
    scripts/bench-vllm-serving.sh openai/gpt-oss-20b 65536 4 1000 600 256 \
    --speculative-config '{"model":"RedHatAI/gpt-oss-20b-speculator.eagle3","method":"eagle3","num_speculative_tokens":3}'
  # 212/1000 prompts (hit 600 s cap), 15 harmony errors. ready after 162 s.
---

**conc-4 EAGLE3 — still a net loss, deepening.** gpt-oss-20b MXFP4 + RedHatAI EAGLE3 speculator on vLLM,
conc 4.

- **Result (conc 4):** prefill 127.09 / decode **85.36** tok/s aggregate; 212/1000 prompts (hit the 600 s
  cap), **15 harmony errors**; peak mem 109.2 GB.
- **EAGLE3 vs base at conc-4: −32.9%** (85.36 vs base [127.26]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-c4/)) — *worse* than the
  conc-2 loss (−29.3%). The spec penalty deepens as the batch fills, exactly the wrong direction for a real
  draft win. Running total for #15: **−29.3% (c2) → −32.9% (c4)**, both strongly negative.
- **Acceptance dismal:** mean accept-len **~1.15**, avg draft acceptance **~5%** — the draft converts almost
  nothing on this ShareGPT+harmony workload, so it's pure overhead.
- **TTFT/TPOT are buffered-reasoning artifacts** — aggregate decode tok/s is the valid metric.
- Sweep: [`-c1`]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-eagle3-c1/) · [`-c2`]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-eagle3-c2/) ·
  [`-c8`]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-eagle3-c8/) · [`-c16`]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-eagle3-c16/) ·
  [`c32` (main)]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-eagle3/). Base: [`-c4`]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-c4/).
