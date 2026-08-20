---
title: Qwen3.8-27B · vLLM · NVFP4 + MTP · conc-4
model: Qwen/Qwen3.8-27B
company: Alibaba
family: Qwen
params: 27B (dense, hybrid linear-attn)
engine: vLLM
speculative: MTP
quant: NVFP4
quant_rationale: Same unsloth NVFP4 checkpoint plus its in-repo BF16 MTP head, at conc-4 — the knee where the speculative speedup starts coming off its low-batch plateau.
source_repo: unsloth/Qwen3.8-27B-NVFP4
download_url: https://huggingface.co/unsloth/Qwen3.8-27B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 4
tags: [qwen3.8-27b, Alibaba, Qwen, NVFP4, 16-40B, conc-4]
status: done
prefill_toks: 110.41
decode_toks: 70.74
mem_gb: 104.52
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85) + MTP head
spec_acceptance: ~55% avg draft acceptance (last-20 samples 46.8–64.3%, median 53.2%) · mean acceptance length ~2.64 (of a possible 4.0) · per-position ~0.76 / 0.52 / 0.37 (num_speculative_tokens=3)
measured_on: 2026-08-21
completed_at: 2026-08-21 01:49 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:677afd5bf3b4bb9881f91e107af7098f8410726b4c05b25cb4a815900b398204
run_command: |
  # conc-4 point with the in-repo MTP head. Same recipe as conc-32 except --max-num-seqs.
  scripts/bench-vllm-serving.sh unsloth/Qwen3.8-27B-NVFP4 65536 4 1000 900 256 \
    --trust-remote-code --dtype bfloat16 \
    --speculative-config '{"method":"mtp","num_speculative_tokens":3}'
  # 269/1000 prompts in the 900 s window (vs 151 for the non-spec baseline), 0 errors. ready after 363 s.
  # TTFT median 435.8 ms, TPOT median 53.6 ms.
---

**+83% decode at conc-4 — the knee where the low-batch plateau starts to break.**

- **Result (conc 4):** decode **70.74** tok/s vs the
  [conc-4 base]({{ site.baseurl }}/configs/qwen3-8-27b-nvfp4-vllm-c4/)'s 38.62 — **+83.2%**. TPOT median
  **99.7 → 53.6 ms** (**1.86× faster per token**). Prefill 110.4 vs 48.4 — a **2.3× prefill gain**, the
  largest on the curve. **269/1000 completed vs 151** in the same window. 0 errors, load 363 s.
- **The knee is between c4 and c8.** Speedups run +91% (c1) → +94% (c2) → **+83% (c4)** → +69% (c8) →
  +31% (c32). c1/c2 sit on a flat ~90–95% plateau, c4 is the first clearly lower point, and the drop
  steepens after that. Serving at **c4 or below buys near-double throughput from MTP**; past c8 the
  batch itself is doing the work speculation used to do.
- **Acceptance ~55%**, back in the model's usual band (last-20 samples 46.8–64.3%, median 53.2%),
  mean acceptance length **~2.64** of a possible 4.0, per-position **0.76 / 0.52 / 0.37**. The c2 run's
  ~58% now looks like small-sample drift rather than a real low-batch effect: acceptance is
  workload-driven, not batch-driven, exactly as `notes/BENCHMARKING.md` predicts.
- **TTFT cost:** 314.5 → **435.8 ms** (+39%) — the same near-constant per-request draft overhead as
  c1 (+49%), c2 (+36%) and c8 (+38%).
- **Memory 104.5 GB**, mid-band for the sweep.
