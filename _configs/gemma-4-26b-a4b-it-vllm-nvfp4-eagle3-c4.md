---
title: Gemma 4 26B-A4B · vLLM · NVFP4 + EAGLE3 · conc 4
model: google/gemma-4-26B-A4B-it
company: Google
family: Gemma
params: 26B / 4B (MoE)
engine: vLLM
speculative: EAGLE3
quant: NVFP4
quant_rationale: NVIDIA NVFP4 base (modelopt) + RedHatAI's official EAGLE3 speculator (RedHatAI/gemma-4-26B-A4B-it-speculator.eagle3) — the EAGLE3 line of the crossover figure.
source_repo: nvidia/Gemma-4-26B-A4B-NVFP4
download_url: https://huggingface.co/nvidia/Gemma-4-26B-A4B-NVFP4
context: 65536
modalities: [text, image]
mm_served: false
concurrency: 4
tags: [gemma-4-26b-a4b, Google, Gemma, NVFP4, 16-40B, conc-4]
status: done
prefill_toks: 191.93
decode_toks: 143.9
mem_gb: 109.34
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85) + EAGLE3 head
spec_acceptance: mean acceptance length 2.11 (1.95-2.30) · avg draft acceptance 37% (32-43%) · per-position ~0.59/0.33/0.19
measured_on: 2026-07-03
completed_at: 2026-07-03 17:54 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:e414712fdc04f61d98ccc58cb61232a0587a8c024544e9e6cf12f97b19b38172
run_command: |
  VLLM_IMAGE=vllm/vllm-openai:nightly-aarch64 scripts/bench-vllm-serving.sh nvidia/Gemma-4-26B-A4B-NVFP4 65536 4 500 500 256 \
    --speculative-config '{"model":"RedHatAI/gemma-4-26B-A4B-it-speculator.eagle3","method":"eagle3","num_speculative_tokens":3}'
  # 307/500 prompts (hit the time cap), 0 errors, 505.5s. ready after 345s. TTFT median 189.4 ms, TPOT median 26.1 ms, req thr 0.607/s.
  # SpecDecoding: mean acceptance length 2.11 (1.95-2.30) · avg draft acceptance 37% (32-43%) · per-position ~0.59/0.33/0.19.
---

**Decode 143.9 tok/s aggregate at concurrency 4.** NVFP4 + RedHatAI EAGLE3 speculator, conc 4, for the crossover figure.

- **Image (pinned):** `vllm/vllm-openai:nightly-aarch64` @ `sha256:e414712fdc04…` — the SINGLE image for all 24 cells of this figure. Ready after **345 s**.
- **Workload:** ShareGPT V3, concurrency 4. **307/500 completed, 0 errors** before the **500 s time cap**.
- **Throughput:** decode **143.9 tok/s** aggregate, prefill 191.93 tok/s. TTFT median 189.4 ms, TPOT median 26.1 ms, req throughput 0.607/s.
- **Spec-decode acceptance:** mean acceptance length 2.11 (1.95-2.30) · avg draft acceptance 37% (32-43%) · per-position ~0.59/0.33/0.19 (num_speculative_tokens=3).
- **Memory: 109.34 GB** = vLLM `--gpu-memory-utilization 0.85` reservation, not the model footprint.
