---
title: DiffusionGemma-26B-A4B · vLLM · NVFP4 · conc 1
model: nvidia/diffusiongemma-26B-A4B-it
company: NVIDIA
family: Gemma
params: 25.2B / 3.8B (MoE, diffusion)
engine: vLLM
quant: NVFP4
quant_rationale: NVIDIA's official NVFP4 (nvidia/diffusiongemma-26B-A4B-it-NVFP4, ModelOpt) discrete-diffusion Gemma-4 MoE — decodes in parallel 256-token denoising blocks (no drafter, no verify). The diffusion line of the crossover figure — fastest at low concurrency, saturates ~199 tok/s from conc 8 onward.
source_repo: nvidia/diffusiongemma-26B-A4B-it-NVFP4
download_url: https://huggingface.co/nvidia/diffusiongemma-26B-A4B-it-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 1
tags: [diffusiongemma-26b-a4b, NVIDIA, Gemma, NVFP4, 16-40B, conc-1]
status: done
prefill_toks: 141.01
decode_toks: 116.04
mem_gb: 112.02
mem_source: system MemAvailable delta (10s sampling) — NVFP4 MoE + diffusion bidirectional-attention KV (util 0.85)
measured_on: 2026-07-04
completed_at: 2026-07-04 00:33 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:e414712fdc04f61d98ccc58cb61232a0587a8c024544e9e6cf12f97b19b38172
run_command: |
  VLLM_IMAGE=vllm/vllm-openai:nightly-aarch64 scripts/bench-vllm-serving.sh nvidia/diffusiongemma-26B-A4B-it-NVFP4 65536 1 300 300 256 \
    --trust-remote-code --attention-backend TRITON_ATTN --reasoning-parser gemma4 --tool-call-parser gemma4 --enable-auto-tool-choice
  # 153/300 prompts (hit the time cap), 0 errors, 301.1s. ready after 419s. TTFT median 1950.0 ms, TPOT median 0.0 ms, req thr 0.508/s.
---

**Decode 116.04 tok/s aggregate at concurrency 1.** DiffusionGemma NVFP4 (parallel 256-token denoising blocks), conc 1, for the crossover figure.

- **Image (pinned):** `vllm/vllm-openai:nightly-aarch64` @ `sha256:e414712fdc04…` — the SINGLE image for all 24 cells of this figure. Ready after **419 s**.
- **Workload:** ShareGPT V3, concurrency 1. **153/300 completed, 0 errors** before the **300 s time cap**.
- **Throughput:** decode **116.04 tok/s** aggregate, prefill 141.01 tok/s. TTFT median 1950.0 ms, TPOT median 0.0 ms, req throughput 0.508/s.
- **TPOT is meaningless here** — decode happens in 256-token parallel denoising blocks, so the client's per-token latency reads near-zero. **Trust the aggregate decode tok/s only.**
- **Memory: 112.02 GB** peak (MemAvailable delta) = ~102 GB vLLM KV reservation (util 0.85) **plus** diffusion's denoising/activation buffers (~10 GB) — not just the reservation. That buffer overhead on top of a 0.85 reservation is exactly what breached the ceiling at higher concurrency.
