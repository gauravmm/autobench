---
title: Qwen3.8-27B · vLLM · FP8 (official)
model: Qwen/Qwen3.8-27B
company: Alibaba
family: Qwen
params: 27B (dense, hybrid linear-attn)
engine: vLLM
quant: FP8
quant_rationale: Alibaba's own FP8 release (Qwen/Qwen3.8-27B-FP8), dynamic-activation E4M3 with the first two vision blocks held out. The official, highest-trust quant — and the reference point the NVFP4 configs are measured against. Also the matched-precision control for the MTP acceptance question raised by the NVFP4+MTP run.
source_repo: Qwen/Qwen3.8-27B-FP8
download_url: https://huggingface.co/Qwen/Qwen3.8-27B-FP8
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 32
tags: [qwen3.8-27b, Alibaba, Qwen, FP8, 16-40B, conc-32]
status: done
prefill_toks: 196.26
decode_toks: 143.89
mem_gb: 108.04
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85)
measured_on: 2026-08-15
completed_at: 2026-08-15 10:50 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:677afd5bf3b4bb9881f91e107af7098f8410726b4c05b25cb4a815900b398204
run_command: |
  # Official Alibaba FP8 (quantization=fp8 auto-detected) on vLLM nightly-aarch64. Base, conc-32.
  scripts/bench-vllm-serving.sh Qwen/Qwen3.8-27B-FP8 65536 32 1000 900 256 \
    --trust-remote-code --dtype bfloat16
  # 573/1000 prompts, 0 errors, hit the 900 s time cap (939.7 s wall; cold load 641 s — ~27 GB
  # download across 66 shards). Zero preemptions.
---

**The official FP8 is the slow path on GB10 — NVFP4 beats it by 46% on decode, a much bigger gap than
the 21% measured on the Qwen3.6-27B generation.**

- **Result (conc 32):** prefill **196.3** / decode **143.9** tok/s; **573/1000, 0 errors**; hit the
  900 s cap (939.7 s wall, 641 s of it cold load — ~27 GB over 66 shards).
- **vs [NVFP4 base](qwen3-8-27b-nvfp4-vllm-c32):** 270.6 / 210.0 → NVFP4 is **+37.9% prefill,
  **+46.0% decode**. For reference the same comparison on Qwen3.6-27B was +7.6% / +21.4%, so the NVFP4
  advantage roughly doubled generation-over-generation.
- **The gap is real compute, not KV starvation.** FP8's KV reservation only supports **15.97×**
  concurrency at 65536 ctx (vs NVFP4's 32.5×) — below the requested `--max-num-seqs 32` — which looks
  like it should throttle the run. It does not: ShareGPT prompts are short, so **zero preemptions were
  logged**. The deficit is the FP8 kernels themselves. (It *would* bite on a long-context sweep.)
- **Memory (vLLM log):** weights + non-torch **32.18 GiB** (vs NVFP4's 25.15 — +7 GB, and NVFP4 keeps
  attention/lm_head/last-8-layer MLPs at FP8 anyway), peak activation **2.49 GiB**, CUDA-graph pool
  **0.26 GiB**, KV **68.77 GiB** = **1,046,391 tokens**.
- **KV precision differs between these two configs — read the memory comparison carefully.** This repo
  carries no `kv_cache_scheme`, so `kv_cache_dtype=auto` gives it a **BF16 KV cache**. The unsloth NVFP4
  checkpoint *does* carry one (static per-tensor E4M3) and therefore silently runs an **FP8 KV cache**,
  which is why its slightly larger reservation holds **2.04× the tokens** (2,128,554 vs 1,046,391).
  Neither run says so on the command line.
- **Hybrid cache alignment (both configs):** vLLM sets `Mamba cache mode = 'align'` and pads the
  attention block size to **784 tokens** so the attention page ≥ the GatedDeltaNet mamba page (mamba
  page padded 0.13% to match exactly). GDN prefill runs the Triton/FLA kernel, decode the CUDA kernel.
- Served text-only (`mm_served: false`), consistent with the rest of the sweep.
