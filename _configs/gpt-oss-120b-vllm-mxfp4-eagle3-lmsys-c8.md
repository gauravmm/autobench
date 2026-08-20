---
title: gpt-oss-120b · vLLM · MXFP4 + EAGLE3 (LMSYS draft) · conc 8
model: openai/gpt-oss-120b
company: OpenAI
family: gpt-oss
params: 116.8B (5.1B active, MoE)
engine: vLLM
speculative: EAGLE3 (lmsys/EAGLE3-gpt-oss-120b-bf16 — the SGLang/SpecForge draft, on vLLM)
quant: MXFP4
quant_rationale: EXPERIMENTS.md #5 — conc-8 point of the vLLM + LMSYS draft sweep, completing the 1/8/32 draft-vs-engine isolation for gpt-oss-120b. At moderate batch the LMSYS draft converts best on vLLM (acceptance peaks here), which characterizes the low-batch EAGLE3 pathology's recovery.
source_repo: openai/gpt-oss-120b
download_url: https://huggingface.co/openai/gpt-oss-120b
context: 65536
modalities: [text]
mm_served: true
concurrency: 8
tags: [gpt-oss-120b, OpenAI, gpt-oss, MXFP4, 41-130B, Spark recipe, conc-8]
status: done
prefill_toks: 201.76
decode_toks: 175.31
mem_gb: 108.36
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85) + EAGLE3 head
spec_acceptance: mean acceptance length ~2.45 (2.32–2.71) · avg draft acceptance ~48% (44–57%) — the HIGHEST of the vLLM+LMSYS sweep (c1 ~20% / c8 ~48% / c32 ~29%), and close to SGLang's ~55%
measured_on: 2026-07-01
completed_at: 2026-07-01 19:40 +0800
engine_image: vllm/vllm-openai:cu130-nightly@sha256:3dbe092ec5b2cef63b6104d33fa75d6ce53a7870962529ada69f78bbbc38e776
run_command: |
  # vLLM + LMSYS draft, conc-8. cu130-nightly, VOCAB_DIR override.
  VLLM_IMAGE=vllm/vllm-openai:cu130-nightly VOCAB_DIR=$HOME/tiktoken_encodings \
    scripts/bench-vllm-serving.sh openai/gpt-oss-120b 65536 8 1000 900 256 \
    --speculative-config '{"model":"lmsys/EAGLE3-gpt-oss-120b-bf16","method":"eagle3","num_speculative_tokens":3}'
  # 628/1000 prompts (hit 900 s cap), 32 harmony errors. ready after 486 s.
---

**conc-8 — the LMSYS draft converts BEST at moderate batch (acceptance ~48%, near SGLang's ~55%).**
gpt-oss-120b MXFP4 + `lmsys/EAGLE3-gpt-oss-120b-bf16` on vLLM.

- **Result (conc 8):** prefill 201.76 / decode **175.31** tok/s aggregate; 628/1000 prompts (hit the 900 s
  cap), **32 harmony errors**; peak mem 108.4 GB.
- **Acceptance peaks here, ~48%** (mean accept-len ~2.45) — higher than both conc-1 (~20%) and conc-32 (~29%),
  and close to the same draft's ~55% on SGLang. So the vLLM+LMSYS acceptance curve is **peak-in-the-middle:
  ~20% (c1) → ~48% (c8) → ~29% (c32)**, *not* the monotone rise the gpt-oss-20b showed (~5% ≤c8 → ~44% ≥c16).
- **What generalizes vs what doesn't.** Common to both models: acceptance is **depressed at the lowest
  concurrency** (120b c1 ~20%, 20b c2 ~5%) — the low-batch EAGLE3 pathology. What differs is the high end:
  the 20b stays high at c16/c32, the 120b **declines by c32** (the classic "draft loses value as the batch
  saturates"). So the robust, cross-model claim is the **low-batch depression**; the high-concurrency shape is
  model-dependent, and shouldn't be stated as a universal "acceptance rises with concurrency" rule.
- **No matched 120b base at conc-8** exists (base is conc-32 only), so this row is characterized by acceptance
  + absolute decode, not a spec-vs-base delta. The decisive draft-vs-engine delta is on the
  [`-lmsys-c32`]({{ site.baseurl }}/configs/gpt-oss-120b-vllm-mxfp4-eagle3-lmsys-c32/) page.
- **TTFT/TPOT are buffered-reasoning artifacts** — aggregate decode tok/s is the valid metric.
- Sweep: [`-lmsys-c1`]({{ site.baseurl }}/configs/gpt-oss-120b-vllm-mxfp4-eagle3-lmsys-c1/) ·
  [`-lmsys-c32`]({{ site.baseurl }}/configs/gpt-oss-120b-vllm-mxfp4-eagle3-lmsys-c32/) · SGLang+LMSYS
  [`sglang-eagle3-c1`]({{ site.baseurl }}/configs/gpt-oss-120b-sglang-mxfp4-eagle3-c1/).
