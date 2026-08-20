---
title: Qwen3.8-27B · vLLM · NVFP4 · conc-16
model: Qwen/Qwen3.8-27B
company: Alibaba
family: Qwen
params: 27B (dense, hybrid linear-attn)
engine: vLLM
quant: NVFP4
quant_rationale: Same unsloth NVFP4 checkpoint as the conc-32 headline — only --max-num-seqs differs. Fills the c8→c32 gap, and the non-speculative baseline for the conc-16 MTP config.
source_repo: unsloth/Qwen3.8-27B-NVFP4
download_url: https://huggingface.co/unsloth/Qwen3.8-27B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 16
tags: [qwen3.8-27b, Alibaba, Qwen, NVFP4, 16-40B, conc-16]
status: done
prefill_toks: 148.98
decode_toks: 128.60
mem_gb: 105.21
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85)
measured_on: 2026-08-21
completed_at: 2026-08-21 02:33 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:677afd5bf3b4bb9881f91e107af7098f8410726b4c05b25cb4a815900b398204
run_command: |
  # conc-16 point. Identical to the conc-32 base recipe except --max-num-seqs.
  scripts/bench-vllm-serving.sh unsloth/Qwen3.8-27B-NVFP4 65536 16 1000 900 256 \
    --trust-remote-code --dtype bfloat16
  # 499/1000 prompts in the 900 s window, 0 errors. ready after 368 s.
  # TTFT median 374.1 ms, TPOT median 118.7 ms.
---

**128.6 tok/s at conc-16 — the point where free batch scaling ends.**

- **Result (conc 16):** prefill **148.98** / decode **128.60** tok/s; TTFT median **374.1 ms**, TPOT
  median **118.7 ms**. **499/1000, 0 errors**, hit the 900 s cap. Load 368 s.
- **Scaling per doubling breaks here.** c1→c8 ran at **1.80× / 1.92× / 1.94×** per doubling; c8→c16 is
  **1.71×** and c16→c32 is **1.63×**. Up to c8 the GB10 is memory-bandwidth bound with idle compute, so
  extra streams ride along free; from c16 the batched GEMMs are large enough to actually occupy the
  tensor cores and each added stream starts costing real work.
- **Prefill saturates first:** 114.9 (c8) → **149.0** (c16), only **1.30×** for 2× the batch, versus
  1.71× on decode. Prefill was already compute-bound at c8, so batching it buys much less than batching
  decode — which is also why TTFT degrades faster than TPOT across this sweep.
- **Per-stream TPOT 118.7 ms** (+17% over c8's 101.5, +34% over the c1 floor of 88.5). Still comfortable
  — a user at c16 sees roughly one third worse per-token latency than having the box to themselves, for
  11.5× the aggregate throughput.
- **Memory 105.2 GB**, mid-band. Resident breakdown on the
  [conc-32 base]({{ site.baseurl }}/configs/qwen3-8-27b-nvfp4-vllm-c32/).
- Base-vs-MTP comparison on [conc-16 + MTP]({{ site.baseurl }}/configs/qwen3-8-27b-nvfp4-vllm-mtp-c16/).
- Served text-only (`mm_served: false`), ctx 65536, consistent with the rest of the sweep.
