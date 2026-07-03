---
title: DiffusionGemma-26B-A4B · vLLM · NVFP4 · conc 8
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
concurrency: 8
tags: [diffusiongemma-26b-a4b, NVIDIA, Gemma, NVFP4, 16-40B, conc-8]
status: done
prefill_toks: 292.29
decode_toks: 199.18
mem_gb: 108.80
mem_source: system MemAvailable delta (10s sampling) — NVFP4 MoE + diffusion bidirectional-attention KV (util 0.70)
measured_on: 2026-07-04
completed_at: 2026-07-04 00:33 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:e414712fdc04f61d98ccc58cb61232a0587a8c024544e9e6cf12f97b19b38172
run_command: |
  VLLM_IMAGE=vllm/vllm-openai:nightly-aarch64 scripts/bench-vllm-serving.sh nvidia/diffusiongemma-26B-A4B-it-NVFP4 65536 8 500 300 256 \
    --trust-remote-code --attention-backend TRITON_ATTN --reasoning-parser gemma4 --tool-call-parser gemma4 --enable-auto-tool-choice --gpu-memory-utilization 0.70
  # 265/500 prompts (hit the time cap), 0 errors, 305.6s. ready after 222s. TTFT median 8942.8 ms, TPOT median 0.0 ms, req thr 0.867/s.
---

**Decode 199.18 tok/s aggregate at concurrency 8.** DiffusionGemma NVFP4 (parallel 256-token denoising blocks), conc 8, for the crossover figure.

- **Image (pinned):** `vllm/vllm-openai:nightly-aarch64` @ `sha256:e414712fdc04…` — the SINGLE image for all 24 cells of this figure. Ready after **222 s**.
- **Workload:** ShareGPT V3, concurrency 8. **265/500 completed, 0 errors** before the **300 s time cap**.
- **Throughput:** decode **199.18 tok/s** aggregate, prefill 292.29 tok/s. TTFT median 8942.8 ms, TPOT median 0.0 ms, req throughput 0.867/s.
- **TPOT is meaningless here** — decode happens in 256-token parallel denoising blocks, so the client's per-token latency reads near-zero. **Trust the aggregate decode tok/s only.**
- **Reduced load (util 0.70, not 0.85).** At `--gpu-memory-utilization 0.85` this cell hung the box — the ~103 GB KV reservation **plus** diffusion's runtime denoising buffers exceeded the 121 GB unified ceiling. Re-run at **0.70** (reservation ~84 GB) it peaked at **108.80 GB** (~12 GB under the ceiling), 0 errors. Shorter 300 s window — decode tok/s is a steady-state rate, unaffected.
- **Memory: 108.80 GB** peak (MemAvailable delta) = ~84 GB vLLM KV reservation (util 0.70) **plus** diffusion's denoising/activation buffers (~25 GB) — not just the reservation. That buffer overhead on top of a 0.85 reservation is exactly what breached the ceiling at higher concurrency.
