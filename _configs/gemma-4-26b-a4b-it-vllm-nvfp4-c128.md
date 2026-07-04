---
title: Gemma 4 26B-A4B · vLLM · NVFP4 · conc 128
model: google/gemma-4-26B-A4B-it
company: Google
family: Gemma
params: 26B / 4B (MoE)
engine: vLLM
quant: NVFP4
quant_rationale: NVIDIA's own NVFP4 build (modelopt) — Blackwell-native 4-bit. Autoregressive reference line (no drafter) for the crossover figure. c128 point of the beyond-c32 ceiling-finding extension.
source_repo: nvidia/Gemma-4-26B-A4B-NVFP4
download_url: https://huggingface.co/nvidia/Gemma-4-26B-A4B-NVFP4
context: 65536
modalities: [text, image]
mm_served: false
concurrency: 128
tags: [gemma-4-26b-a4b, Google, Gemma, NVFP4, 16-40B, conc-128]
status: done
prefill_toks: 1142.2
decode_toks: 995.1
mem_gb: 109.32
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85); ~9.4 GB free at peak (no draft buffers, so roomier than the MTP/EAGLE3 lines)
measured_on: 2026-07-04
completed_at: 2026-07-04 12:52 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:e414712fdc04f61d98ccc58cb61232a0587a8c024544e9e6cf12f97b19b38172
run_command: |
  # Run under scripts/mem-watchdog.sh (floor 3.5 GB) — GB10 unified memory; see notes/BENCHMARKING.md.
  VLLM_IMAGE=vllm/vllm-openai:nightly-aarch64 scripts/bench-vllm-serving.sh nvidia/Gemma-4-26B-A4B-NVFP4 65536 128 1000 900 256
  # 1000/1000 prompts (clean full run), 0 errors, 235.9s. ready after 320s. TTFT median 396.8 ms, TPOT median 117.5 ms, req thr 4.238/s. Watchdog no trip (9.4 GB free).
---

**Decode 995.1 tok/s aggregate at concurrency 128 — still climbing, and with memory to spare.** Autoregressive NVFP4 reference, second point of the beyond-c32 ceiling-finding sweep (context held at 65536).

- **Compute still has clear headroom:** decode **995.1 tok/s** vs c64 (680.93) = **1.46× per doubling** — barely decelerating from c32→c64 (1.62×). Base is nowhere near a plateau at c128.
- **Roomier than the spec lines — the key contrast:** peak **109.32 GB delta = ~9.4 GB free**, essentially flat vs c64 (110.16). Because the base line carries **no MTP/EAGLE3 draft head and no per-seq draft-token buffers**, its memory doesn't climb with concurrency the way MTP does (mtp c128 sat at only ~4.5 GB free). This is why base — alone among the gemma lines — has the headroom to attempt c256.
- **Image (pinned):** `vllm/vllm-openai:nightly-aarch64` @ `sha256:e414712fdc04…`. Ready after 320 s. Watchdog (floor 3.5 GB) armed, did not trip.
- **Workload:** ShareGPT V3, concurrency 128. **1000/1000, 0 errors** in **235.9 s** (no time cap). TTFT median 396.8 ms, TPOT median 117.5 ms, req throughput 4.238/s.
</content>
</invoke>
