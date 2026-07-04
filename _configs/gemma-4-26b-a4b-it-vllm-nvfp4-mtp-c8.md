---
title: Gemma 4 26B-A4B · vLLM · NVFP4 + MTP · conc 8
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
concurrency: 8
tags: [gemma-4-26b-a4b, Google, Gemma, NVFP4, 16-40B, conc-8]
status: done
prefill_toks: 284.06
decode_toks: 267.13
mem_gb: 108.68
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85) + Gemma4 MTP head
spec_acceptance: mean acceptance length 2.59 (2.26-2.88) · avg draft acceptance 53% (42-63%) · per-position ~0.73/0.51/0.35
measured_on: 2026-07-03
completed_at: 2026-07-03 16:32 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:e414712fdc04f61d98ccc58cb61232a0587a8c024544e9e6cf12f97b19b38172
run_command: |
  VLLM_IMAGE=vllm/vllm-openai:nightly-aarch64 scripts/bench-vllm-serving.sh nvidia/Gemma-4-26B-A4B-NVFP4 65536 8 700 600 256 \
    --speculative-config '{"method":"mtp","model":"google/gemma-4-26B-A4B-it-assistant","num_speculative_tokens":3}'
  # 684/700 prompts (hit the time cap), 0 errors, 606.1s. ready after 306s. TTFT median 237.5 ms, TPOT median 28.0 ms, req thr 1.128/s.
  # SpecDecoding: mean acceptance length 2.59 (2.26-2.88) · avg draft acceptance 53% (42-63%) · per-position ~0.73/0.51/0.35.
---

**Decode 267.13 tok/s aggregate at concurrency 8.** NVFP4 + Google MTP assistant drafter, conc 8 — the near-free-drafter line of the crossover figure.

- **Image (pinned):** `vllm/vllm-openai:nightly-aarch64` @ `sha256:e414712fdc04…` — the SINGLE image for all 24 cells of this figure. Ready after **306 s**.
- **Workload:** ShareGPT V3, concurrency 8. **684/700 completed, 0 errors** before the **600 s time cap**.
- **Throughput:** decode **267.13 tok/s** aggregate, prefill 284.06 tok/s. TTFT median 237.5 ms, TPOT median 28.0 ms, req throughput 1.128/s.
- **Spec-decode acceptance:** mean acceptance length 2.59 (2.26-2.88) · avg draft acceptance 53% (42-63%) · per-position ~0.73/0.51/0.35 (num_speculative_tokens=3).
- **Memory: 108.68 GB** = vLLM `--gpu-memory-utilization 0.85` reservation, not the model footprint.
