---
title: Qwen3.6-35B-A3B · vLLM · NVFP4 + MTP · conc 64
model: Qwen/Qwen3.6-35B-A3B
company: Alibaba
family: Qwen
params: 35B / 3B (MoE)
engine: vLLM
speculative: MTP
quant: NVFP4
quant_rationale: NVIDIA's official NVFP4 (nvidia/Qwen3.6-35B-A3B-NVFP4, ModelOpt v0.44.0) + the checkpoint's own MTP module, NVIDIA DGX Spark recipe (marlin base + triton MTP head). c64 point of the beyond-c32 ceiling-finding extension.
source_repo: nvidia/Qwen3.6-35B-A3B-NVFP4
download_url: https://huggingface.co/nvidia/Qwen3.6-35B-A3B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 64
tags: [qwen3.6-35b-a3b, Alibaba, Qwen, NVFP4, 16-40B, Spark recipe, conc-64]
status: done
prefill_toks: 691.31
decode_toks: 670.82
mem_gb: 109.82
mem_source: system MemAvailable delta (10s sampling) — NVFP4 MoE + in-repo MTP head; ~8.7 GB free at peak (util 0.85)
spec_acceptance: mean acceptance length 3.00 (2.96-3.00) · avg draft acceptance ~66% (65-67%) · per-position 0.83/0.65/0.51
measured_on: 2026-07-04
completed_at: 2026-07-04 12:09 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:68e23ddd982ad5642e21354c2242a3a86d31a3ea83f5937e5c3867942dc6595b
run_command: |
  # Run under scripts/mem-watchdog.sh (floor 6 GB) — GB10 unified memory; see the c256/crash note.
  VLLM_IMAGE=vllm/vllm-openai@sha256:68e23ddd982ad5642e21354c2242a3a86d31a3ea83f5937e5c3867942dc6595b \
  scripts/bench-vllm-serving.sh nvidia/Qwen3.6-35B-A3B-NVFP4 65536 64 1000 900 256 \
    --quantization modelopt --trust-remote-code --reasoning-parser qwen3 --moe-backend marlin \
    --speculative-config '{"method":"mtp","num_speculative_tokens":3,"moe_backend":"triton"}'
  # 1000/1000 prompts (clean full run), 0 errors, 381.2s. ready after 407s. req thr 2.623/s. Watchdog did NOT trip (8.7 GB free).
  # TPOT median 0.0 / TTFT median 21.6s = qwen3 reasoning-parser client artifacts — trust aggregate decode + SpecDecoding log.
  # SpecDecoding: mean acceptance length 3.00 · avg draft acceptance ~66% · per-position 0.83/0.65/0.51.
---

**Decode 670.82 tok/s aggregate at concurrency 64.** NVFP4 MoE + native MTP, first point of the beyond-c32 ceiling-finding sweep (context held at 65536; splices onto the c1–c32 curve). Run under the unified-memory watchdog after conc-256/c64 first crashed the box.

- **Still climbing but decelerating faster than gemma:** decode **670.82 tok/s** vs the c32 point (541.26) = **1.24× per doubling** — down from the c16→c32 step (1.25×) and well below gemma-mtp's c32→c64 (1.47×). This 35B-A3B line is closer to its knee than the 26B-A4B line at the same concurrency.
- **Memory ~8.7 GB free at peak (109.82 GB delta)** — essentially flat vs c32 (110.28, 8.2 GB free); the fixed 0.85 KV reservation dominates and c64 graph/activation growth is modest for this MoE. The [`mem-watchdog`](https://github.com/gauravmm/autobench) (floor 6 GB) was armed throughout and **did not trip**.
- **Acceptance healthy and flat:** mean acceptance length **3.00**, avg draft acceptance **~66%**, per-position **0.83/0.65/0.51** — identical to the c1–c32 points (~66–69%), confirming acceptance is workload-driven, not concurrency-driven.
- **Image (pinned):** `vllm/vllm-openai@sha256:68e23dd…` — the SAME image as the c1–c32 Qwen cells (the `nightly-aarch64` tag has since moved to `e414712f`; pinned by digest for a clean splice). Ready after 407 s.
- **Workload:** ShareGPT V3, concurrency 64. **1000/1000, 0 errors** in **381.2 s** (no time cap). TPOT/TTFT medians are the usual `qwen3` reasoning-parser client artifacts.
</content>
</invoke>
