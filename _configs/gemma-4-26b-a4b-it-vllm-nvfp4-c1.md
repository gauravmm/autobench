---
title: Gemma 4 26B-A4B · vLLM · NVFP4 · conc 1
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
concurrency: 1
tags: [gemma-4-26b-a4b, Google, Gemma, NVFP4, 16-40B, conc-1]
status: done
prefill_toks: 59.01
decode_toks: 29.47
mem_gb: 108.21
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85)
measured_on: 2026-07-03
completed_at: 2026-07-03 15:15 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:e414712fdc04f61d98ccc58cb61232a0587a8c024544e9e6cf12f97b19b38172
run_command: |
  VLLM_IMAGE=vllm/vllm-openai:nightly-aarch64 scripts/bench-vllm-serving.sh nvidia/Gemma-4-26B-A4B-NVFP4 65536 1 300 300 256
  # 37/300 prompts (hit the time cap), 0 errors, 304.5s. ready after 306s. TTFT median 101.7 ms, TPOT median 33.1 ms, req thr 0.121/s.
---

**Decode 29.47 tok/s aggregate at concurrency 1.** Autoregressive NVFP4 reference point, conc 1, for the decode-vs-concurrency crossover figure.

- **Image (pinned):** `vllm/vllm-openai:nightly-aarch64` @ `sha256:e414712fdc04…` — the SINGLE image for all 24 cells of this figure. Ready after **306 s**.
- **Workload:** ShareGPT V3, concurrency 1. **37/300 completed, 0 errors** before the **300 s time cap**.
- **Throughput:** decode **29.47 tok/s** aggregate, prefill 59.01 tok/s. TTFT median 101.7 ms, TPOT median 33.1 ms, req throughput 0.121/s.
- **Memory: 108.21 GB** = vLLM `--gpu-memory-utilization 0.85` reservation, not the model footprint.
