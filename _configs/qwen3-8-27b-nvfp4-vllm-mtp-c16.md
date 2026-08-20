---
title: Qwen3.8-27B · vLLM · NVFP4 + MTP · conc-16
model: Qwen/Qwen3.8-27B
company: Alibaba
family: Qwen
params: 27B (dense, hybrid linear-attn)
engine: vLLM
speculative: MTP
quant: NVFP4
quant_rationale: Same unsloth NVFP4 checkpoint plus its in-repo BF16 MTP head, at conc-16 — the midpoint of the decaying half of the speculative-speedup-vs-batch curve.
source_repo: unsloth/Qwen3.8-27B-NVFP4
download_url: https://huggingface.co/unsloth/Qwen3.8-27B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 16
tags: [qwen3.8-27b, Alibaba, Qwen, NVFP4, 16-40B, conc-16]
status: done
prefill_toks: 245.47
decode_toks: 194.99
mem_gb: 105.69
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85) + MTP head
spec_acceptance: ~57% avg draft acceptance (last-20 samples 51.2–63.8%, median 56.8%) · mean acceptance length ~2.72 (of a possible 4.0) · per-position ~0.76 / 0.55 / 0.41 (num_speculative_tokens=3)
measured_on: 2026-08-21
completed_at: 2026-08-21 02:33 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:677afd5bf3b4bb9881f91e107af7098f8410726b4c05b25cb4a815900b398204
run_command: |
  # conc-16 point with the in-repo MTP head. Same recipe as conc-32 except --max-num-seqs.
  scripts/bench-vllm-serving.sh unsloth/Qwen3.8-27B-NVFP4 65536 16 1000 900 256 \
    --trust-remote-code --dtype bfloat16 \
    --speculative-config '{"method":"mtp","num_speculative_tokens":3}'
  # 744/1000 prompts in the 900 s window (vs 499 for the non-spec baseline), 0 errors. ready after 383 s.
  # TTFT median 616.7 ms, TPOT median 76.8 ms.
---

**+52% decode at conc-16 — still worth it, but the batch is now doing half the work.**

- **Result (conc 16):** decode **194.99** tok/s vs the
  [conc-16 base]({{ site.baseurl }}/configs/qwen3-8-27b-nvfp4-vllm-c16/)'s 128.60 — **+51.6%**. TPOT
  median **118.7 → 76.8 ms** (**1.55× faster per token**). Prefill 245.5 vs 149.0 (**1.65×**).
  **744/1000 completed vs 499** in the same window. 0 errors, load 383 s.
- **Fits the decay curve exactly.** +91% (c1) → +94% (c2) → +83% (c4) → +69% (c8) → **+52% (c16)** →
  +31% (c32). Once past the low-batch plateau the speedup falls roughly linearly in log₂(batch), losing
  ~14 points per doubling. Speculation and batching are two ways to spend the same idle compute; the
  more of it the batch consumes, the less is left for drafted tokens.
- **MTP still beats a batch doubling on latency.** c16+MTP does 195.0 tok/s at **76.8 ms TPOT**;
  the non-speculative c32 does a comparable 210.0 tok/s but at **144.1 ms TPOT**. For the same rough
  throughput, MTP at half the batch gives users **~1.9× better per-token latency** — the clearest
  argument on this sweep for spending memory on a draft head instead of on more concurrent slots.
- **Acceptance ~57%** (last-20 samples 51.2–63.8%, median 56.8%), mean acceptance length **~2.72** of a
  possible 4.0, per-position **0.76 / 0.55 / 0.41**. Six MTP runs on this model now span **~52–58%**
  with no trend in concurrency — acceptance is workload-driven, per `notes/BENCHMARKING.md`.
- **TTFT cost:** 374.1 → **616.7 ms** (+65%), the largest relative hit so far apart from c32's +88%.
  The constant per-request draft overhead is now landing on top of a queue deep enough to amplify it.
- **Memory 105.7 GB**, mid-band for the sweep.
