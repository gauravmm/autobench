---
title: Gemma 4 26B-A4B · vLLM · NVFP4 + EAGLE3 · conc 8
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
concurrency: 8
tags: [gemma-4-26b-a4b, Google, Gemma, NVFP4, 16-40B, conc-8]
status: done
prefill_toks: 270.31
decode_toks: 230.18
mem_gb: 107.48
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85) + EAGLE3 head
spec_acceptance: mean acceptance length 2.10 (1.90-2.25) · avg draft acceptance 37% (30-42%) · per-position ~0.58/0.33/0.19
measured_on: 2026-07-03
completed_at: 2026-07-03 17:54 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:e414712fdc04f61d98ccc58cb61232a0587a8c024544e9e6cf12f97b19b38172
run_command: |
  VLLM_IMAGE=vllm/vllm-openai:nightly-aarch64 scripts/bench-vllm-serving.sh nvidia/Gemma-4-26B-A4B-NVFP4 65536 8 700 600 256 \
    --speculative-config '{"model":"RedHatAI/gemma-4-26B-A4B-it-speculator.eagle3","method":"eagle3","num_speculative_tokens":3}'
  # 596/700 prompts (hit the time cap), 0 errors, 607.2s. ready after 369s. TTFT median 217.9 ms, TPOT median 32.5 ms, req thr 0.982/s.
  # SpecDecoding: mean acceptance length 2.10 (1.90-2.25) · avg draft acceptance 37% (30-42%) · per-position ~0.58/0.33/0.19.
---

**Decode 230.18 tok/s aggregate at concurrency 8.** NVFP4 + RedHatAI EAGLE3 speculator, conc 8, for the crossover figure.

- **Image (pinned):** `vllm/vllm-openai:nightly-aarch64` @ `sha256:e414712fdc04…` — the SINGLE image for all 24 cells of this figure. Ready after **369 s**.
- **Workload:** ShareGPT V3, concurrency 8. **596/700 completed, 0 errors** before the **600 s time cap**.
- **Throughput:** decode **230.18 tok/s** aggregate, prefill 270.31 tok/s. TTFT median 217.9 ms, TPOT median 32.5 ms, req throughput 0.982/s.
- **Spec-decode acceptance:** mean acceptance length 2.10 (1.90-2.25) · avg draft acceptance 37% (30-42%) · per-position ~0.58/0.33/0.19 (num_speculative_tokens=3).
- **Memory: 107.48 GB** = vLLM `--gpu-memory-utilization 0.85` reservation, not the model footprint.
