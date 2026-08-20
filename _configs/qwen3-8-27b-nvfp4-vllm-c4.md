---
title: Qwen3.8-27B · vLLM · NVFP4 · conc-4
model: Qwen/Qwen3.8-27B
company: Alibaba
family: Qwen
params: 27B (dense, hybrid linear-attn)
engine: vLLM
quant: NVFP4
quant_rationale: Same unsloth NVFP4 checkpoint as the conc-32 headline — only --max-num-seqs differs. Fills the c2→c8 gap in the concurrency curve, and the non-speculative baseline for the conc-4 MTP config.
source_repo: unsloth/Qwen3.8-27B-NVFP4
download_url: https://huggingface.co/unsloth/Qwen3.8-27B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 4
tags: [qwen3.8-27b, Alibaba, Qwen, NVFP4, 16-40B, conc-4]
status: done
prefill_toks: 48.39
decode_toks: 38.62
mem_gb: 102.91
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85)
measured_on: 2026-08-21
completed_at: 2026-08-21 01:49 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:677afd5bf3b4bb9881f91e107af7098f8410726b4c05b25cb4a815900b398204
run_command: |
  # conc-4 point. Identical to the conc-32 base recipe except --max-num-seqs.
  scripts/bench-vllm-serving.sh unsloth/Qwen3.8-27B-NVFP4 65536 4 1000 900 256 \
    --trust-remote-code --dtype bfloat16
  # 151/1000 prompts in the 900 s window, 0 errors. ready after 343 s.
  # TTFT median 314.5 ms, TPOT median 99.7 ms.
---

**38.6 tok/s at conc-4 — batch scaling is still essentially free here.**

- **Result (conc 4):** prefill **48.39** / decode **38.62** tok/s; TTFT median **314.5 ms**, TPOT median
  **99.7 ms**. **151/1000, 0 errors**, hit the 900 s cap. Load 343 s.
- **Near-perfect doubling up to c8.** Decode goes 11.16 → 20.11 → **38.62** → 75.04 tok/s for
  c1 → c2 → c4 → c8: per-step ratios of **1.80×, 1.92×, 1.94×**. Below c8 this box is memory-bandwidth
  bound with compute to spare, so each added stream is nearly a free extra token stream. Per-stream TPOT
  over that whole range moves only 88.5 → 99.7 ms (**+13%**).
- **c4 costs a single user ~12% latency for 3.5× the aggregate throughput** versus running alone. If the
  deployment has more than one user, there is no reason to run below c4.
- **Memory 102.9 GB**, the low point of the sweep's 103–107 GB band — noise on the
  `gpu-memory-utilization` reservation, not a concurrency effect. Resident breakdown on the
  [conc-32 base]({{ site.baseurl }}/configs/qwen3-8-27b-nvfp4-vllm-c32/).
- Base-vs-MTP comparison on [conc-4 + MTP]({{ site.baseurl }}/configs/qwen3-8-27b-nvfp4-vllm-mtp-c4/).
- Served text-only (`mm_served: false`), ctx 65536, consistent with the rest of the sweep.
