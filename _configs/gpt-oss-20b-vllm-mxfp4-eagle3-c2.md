---
title: gpt-oss-20b · vLLM · MXFP4 + EAGLE3 · conc 2
model: openai/gpt-oss-20b
company: OpenAI
family: gpt-oss
params: 21B / 3.6B (MoE)
engine: vLLM
speculative: EAGLE3
quant: MXFP4
quant_rationale: conc-2 point of the EAGLE3 fine-grained sweep (EXPERIMENTS.md #15) — is the published conc-32 "+28%" a real acceptance win or a scheduling artifact? Same cu130-nightly + RedHatAI EAGLE3 speculator recipe as the conc-1/8/32 rows; measured against the matched conc-2 base to get the true spec-decode speedup at low batch.
source_repo: openai/gpt-oss-20b
download_url: https://huggingface.co/openai/gpt-oss-20b
context: 65536
modalities: [text]
mm_served: true
concurrency: 2
tags: [gpt-oss-20b, OpenAI, gpt-oss, MXFP4, 16-40B, Spark recipe, conc-2]
status: done
prefill_toks: 67.51
decode_toks: 58.98
mem_gb: 108.43
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85) + EAGLE3 head
spec_acceptance: mean acceptance length ~1.1–1.45 (centered ~1.2) · avg draft acceptance ~3–15% (centered ~6%) · per-position ~0.06–0.23 / 0.01–0.13 / 0.004–0.09
measured_on: 2026-07-01
completed_at: 2026-07-01 16:02 +0800
engine_image: vllm/vllm-openai:cu130-nightly@sha256:3dbe092ec5b2cef63b6104d33fa75d6ce53a7870962529ada69f78bbbc38e776
run_command: |
  # conc-2 EAGLE3, cu130-nightly + RedHatAI speculator. Harmony vocab via VOCAB_DIR override.
  VLLM_IMAGE=vllm/vllm-openai:cu130-nightly VOCAB_DIR=$HOME/tiktoken_encodings \
    scripts/bench-vllm-serving.sh openai/gpt-oss-20b 65536 2 1000 600 256 \
    --speculative-config '{"model":"RedHatAI/gpt-oss-20b-speculator.eagle3","method":"eagle3","num_speculative_tokens":3}'
  # 141/1000 prompts (hit 600 s cap), 11 harmony errors. ready after 195 s.
---

**conc-2 EAGLE3 — spec-decode is a NET LOSS here, confirming the "+28%@c32 is an artifact" thesis.**
gpt-oss-20b MXFP4 + RedHatAI EAGLE3 speculator on vLLM, conc 2.

- **Result (conc 2):** prefill 67.51 / decode **58.98** tok/s aggregate; 141/1000 prompts (hit the 600 s
  cap), **11 harmony errors**; peak mem 108.4 GB.
- **EAGLE3 vs base at conc-2: −29.3%** (58.98 vs base [83.37]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-c2/)). The draft doesn't
  just fail to help — it **actively hurts** at low batch, because the wasted draft/verify work isn't offset by
  any acceptance. This is the decisive evidence for #15: if the conc-32 "+28%" came from acceptance, spec
  would help here too; instead it's **strongly negative**, so the c32 win is a scheduling/prefill effect at
  that one batch size, not a real draft win.
- **Acceptance is dismal (as at c1/c8):** mean accept-len **~1.1–1.45** (≈1 extra token per 3 drafted), avg
  draft acceptance **~3–15%** (centered ~6%), per-position collapsing to near-zero by slot 3. Far below
  EAGLE3's ~3.0 / ~70% expectation — ShareGPT general chat + gpt-oss's harmony reasoning channel is
  off-distribution for this draft (see notes/INCOMPATIBILITIES.md).
- **TTFT/TPOT are buffered-reasoning artifacts** — aggregate decode tok/s is the valid metric.
- Sweep: [`-c1`]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-eagle3-c1/) · [`-c4`]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-eagle3-c4/) ·
  [`-c8`]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-eagle3-c8/) · [`-c16`]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-eagle3-c16/) ·
  [`c32` (main)]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-eagle3/). Base: [`-c2`]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-c2/).
