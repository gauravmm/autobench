---
title: Qwen3.8-27B · vLLM · NVFP4 · conc-1
model: Qwen/Qwen3.8-27B
company: Alibaba
family: Qwen
params: 27B (dense, hybrid linear-attn)
engine: vLLM
quant: NVFP4
quant_rationale: Same unsloth NVFP4 checkpoint as the conc-32 headline — only --max-num-seqs differs. Single-stream latency point, and the non-speculative baseline the conc-1 MTP config is measured against.
source_repo: unsloth/Qwen3.8-27B-NVFP4
download_url: https://huggingface.co/unsloth/Qwen3.8-27B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 1
tags: [qwen3.8-27b, Alibaba, Qwen, NVFP4, 16-40B, conc-1]
status: done
prefill_toks: 22.87
decode_toks: 11.16
mem_gb: 105.37
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85)
measured_on: 2026-08-15
completed_at: 2026-08-15 11:56 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:677afd5bf3b4bb9881f91e107af7098f8410726b4c05b25cb4a815900b398204
run_command: |
  # conc-1 single-stream point. Identical to the conc-32 base recipe except --max-num-seqs.
  scripts/bench-vllm-serving.sh unsloth/Qwen3.8-27B-NVFP4 65536 1 1000 900 256 \
    --trust-remote-code --dtype bfloat16
  # 41/1000 prompts in the 900 s window (single stream — the cap is expected here), 0 errors.
  # ready after 354 s. TTFT median 177.1 ms, TPOT median 88.5 ms.
---

**Single-stream floor for the 27B: 11.3 tok/s per stream (TPOT 88.5 ms), TTFT 177 ms.** The
non-speculative conc-1 baseline; [`+MTP`]({{ site.baseurl }}/configs/qwen3-8-27b-nvfp4-vllm-mtp-c1/) doubles it.

- **Result (conc 1):** decode **11.16** tok/s aggregate, TPOT median **88.5 ms** (≈11.3 tok/s
  per-stream — at conc-1 the two agree, which is the point of the config), TTFT median **177.1 ms**,
  prefill 22.87 tok/s aggregate. **41/1000, 0 errors**, hit the 900 s cap as expected for a single
  stream.
- **Read TPOT, not `decode_toks`, when comparing conc-1 runs across pages.** The aggregate is averaged
  over the whole window including post-load ramp, so it is sensitive to how long the window was and how
  many requests landed in it. The Qwen3.6-27B conc-1 pages used different caps (500 prompts/600 s base,
  200/300 s for MTP) and completed only 22 and 20 requests — their aggregates are not directly
  comparable to this 41-request run. This sweep uses the same 1000/900 s cap at every concurrency so the
  c1/c8/c32 points are internally consistent.
- **Memory is essentially concurrency-independent here:** 105.4 GB vs 104.1 at conc-32. vLLM reserves
  `gpu-memory-utilization`·121 GB up front regardless of `--max-num-seqs`; only the CUDA-graph capture
  set and activation buffers scale with it, and at c1 those are tiny. The headline memory of a conc-1
  run says nothing about how much a single stream actually needs.
- **Load 354 s**, down from the conc-32 base run's 571 s — weights were already in the page cache. The
  38 s torch.compile did *not* come off: `--max-num-seqs` feeds `cudagraph_capture_sizes`, which is part
  of the compile-cache key, so every concurrency point mints a fresh cache entry under
  `~/.cache/vllm/torch_compile_cache/`. Expected, not a misconfiguration — a hit needs an exact re-run.
- Served text-only (`mm_served: false`), ctx 65536, consistent with the rest of the sweep.
