---
title: Gemma 4 26B-A4B · vLLM · NVFP4 · conc 64
model: google/gemma-4-26B-A4B-it
company: Google
family: Gemma
params: 26B / 4B (MoE)
engine: vLLM
quant: NVFP4
quant_rationale: NVIDIA's own NVFP4 build (TensorRT-Model-Optimizer / modelopt) — Blackwell-native 4-bit. The autoregressive reference line (no drafter) for the decode-vs-concurrency crossover figure. c64 point of the beyond-c32 ceiling-finding extension.
source_repo: nvidia/Gemma-4-26B-A4B-NVFP4
download_url: https://huggingface.co/nvidia/Gemma-4-26B-A4B-NVFP4
context: 65536
modalities: [text, image]
mm_served: false
concurrency: 64
tags: [gemma-4-26b-a4b, Google, Gemma, NVFP4, 16-40B, conc-64]
status: done
prefill_toks: 779.73
decode_toks: 680.93
mem_gb: 110.16
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85); ~8.5 GB free at peak
measured_on: 2026-07-04
completed_at: 2026-07-04 12:42 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:e414712fdc04f61d98ccc58cb61232a0587a8c024544e9e6cf12f97b19b38172
run_command: |
  # Run under scripts/mem-watchdog.sh (floor 3.5 GB) — GB10 unified memory; see notes/BENCHMARKING.md.
  VLLM_IMAGE=vllm/vllm-openai:nightly-aarch64 scripts/bench-vllm-serving.sh nvidia/Gemma-4-26B-A4B-NVFP4 65536 64 1000 900 256
  # 1000/1000 prompts (clean full run), 0 errors, 345.6s. ready after 312s. TTFT median 276.4 ms, TPOT median 86.9 ms, req thr 2.893/s. Watchdog no trip (8.5 GB free).
---

**Decode 680.93 tok/s aggregate at concurrency 64.** Autoregressive NVFP4 reference (no drafter), first point of the beyond-c32 ceiling-finding sweep (context held at 65536; splices onto the c1–c32 curve).

- **Base scales even harder than the spec lines here:** decode **680.93 tok/s** vs the c32 base point (421.13) = **1.62× per doubling** — steeper than MTP's c32→c64 (1.47×), because the base line has no drafter forward passes competing for compute, so more of the added batch turns into throughput. Lots of headroom left.
- **Memory ~8.5 GB free at peak (110.16 GB delta)** — the fixed 0.85 KV reservation dominates. Watchdog (floor 3.5 GB) armed throughout, did not trip.
- **Image (pinned):** `vllm/vllm-openai:nightly-aarch64` @ `sha256:e414712fdc04…` — same single image as the c1–c32 cells. Ready after 312 s.
- **Workload:** ShareGPT V3, concurrency 64. **1000/1000, 0 errors** in **345.6 s** (no time cap). TTFT median 276.4 ms, TPOT median 86.9 ms, req throughput 2.893/s (clean per-stream metrics — no reasoning parser on gemma-4).
</content>
</invoke>
