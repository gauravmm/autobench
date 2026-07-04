---
title: Gemma 4 26B-A4B · vLLM · NVFP4
model: google/gemma-4-26B-A4B-it
company: Google
family: Gemma
params: 26B / 4B (MoE)
engine: vLLM
quant: NVFP4
quant_rationale: NVIDIA's own NVFP4 build (TensorRT-Model-Optimizer / modelopt) — Blackwell-native 4-bit. The autoregressive reference line (no drafter) for the decode-vs-concurrency crossover figure.
source_repo: nvidia/Gemma-4-26B-A4B-NVFP4
download_url: https://huggingface.co/nvidia/Gemma-4-26B-A4B-NVFP4
context: 65536
modalities: [text, image]
mm_served: false
concurrency: 32
tags: [gemma-4-26b-a4b, Google, Gemma, NVFP4, 16-40B, conc-32]
status: done
prefill_toks: 480.96
decode_toks: 421.13
mem_gb: 108.58
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85)
measured_on: 2026-07-03
completed_at: 2026-07-03 15:15 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:e414712fdc04f61d98ccc58cb61232a0587a8c024544e9e6cf12f97b19b38172
run_command: |
  VLLM_IMAGE=vllm/vllm-openai:nightly-aarch64 scripts/bench-vllm-serving.sh nvidia/Gemma-4-26B-A4B-NVFP4 65536 32 1000 900 256
  # 1000/1000 prompts (clean full run), 0 errors, 560.3s. ready after 323s. TTFT median 230.5 ms, TPOT median 72.9 ms, req thr 1.785/s.
---

**Decode 421.13 tok/s aggregate at concurrency 32.** Autoregressive NVFP4 reference point, conc 32, for the decode-vs-concurrency crossover figure.

- **Image (pinned):** `vllm/vllm-openai:nightly-aarch64` @ `sha256:e414712fdc04…` — the SINGLE image for all 24 cells of this figure. Ready after **323 s**.
- **Workload:** ShareGPT V3, concurrency 32. **1000/1000, 0 errors** in **560.3 s** (clean full run).
- **Throughput:** decode **421.13 tok/s** aggregate, prefill 480.96 tok/s. TTFT median 230.5 ms, TPOT median 72.9 ms, req throughput 1.785/s.
- **Memory: 108.58 GB** = vLLM `--gpu-memory-utilization 0.85` reservation, not the model footprint.
