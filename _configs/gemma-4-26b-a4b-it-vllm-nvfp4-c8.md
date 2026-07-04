---
title: Gemma 4 26B-A4B · vLLM · NVFP4 · conc 8
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
concurrency: 8
tags: [gemma-4-26b-a4b, Google, Gemma, NVFP4, 16-40B, conc-8]
status: done
prefill_toks: 191.42
decode_toks: 171.69
mem_gb: 109.47
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85)
measured_on: 2026-07-03
completed_at: 2026-07-03 15:15 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:e414712fdc04f61d98ccc58cb61232a0587a8c024544e9e6cf12f97b19b38172
run_command: |
  VLLM_IMAGE=vllm/vllm-openai:nightly-aarch64 scripts/bench-vllm-serving.sh nvidia/Gemma-4-26B-A4B-NVFP4 65536 8 700 600 256
  # 444/700 prompts (hit the time cap), 0 errors, 608.4s. ready after 298s. TTFT median 156.8 ms, TPOT median 45.3 ms, req thr 0.73/s.
---

**Decode 171.69 tok/s aggregate at concurrency 8.** Autoregressive NVFP4 reference point, conc 8, for the decode-vs-concurrency crossover figure.

- **Image (pinned):** `vllm/vllm-openai:nightly-aarch64` @ `sha256:e414712fdc04…` — the SINGLE image for all 24 cells of this figure. Ready after **298 s**.
- **Workload:** ShareGPT V3, concurrency 8. **444/700 completed, 0 errors** before the **600 s time cap**.
- **Throughput:** decode **171.69 tok/s** aggregate, prefill 191.42 tok/s. TTFT median 156.8 ms, TPOT median 45.3 ms, req throughput 0.73/s.
- **Memory: 109.47 GB** = vLLM `--gpu-memory-utilization 0.85` reservation, not the model footprint.
