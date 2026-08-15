---
title: Qwen3.8-27B · vLLM · NVFP4 · conc-8
model: Qwen/Qwen3.8-27B
company: Alibaba
family: Qwen
params: 27B (dense, hybrid linear-attn)
engine: vLLM
quant: NVFP4
quant_rationale: Same unsloth NVFP4 checkpoint as the conc-32 headline — only --max-num-seqs differs. Mid-batch point of the c1/c8/c32 curve, and the non-speculative baseline for the conc-8 MTP config.
source_repo: unsloth/Qwen3.8-27B-NVFP4
download_url: https://huggingface.co/unsloth/Qwen3.8-27B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 8
tags: [qwen3.8-27b, Alibaba, Qwen, NVFP4, 16-40B, conc-8]
status: done
prefill_toks: 114.92
decode_toks: 75.04
mem_gb: 107.30
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85)
measured_on: 2026-08-15
completed_at: 2026-08-15 12:39 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:677afd5bf3b4bb9881f91e107af7098f8410726b4c05b25cb4a815900b398204
run_command: |
  # conc-8 point. Identical to the conc-32 base recipe except --max-num-seqs.
  scripts/bench-vllm-serving.sh unsloth/Qwen3.8-27B-NVFP4 65536 8 1000 900 256 \
    --trust-remote-code --dtype bfloat16
  # 288/1000 prompts in the 900 s window, 0 errors. ready after 339 s.
  # TTFT median 345.3 ms, TPOT median 101.5 ms.
---

**Mid-batch point of the NVFP4 curve: 75.0 tok/s decode at conc-8.**

- **Result (conc 8):** prefill **114.9** / decode **75.04** tok/s; TTFT median **345.3 ms**, TPOT median
  **101.5 ms**. **288/1000, 0 errors**, hit the 900 s cap. Load 339 s (fastest of the sweep — weights
  fully warm in page cache).
- **Batch scaling across the sweep** (decode tok/s, all NVFP4 base, same 1000/900 s cap, ctx 65536):

  | conc | decode | vs c1 | per-stream TPOT |
  |------|--------|-------|-----------------|
  | 1    | 11.16  | 1.0×  | 88.5 ms |
  | 8    | 75.04  | 6.7×  | 101.5 ms |
  | 32   | 209.97 | 18.8× | 144.1 ms |

  **Aggregate throughput scales strongly but sublinearly** — 6.7× for 8× the batch, then 2.8× more for
  4× the batch (18.8× total at 32×). Per-stream TPOT degrades gently, 88.5 → 101.5 → 144.1 ms, so a
  single user's experience is only ~15% worse at c8 than alone on the box. **c8 is the sweet spot for a
  small multi-user deployment**: near-linear aggregate gain with almost no per-stream latency cost.
- **Memory 107.3 GB**, within noise of the c1 (105.4) and c32 (104.1) runs — the reservation is set by
  `gpu-memory-utilization`, not concurrency. See the [conc-32 base](qwen3-8-27b-nvfp4-vllm-c32) for the
  resident breakdown and the silent FP8-KV-cache note.
- Served text-only (`mm_served: false`), consistent with the rest of the sweep.
