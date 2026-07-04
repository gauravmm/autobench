---
title: Gemma 4 26B-A4B · vLLM · NVFP4 + EAGLE3
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
concurrency: 32
tags: [gemma-4-26b-a4b, Google, Gemma, NVFP4, 16-40B, conc-32]
status: done
prefill_toks: 680.76
decode_toks: 596.32
mem_gb: 110.02
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85) + EAGLE3 head
spec_acceptance: mean acceptance length 2.06 (1.89-2.20) · avg draft acceptance 35% (30-40%) · per-position ~0.57/0.32/0.17
measured_on: 2026-07-03
completed_at: 2026-07-03 17:54 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:e414712fdc04f61d98ccc58cb61232a0587a8c024544e9e6cf12f97b19b38172
run_command: |
  VLLM_IMAGE=vllm/vllm-openai:nightly-aarch64 scripts/bench-vllm-serving.sh nvidia/Gemma-4-26B-A4B-NVFP4 65536 32 1000 900 256 \
    --speculative-config '{"model":"RedHatAI/gemma-4-26B-A4B-it-speculator.eagle3","method":"eagle3","num_speculative_tokens":3}'
  # 1000/1000 prompts (clean full run), 0 errors, 395.9s. ready after 311s. TTFT median 307.5 ms, TPOT median 49.6 ms, req thr 2.526/s.
  # SpecDecoding: mean acceptance length 2.06 (1.89-2.20) · avg draft acceptance 35% (30-40%) · per-position ~0.57/0.32/0.17.
---

**Decode 596.32 tok/s aggregate at concurrency 32.** NVFP4 + RedHatAI EAGLE3 speculator, conc 32, for the crossover figure.

- **Image (pinned):** `vllm/vllm-openai:nightly-aarch64` @ `sha256:e414712fdc04…` — the SINGLE image for all 24 cells of this figure. Ready after **311 s**.
- **Workload:** ShareGPT V3, concurrency 32. **1000/1000, 0 errors** in **395.9 s** (clean full run).
- **Throughput:** decode **596.32 tok/s** aggregate, prefill 680.76 tok/s. TTFT median 307.5 ms, TPOT median 49.6 ms, req throughput 2.526/s.
- **Spec-decode acceptance:** mean acceptance length 2.06 (1.89-2.20) · avg draft acceptance 35% (30-40%) · per-position ~0.57/0.32/0.17 (num_speculative_tokens=3).
- **Memory: 110.02 GB** = vLLM `--gpu-memory-utilization 0.85` reservation, not the model footprint.
