---
title: Qwen3.8-27B · vLLM · NVFP4 + MTP · conc-1
model: Qwen/Qwen3.8-27B
company: Alibaba
family: Qwen
params: 27B (dense, hybrid linear-attn)
engine: vLLM
speculative: MTP
quant: NVFP4
quant_rationale: Same unsloth NVFP4 checkpoint plus its in-repo BF16 MTP head, at conc-1 — the best case for speculative decoding, where there is no batch to amortise the target forward and every accepted draft token is pure win.
source_repo: unsloth/Qwen3.8-27B-NVFP4
download_url: https://huggingface.co/unsloth/Qwen3.8-27B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 1
tags: [qwen3.8-27b, Alibaba, Qwen, NVFP4, 16-40B, conc-1]
status: done
prefill_toks: 41.91
decode_toks: 21.35
mem_gb: 106.52
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85) + MTP head
spec_acceptance: ~57% avg draft acceptance (steady-state range 42.8–74.6%, noisier than conc-32 on small per-window samples) · mean acceptance length ~2.8 (of a possible 4.0) · per-position ~0.78 / 0.56 / 0.44 (num_speculative_tokens=3)
measured_on: 2026-08-15
completed_at: 2026-08-15 11:56 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:677afd5bf3b4bb9881f91e107af7098f8410726b4c05b25cb4a815900b398204
run_command: |
  # conc-1 single-stream point with the in-repo MTP head. Same recipe as conc-32 except --max-num-seqs.
  scripts/bench-vllm-serving.sh unsloth/Qwen3.8-27B-NVFP4 65536 1 1000 900 256 \
    --trust-remote-code --dtype bfloat16 \
    --speculative-config '{"method":"mtp","num_speculative_tokens":3}'
  # 83/1000 prompts in the 900 s window (vs 41 for the non-spec baseline), 0 errors. ready after 380 s.
  # TTFT median 264.2 ms, TPOT median 44.6 ms.
---

**MTP nearly doubles single-stream speed: +91% decode, TPOT halved from 88.5 → 44.6 ms. The +31%
measured at conc-32 was a floor, exactly as expected — and this is the config to quote for
interactive, one-user-at-a-time use on the Spark.**

- **Result (conc 1):** decode **21.35** tok/s vs the [conc-1 base](qwen3-8-27b-nvfp4-vllm-c1)'s 11.16 —
  **+91.3%**. TPOT median **88.5 → 44.6 ms** (**2.0× faster per token**). Prefill 41.91 vs 22.87.
  **83/1000 completed vs 41** in the same 900 s window — the request count itself doubled.
  0 errors, load 380 s.
- **Speedup scales inversely with batch, as speculation theory predicts:** **+91% at conc-1** →
  **+31% at conc-32**. At conc-1 the target forward is pure latency with nothing to amortise it
  against, so every accepted draft token converts directly into wall-clock; at conc-32 the batch
  already keeps the GPU busy and the drafted tokens compete with real ones for the same compute.
- **Acceptance ~57%, consistent with the other MTP runs — and that is the real finding.** Steady-state
  windows ranged 42.8–74.6% (noisier here: at conc-1 each 10 s window holds only ~240 drafted tokens,
  vs ~3000 at conc-32), mean acceptance length **~2.8**, per-position **0.78 / 0.56 / 0.44**. Compare
  ~54% at NVFP4/conc-32 and ~56% at FP8/conc-32: **acceptance is flat across concurrency and across
  target quant**, which is what `notes/BENCHMARKING.md` says it should be (workload-driven, not
  concurrency-driven). What changes with concurrency is whether the speedup *materialises* — and it
  does, dramatically. The ~54–57% band remains well below the 70–85% rule of thumb and below the
  Qwen3.6-27B sibling's 67%; see [`qwen3-8-27b-fp8-vllm-mtp-c32`](qwen3-8-27b-fp8-vllm-mtp-c32) for
  the control that ruled out a precision mismatch.
- **This corrects the apparent MTP regression on the previous generation.** The Qwen3.6-27B conc-1 pair
  records `decode_toks` 16.85 (base) → 9.33 (MTP), which reads as MTP *hurting* at conc-1. That is an
  artifact of the windows those runs used (600 s / 500 prompts and 300 s / 200 prompts, completing only
  22 and 20 requests, so cold-start ramp dominates the aggregate) — its own TPOT of 51.5 ms implies
  ~19 tok/s per stream, i.e. a speedup, not a regression. Measured on a matched 900 s / 1000-prompt
  window here, MTP at conc-1 is unambiguously a large win. **Prefer TPOT over aggregate `decode_toks`
  when reading any conc-1 page.**
- **TTFT cost:** 177.1 → **264.2 ms** (+49%). The same trade as at conc-32 (456 → 857 ms), but much
  cheaper in absolute terms — at conc-1 there is no queueing delay stacked on top of the draft
  overhead. For interactive use the 2× TPOT improvement dominates a 87 ms TTFT penalty.
- **Memory:** 106.5 GB vs 105.4 for the conc-1 base (+1.1, the MTP head plus its KV group), and
  essentially the same as the conc-32 MTP run's 105.4 — the reservation is set by
  `gpu-memory-utilization`, not by concurrency.
