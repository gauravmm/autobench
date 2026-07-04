---
title: Gemma 4 26B-A4B · vLLM · NVFP4 + MTP · conc 16
model: google/gemma-4-26B-A4B-it
company: Google
family: Gemma
params: 26B / 4B (MoE)
engine: vLLM
speculative: MTP (Google assistant drafter)
quant: NVFP4
quant_rationale: NVIDIA NVFP4 base (modelopt) + Google's official MTP assistant drafter (google/gemma-4-26B-A4B-it-assistant) via vLLM's native gemma-4 MTP path — the near-free-drafter line of the crossover figure.
source_repo: nvidia/Gemma-4-26B-A4B-NVFP4
download_url: https://huggingface.co/nvidia/Gemma-4-26B-A4B-NVFP4
context: 65536
modalities: [text, image]
mm_served: false
concurrency: 16
tags: [gemma-4-26b-a4b, Google, Gemma, NVFP4, 16-40B, conc-16]
status: done
prefill_toks: 498.8
decode_toks: 436.71
mem_gb: 108.39
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85) + Gemma4 MTP head
spec_acceptance: mean acceptance length 2.64 (2.30-2.89) · avg draft acceptance 55% (43-63%) · per-position ~0.74/0.53/0.37
measured_on: 2026-07-03
completed_at: 2026-07-03 16:32 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:e414712fdc04f61d98ccc58cb61232a0587a8c024544e9e6cf12f97b19b38172
run_command: |
  VLLM_IMAGE=vllm/vllm-openai:nightly-aarch64 scripts/bench-vllm-serving.sh nvidia/Gemma-4-26B-A4B-NVFP4 65536 16 1000 700 256 \
    --speculative-config '{"method":"mtp","model":"google/gemma-4-26B-A4B-it-assistant","num_speculative_tokens":3}'
  # 1000/1000 prompts (clean full run), 0 errors, 540.3s. ready after 328s. TTFT median 276.6 ms, TPOT median 33.9 ms, req thr 1.851/s.
  # SpecDecoding: mean acceptance length 2.64 (2.30-2.89) · avg draft acceptance 55% (43-63%) · per-position ~0.74/0.53/0.37.
---

**Decode 436.71 tok/s aggregate at concurrency 16.** NVFP4 + Google MTP assistant drafter, conc 16 — the near-free-drafter line of the crossover figure.

- **Image (pinned):** `vllm/vllm-openai:nightly-aarch64` @ `sha256:e414712fdc04…` — the SINGLE image for all 24 cells of this figure. Ready after **328 s**.
- **Workload:** ShareGPT V3, concurrency 16. **1000/1000, 0 errors** in **540.3 s** (clean full run).
- **Throughput:** decode **436.71 tok/s** aggregate, prefill 498.8 tok/s. TTFT median 276.6 ms, TPOT median 33.9 ms, req throughput 1.851/s.
- **Spec-decode acceptance:** mean acceptance length 2.64 (2.30-2.89) · avg draft acceptance 55% (43-63%) · per-position ~0.74/0.53/0.37 (num_speculative_tokens=3).
- **Memory: 108.39 GB** = vLLM `--gpu-memory-utilization 0.85` reservation, not the model footprint.
