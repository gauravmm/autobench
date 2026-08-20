---
title: Qwen3.8-27B · vLLM · NVFP4 + MTP · conc-64
model: Qwen/Qwen3.8-27B
company: Alibaba
family: Qwen
params: 27B (dense, hybrid linear-attn)
engine: vLLM
speculative: MTP
quant: NVFP4
quant_rationale: Same unsloth NVFP4 checkpoint plus its in-repo BF16 MTP head, at conc-64 — the tail of the speculative-speedup-vs-batch curve, where the batch has absorbed most of the idle compute speculation feeds on.
source_repo: unsloth/Qwen3.8-27B-NVFP4
download_url: https://huggingface.co/unsloth/Qwen3.8-27B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 64
tags: [qwen3.8-27b, Alibaba, Qwen, NVFP4, 16-40B, conc-64]
status: done
prefill_toks: 413.94
decode_toks: 324.08
mem_gb: 107.25
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85) + MTP head
spec_acceptance: ~54% avg draft acceptance (last-20 samples 48.2–59.5%, median 53.3%) · mean acceptance length ~2.62 (of a possible 4.0) · per-position ~0.74 / 0.51 / 0.36 (num_speculative_tokens=3)
measured_on: 2026-08-21
completed_at: 2026-08-21 03:13 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:677afd5bf3b4bb9881f91e107af7098f8410726b4c05b25cb4a815900b398204
run_command: |
  # conc-64 point with the in-repo MTP head. Same recipe as conc-32 except --max-num-seqs.
  scripts/bench-vllm-serving.sh unsloth/Qwen3.8-27B-NVFP4 65536 64 1000 900 256 \
    --trust-remote-code --dtype bfloat16 \
    --speculative-config '{"method":"mtp","num_speculative_tokens":3}'
  # 1000/1000 prompts in 738.2 s — DRAINED the dataset, did NOT hit the 900 s cap. 0 errors.
  # ready after 390 s. TTFT median 1445.0 ms, TPOT median 182.0 ms.
---

**+14% decode at conc-64 — MTP is still positive, but this is where it stops being worth the TTFT.**

- **Result (conc 64):** decode **324.08** tok/s vs the
  [conc-64 base]({{ site.baseurl }}/configs/qwen3-8-27b-nvfp4-vllm-c64/)'s 283.72 — **+14.2%**. TPOT
  median **209.1 → 182.0 ms** (1.15×). Prefill 413.9 vs 363.8. 0 errors, load 390 s.
- **This pair is the cleanest comparison on the sweep — identical work, different wall clock.** Both
  runs drained all 1000 prompts (same 305,551 prompt tokens, ~239k completion tokens either way), so
  neither hit the time cap. Base took **840.0 s**, MTP **738.2 s** — a **1.14× end-to-end speedup**,
  matching the +14.2% decode figure exactly. No cap artifact, no sampling difference.
- **The decay curve, completed:** +91% (c1) → +94% (c2) → +83% (c4) → +69% (c8) → +52% (c16) →
  +31% (c32) → **+14% (c64)**. Losing ~15 points per doubling past c4, heading for zero somewhere around
  **c128–c256**. MTP never goes negative on this model in the measured range, but the return shrinks to
  noise.
- **TTFT is the real cost at this batch: 658.1 → 1445.0 ms (+120%).** Every earlier point paid a roughly
  constant ~36–65% TTFT premium; at c64 the draft work sits on top of a 64-deep queue and more than
  doubles time-to-first-token. **Trading +120% TTFT for +14% throughput is a bad deal for anything
  interactive** — at c64 and above, turn MTP off unless the workload is pure offline batch.
- **Acceptance ~54%** (last-20 samples 48.2–59.5%, median 53.3%), mean acceptance length **~2.62**,
  per-position **0.74 / 0.51 / 0.36**. Seven MTP runs on this model now span **~52–58%** with no trend
  in concurrency — the shortfall against the Qwen3.6-27B sibling's 67% is a property of this head, not
  of batch size or target quant (ruled out in
  [`qwen3-8-27b-fp8-vllm-mtp-c32`]({{ site.baseurl }}/configs/qwen3-8-27b-fp8-vllm-mtp-c32/)).
- **Memory 107.3 GB**, the top of the sweep's 103–107 GB band.
