---
title: Gemma 4 26B-A4B · vLLM · NVFP4 + MTP · conc 4
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
concurrency: 4
tags: [gemma-4-26b-a4b, Google, Gemma, NVFP4, 16-40B, conc-4]
status: done
prefill_toks: 203.39
decode_toks: 165.39
mem_gb: 108.98
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85) + Gemma4 MTP head
spec_acceptance: mean acceptance length 2.73 (2.54-2.93) · avg draft acceptance 58% (51-64%) · per-position ~0.76/0.56/0.41
measured_on: 2026-07-03
completed_at: 2026-07-03 16:32 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:e414712fdc04f61d98ccc58cb61232a0587a8c024544e9e6cf12f97b19b38172
run_command: |
  VLLM_IMAGE=vllm/vllm-openai:nightly-aarch64 scripts/bench-vllm-serving.sh nvidia/Gemma-4-26B-A4B-NVFP4 65536 4 500 500 256 \
    --speculative-config '{"method":"mtp","model":"google/gemma-4-26B-A4B-it-assistant","num_speculative_tokens":3}'
  # 355/500 prompts (hit the time cap), 0 errors, 503.1s. ready after 303s. TTFT median 204.1 ms, TPOT median 22.9 ms, req thr 0.706/s.
  # SpecDecoding: mean acceptance length 2.73 (2.54-2.93) · avg draft acceptance 58% (51-64%) · per-position ~0.76/0.56/0.41.
---

**Decode 165.39 tok/s aggregate at concurrency 4.** NVFP4 + Google MTP assistant drafter, conc 4 — the near-free-drafter line of the crossover figure.

- **Image (pinned):** `vllm/vllm-openai:nightly-aarch64` @ `sha256:e414712fdc04…` — the SINGLE image for all 24 cells of this figure. Ready after **303 s**.
- **Workload:** ShareGPT V3, concurrency 4. **355/500 completed, 0 errors** before the **500 s time cap**.
- **Throughput:** decode **165.39 tok/s** aggregate, prefill 203.39 tok/s. TTFT median 204.1 ms, TPOT median 22.9 ms, req throughput 0.706/s.
- **Spec-decode acceptance:** mean acceptance length 2.73 (2.54-2.93) · avg draft acceptance 58% (51-64%) · per-position ~0.76/0.56/0.41 (num_speculative_tokens=3).
- **Memory: 108.98 GB** = vLLM `--gpu-memory-utilization 0.85` reservation, not the model footprint.
