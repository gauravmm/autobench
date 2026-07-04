---
title: Gemma 4 26B-A4B · vLLM · NVFP4 · conc 256
model: google/gemma-4-26B-A4B-it
company: Google
family: Gemma
params: 26B / 4B (MoE)
engine: vLLM
quant: NVFP4
quant_rationale: NVIDIA's own NVFP4 build (modelopt) — Blackwell-native 4-bit. Autoregressive reference line (no drafter) for the crossover figure. c256 point of the beyond-c32 ceiling-finding extension — base survives c256 where MTP/EAGLE3 collapse.
source_repo: nvidia/Gemma-4-26B-A4B-NVFP4
download_url: https://huggingface.co/nvidia/Gemma-4-26B-A4B-NVFP4
context: 65536
modalities: [text, image]
mm_served: false
concurrency: 256
tags: [gemma-4-26b-a4b, Google, Gemma, NVFP4, 16-40B, conc-256]
status: done
prefill_toks: 1563.93
decode_toks: 1365.89
mem_gb: 108.70
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85); ~10 GB free at peak, FLAT across c64/c128/c256 (no draft buffers)
measured_on: 2026-07-04
completed_at: 2026-07-04 13:01 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:e414712fdc04f61d98ccc58cb61232a0587a8c024544e9e6cf12f97b19b38172
run_command: |
  # Run under scripts/mem-watchdog.sh (floor 3.5 GB) — GB10 unified memory; see notes/BENCHMARKING.md.
  VLLM_IMAGE=vllm/vllm-openai:nightly-aarch64 scripts/bench-vllm-serving.sh nvidia/Gemma-4-26B-A4B-NVFP4 65536 256 1000 900 256
  # 1000/1000 prompts (clean full run), 0 errors, 172.3s. ready after 317s. TTFT median 768.9 ms, TPOT median 164.6 ms, req thr 5.803/s. Watchdog no trip (10 GB free).
---

**Decode 1365.89 tok/s aggregate at concurrency 256 — base sails clean through the point where MTP collapsed.** Autoregressive NVFP4 reference, top of the planned beyond-c32 sweep (context held at 65536).

- **The headline contrast of this whole extension:** at c256 the **MTP line collapsed** (9/1000 completed, 512 errors — draft-slot scheduler cap + memory wall) while the **base line runs 1000/1000, 0 errors at 1365.89 tok/s**. No draft head means no `max_num_scheduled_tokens=2496` throttle and no per-seq draft buffers — so base neither thrashes the scheduler nor exhausts memory.
- **Still climbing, not saturated:** decode **1365.89** vs c128 (995.1) = **1.37× per doubling** — base has NOT plateaued even at c256. And memory is **flat at ~10 GB free** (108.70 delta, essentially unchanged from c64/c128). So base is neither compute- nor memory-bound here: **its true ceiling is beyond c256** (unexplored — c512 would be the next rung; capped at c256 for this sweep). Note base at c256 (1366) essentially matches MTP at its own top c128 (1380).
- **Image (pinned):** `vllm/vllm-openai:nightly-aarch64` @ `sha256:e414712fdc04…`. Ready after 317 s. Watchdog (floor 3.5 GB) armed, did not trip.
- **Workload:** ShareGPT V3, concurrency 256. **1000/1000, 0 errors** in **172.3 s** (no time cap). TTFT median 768.9 ms, TPOT median 164.6 ms, req throughput 5.803/s.
</content>
</invoke>
