---
title: Gemma 4 26B-A4B · vLLM · NVFP4 + EAGLE3 · conc 16
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
concurrency: 16
tags: [gemma-4-26b-a4b, Google, Gemma, NVFP4, 16-40B, conc-16]
status: done
prefill_toks: 430.9
decode_toks: 376.25
mem_gb: 108.85
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85) + EAGLE3 head
spec_acceptance: mean acceptance length 2.08 (1.86-2.21) · avg draft acceptance 36% (29-40%) · per-position ~0.58/0.32/0.18
measured_on: 2026-07-03
completed_at: 2026-07-03 17:54 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:e414712fdc04f61d98ccc58cb61232a0587a8c024544e9e6cf12f97b19b38172
run_command: |
  VLLM_IMAGE=vllm/vllm-openai:nightly-aarch64 scripts/bench-vllm-serving.sh nvidia/Gemma-4-26B-A4B-NVFP4 65536 16 1000 700 256 \
    --speculative-config '{"model":"RedHatAI/gemma-4-26B-A4B-it-speculator.eagle3","method":"eagle3","num_speculative_tokens":3}'
  # 1000/1000 prompts (clean full run), 0 errors, 625.4s. ready after 314s. TTFT median 256.9 ms, TPOT median 39.7 ms, req thr 1.599/s.
  # SpecDecoding: mean acceptance length 2.08 (1.86-2.21) · avg draft acceptance 36% (29-40%) · per-position ~0.58/0.32/0.18.
---

**Decode 376.25 tok/s aggregate at concurrency 16.** NVFP4 + RedHatAI EAGLE3 speculator, conc 16, for the crossover figure.

- **Image (pinned):** `vllm/vllm-openai:nightly-aarch64` @ `sha256:e414712fdc04…` — the SINGLE image for all 24 cells of this figure. Ready after **314 s**.
- **Workload:** ShareGPT V3, concurrency 16. **1000/1000, 0 errors** in **625.4 s** (clean full run).
- **Throughput:** decode **376.25 tok/s** aggregate, prefill 430.9 tok/s. TTFT median 256.9 ms, TPOT median 39.7 ms, req throughput 1.599/s.
- **Spec-decode acceptance:** mean acceptance length 2.08 (1.86-2.21) · avg draft acceptance 36% (29-40%) · per-position ~0.58/0.32/0.18 (num_speculative_tokens=3).
- **Memory: 108.85 GB** = vLLM `--gpu-memory-utilization 0.85` reservation, not the model footprint.
