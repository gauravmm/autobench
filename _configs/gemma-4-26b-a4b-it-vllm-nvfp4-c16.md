---
title: Gemma 4 26B-A4B · vLLM · NVFP4 · conc 16
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
concurrency: 16
tags: [gemma-4-26b-a4b, Google, Gemma, NVFP4, 16-40B, conc-16]
status: done
prefill_toks: 312.65
decode_toks: 273.61
mem_gb: 109.30
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85)
measured_on: 2026-07-03
completed_at: 2026-07-03 15:15 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:e414712fdc04f61d98ccc58cb61232a0587a8c024544e9e6cf12f97b19b38172
run_command: |
  VLLM_IMAGE=vllm/vllm-openai:nightly-aarch64 scripts/bench-vllm-serving.sh nvidia/Gemma-4-26B-A4B-NVFP4 65536 16 1000 700 256
  # 824/1000 prompts (hit the time cap), 0 errors, 711.5s. ready after 293s. TTFT median 186.1 ms, TPOT median 56.9 ms, req thr 1.158/s.
---

**Decode 273.61 tok/s aggregate at concurrency 16.** Autoregressive NVFP4 reference point, conc 16, for the decode-vs-concurrency crossover figure.

- **Image (pinned):** `vllm/vllm-openai:nightly-aarch64` @ `sha256:e414712fdc04…` — the SINGLE image for all 24 cells of this figure. Ready after **293 s**.
- **Workload:** ShareGPT V3, concurrency 16. **824/1000 completed, 0 errors** before the **700 s time cap**.
- **Throughput:** decode **273.61 tok/s** aggregate, prefill 312.65 tok/s. TTFT median 186.1 ms, TPOT median 56.9 ms, req throughput 1.158/s.
- **Memory: 109.30 GB** = vLLM `--gpu-memory-utilization 0.85` reservation, not the model footprint.
