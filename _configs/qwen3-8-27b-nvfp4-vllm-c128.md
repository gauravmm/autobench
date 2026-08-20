---
title: Qwen3.8-27B · vLLM · NVFP4 · conc-128
model: Qwen/Qwen3.8-27B
company: Alibaba
family: Qwen
params: 27B (dense, hybrid linear-attn)
engine: vLLM
quant: NVFP4
quant_rationale: Same unsloth NVFP4 checkpoint as the conc-32 headline — only --max-num-seqs differs. Top of the concurrency curve, and the non-speculative baseline for the conc-128 MTP config.
source_repo: unsloth/Qwen3.8-27B-NVFP4
download_url: https://huggingface.co/unsloth/Qwen3.8-27B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 128
tags: [qwen3.8-27b, Alibaba, Qwen, NVFP4, 16-40B, conc-128]
status: done
prefill_toks: 445.24
decode_toks: 346.23
mem_gb: 106.18
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85)
measured_on: 2026-08-21
completed_at: 2026-08-21 03:48 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:677afd5bf3b4bb9881f91e107af7098f8410726b4c05b25cb4a815900b398204
run_command: |
  # conc-128 point. Identical to the conc-32 base recipe except --max-num-seqs.
  scripts/bench-vllm-serving.sh unsloth/Qwen3.8-27B-NVFP4 65536 128 1000 900 256 \
    --trust-remote-code --dtype bfloat16
  # 1000/1000 prompts in 686.3 s — DRAINED the dataset, did NOT hit the 900 s cap. 0 errors.
  # ready after 339 s. TTFT median 1251.1 ms, TPOT median 349.1 ms.
---

**346.2 tok/s at conc-128 — the throughput ceiling of this model on a Spark, and it is not worth it.**

- **Result (conc 128):** prefill **445.24** / decode **346.23** tok/s; TTFT median **1251.1 ms**, TPOT
  median **349.1 ms**. **1000/1000 completed in 686.3 s, 0 errors.** Load 339 s.
- **Like c64, this run drained the dataset rather than hitting the time cap**, so the aggregate includes
  a ramp-down tail and reads as a floor. A saturated `--num-prompts 4000` re-run is recorded below when
  available; the 1000-prompt figure stays the headline so the c1…c128 curve is recipe-identical
  throughout.
- **The curve has flattened out.** Per-doubling gain: 1.94× (c4→c8) → 1.71× (c8→c16) → 1.63× (c16→c32) →
  1.35× (c32→c64) → **1.22×** (c64→c128). Aggregate throughput is asymptoting somewhere near
  **~370–400 tok/s** for this model at this quant on this box.
- **Per-stream latency has collapsed: TPOT 349.1 ms ≈ 2.9 tok/s per user**, versus 88.5 ms (11.3 tok/s)
  at c1. Quadrupling the batch from c32 bought **1.65× aggregate throughput for 2.4× worse per-token
  latency** — a losing trade unless the workload is entirely offline. **The useful operating range on
  this box is c4–c32;** c64 and c128 exist here to bound the curve, not to be deployed.
- **Memory 106.2 GB**, still mid-band — `--max-num-seqs` does not move the static reservation. (The MTP
  variant at this batch is the one exception on the whole sweep; see below.)
- Base-vs-MTP comparison on
  [conc-128 + MTP]({{ site.baseurl }}/configs/qwen3-8-27b-nvfp4-vllm-mtp-c128/) — where the speculative
  speedup finally reaches zero.
- Served text-only (`mm_served: false`), ctx 65536, consistent with the rest of the sweep.
