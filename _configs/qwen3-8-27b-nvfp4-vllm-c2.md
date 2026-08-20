---
title: Qwen3.8-27B · vLLM · NVFP4 · conc-2
model: Qwen/Qwen3.8-27B
company: Alibaba
family: Qwen
params: 27B (dense, hybrid linear-attn)
engine: vLLM
quant: NVFP4
quant_rationale: Same unsloth NVFP4 checkpoint as the conc-32 headline — only --max-num-seqs differs. Fills the c1→c8 gap in the concurrency curve, and the non-speculative baseline for the conc-2 MTP config.
source_repo: unsloth/Qwen3.8-27B-NVFP4
download_url: https://huggingface.co/unsloth/Qwen3.8-27B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 2
tags: [qwen3.8-27b, Alibaba, Qwen, NVFP4, 16-40B, conc-2]
status: done
prefill_toks: 40.41
decode_toks: 20.11
mem_gb: 103.14
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85)
measured_on: 2026-08-21
completed_at: 2026-08-21 01:06 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:677afd5bf3b4bb9881f91e107af7098f8410726b4c05b25cb4a815900b398204
run_command: |
  # conc-2 point. Identical to the conc-32 base recipe except --max-num-seqs.
  scripts/bench-vllm-serving.sh unsloth/Qwen3.8-27B-NVFP4 65536 2 1000 900 256 \
    --trust-remote-code --dtype bfloat16
  # 80/1000 prompts in the 900 s window, 0 errors. ready after 344 s.
  # TTFT median 301.1 ms, TPOT median 96.3 ms.
---

**20.1 tok/s at conc-2 — 1.80× the single stream for 2× the batch.**

- **Result (conc 2):** prefill **40.41** / decode **20.11** tok/s; TTFT median **301.1 ms**, TPOT median
  **96.3 ms**. **80/1000, 0 errors**, hit the 900 s cap. Load 344 s.
- **Scaling from c1:** 11.16 → 20.11 tok/s (**1.80×** for 2× the batch) while per-stream TPOT slips
  88.5 → 96.3 ms (**+8.8%**). Cheapest doubling on the whole curve — two users cost almost nothing
  relative to one.
- **TTFT rises faster than TPOT** (177.1 → 301.1 ms, +70%): with two streams a request routinely waits
  behind a peer's prefill chunk, and prefill is the serialized part. Decode interleaves; prefill queues.
- **Memory 103.1 GB**, the low end of the sweep's 103–107 GB band, which is measurement noise on the
  `gpu-memory-utilization` reservation rather than a concurrency effect — see the
  [conc-32 base]({{ site.baseurl }}/configs/qwen3-8-27b-nvfp4-vllm-c32/) for the resident breakdown.
- Full base-vs-MTP curve on [conc-2 + MTP]({{ site.baseurl }}/configs/qwen3-8-27b-nvfp4-vllm-mtp-c2/).
- Served text-only (`mm_served: false`), ctx 65536, consistent with the rest of the sweep.
