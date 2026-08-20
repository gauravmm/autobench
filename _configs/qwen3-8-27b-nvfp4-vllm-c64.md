---
title: Qwen3.8-27B · vLLM · NVFP4 · conc-64
model: Qwen/Qwen3.8-27B
company: Alibaba
family: Qwen
params: 27B (dense, hybrid linear-attn)
engine: vLLM
quant: NVFP4
quant_rationale: Same unsloth NVFP4 checkpoint as the conc-32 headline — only --max-num-seqs differs. Extends the curve past the c32 headline, and the non-speculative baseline for the conc-64 MTP config.
source_repo: unsloth/Qwen3.8-27B-NVFP4
download_url: https://huggingface.co/unsloth/Qwen3.8-27B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 64
tags: [qwen3.8-27b, Alibaba, Qwen, NVFP4, 16-40B, conc-64]
status: done
prefill_toks: 363.75
decode_toks: 283.72
mem_gb: 105.39
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85)
measured_on: 2026-08-21
completed_at: 2026-08-21 03:13 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:677afd5bf3b4bb9881f91e107af7098f8410726b4c05b25cb4a815900b398204
run_command: |
  # conc-64 point. Identical to the conc-32 base recipe except --max-num-seqs.
  scripts/bench-vllm-serving.sh unsloth/Qwen3.8-27B-NVFP4 65536 64 1000 900 256 \
    --trust-remote-code --dtype bfloat16
  # 1000/1000 prompts in 840.0 s — DRAINED the dataset, did NOT hit the 900 s cap. 0 errors.
  # ready after 358 s. TTFT median 658.1 ms, TPOT median 209.1 ms.
---

**283.7 tok/s at conc-64 — and the first point where the sweep's run cap stops binding.**

- **Result (conc 64):** prefill **363.75** / decode **283.72** tok/s; TTFT median **658.1 ms**, TPOT
  median **209.1 ms**. **1000/1000 completed in 840.0 s, 0 errors.** Load 358 s.
- **Read this number as a floor, not a steady state.** Every point from c1 to c32 hit the 900 s time cap
  with prompts to spare, so its aggregate is pure steady-state throughput. At c64 the box chewed through
  all 1000 ShareGPT prompts in 840 s, so the average includes the **ramp-down tail** where fewer than 64
  slots are busy. Mean request latency is ≈64/1.19 ≈ **54 s**, so roughly the last 6% of the window is
  draining — real steady-state throughput is a few percent above 283.7. A saturated re-run at
  `--num-prompts 4000` is recorded below when available; the 1000-prompt figure is kept as the headline
  so the c1…c128 curve stays recipe-identical.
- **Scaling continues to flatten:** 1.94× (c4→c8) → 1.71× (c8→c16) → 1.63× (c16→c32) → **1.35×**
  (c32→c64), and that 1.35× is itself understated by the tail. The GB10 is firmly compute-bound at this
  batch.
- **Per-stream latency is where c64 actually costs you:** TPOT **209.1 ms**, up 45% from c32's 144.1 and
  **2.4× the c1 floor of 88.5 ms**. At ~5 tok/s per stream this is past what most interactive use
  tolerates. c64 is a batch-throughput setting, not a chat setting.
- **Memory 105.4 GB**, mid-band — unchanged by concurrency, as everywhere on this sweep. Resident
  breakdown on the [conc-32 base]({{ site.baseurl }}/configs/qwen3-8-27b-nvfp4-vllm-c32/).
- Base-vs-MTP comparison on [conc-64 + MTP]({{ site.baseurl }}/configs/qwen3-8-27b-nvfp4-vllm-mtp-c64/).
- Served text-only (`mm_served: false`), ctx 65536, consistent with the rest of the sweep.
