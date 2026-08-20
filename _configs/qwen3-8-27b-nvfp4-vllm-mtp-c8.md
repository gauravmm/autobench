---
title: Qwen3.8-27B · vLLM · NVFP4 + MTP · conc-8
model: Qwen/Qwen3.8-27B
company: Alibaba
family: Qwen
params: 27B (dense, hybrid linear-attn)
engine: vLLM
speculative: MTP
quant: NVFP4
quant_rationale: Same unsloth NVFP4 checkpoint plus its in-repo BF16 MTP head, at conc-8 — the middle point that completes the speculative-speedup-vs-batch curve (c1 / c8 / c32).
source_repo: unsloth/Qwen3.8-27B-NVFP4
download_url: https://huggingface.co/unsloth/Qwen3.8-27B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 8
tags: [qwen3.8-27b, Alibaba, Qwen, NVFP4, 16-40B, conc-8]
status: done
prefill_toks: 149.68
decode_toks: 126.68
mem_gb: 105.44
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85) + MTP head
spec_acceptance: ~52% avg draft acceptance (steady-state range 50.1–56.5%) · mean acceptance length ~2.6 (of a possible 4.0) · per-position ~0.73 / 0.50 / 0.35 (num_speculative_tokens=3)
measured_on: 2026-08-15
completed_at: 2026-08-15 12:39 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:677afd5bf3b4bb9881f91e107af7098f8410726b4c05b25cb4a815900b398204
run_command: |
  # conc-8 point with the in-repo MTP head. Same recipe as conc-32 except --max-num-seqs.
  scripts/bench-vllm-serving.sh unsloth/Qwen3.8-27B-NVFP4 65536 8 1000 900 256 \
    --trust-remote-code --dtype bfloat16 \
    --speculative-config '{"method":"mtp","num_speculative_tokens":3}'
  # 487/1000 prompts in the 900 s window (vs 288 for the non-spec baseline), 0 errors. ready after 374 s.
  # TTFT median 476.1 ms, TPOT median 59.3 ms.
---

**+69% decode at conc-8 — the middle of a clean, monotonic speedup-vs-batch curve.**

- **Result (conc 8):** decode **126.68** tok/s vs the [conc-8 base](qwen3-8-27b-nvfp4-vllm-c8)'s 75.04 —
  **+68.8%**. TPOT median **101.5 → 59.3 ms** (**1.71× faster per token**). Prefill 149.7 vs 114.9.
  **487/1000 completed vs 288** in the same window. 0 errors, load 374 s.
- **The completed speculative curve** (NVFP4 base vs NVFP4+MTP, identical 1000/900 s cap, ctx 65536):

  | conc | base decode | +MTP decode | speedup | base TPOT | +MTP TPOT |
  |------|-------------|-------------|---------|-----------|-----------|
  | 1    | 11.16       | 21.35       | **+91%** | 88.5 ms  | 44.6 ms |
  | 8    | 75.04       | 126.68      | **+69%** | 101.5 ms | 59.3 ms |
  | 32   | 209.97      | 274.74      | **+31%** | 144.1 ms | 108.0 ms |

  Monotonic decline exactly as speculation theory predicts: the emptier the batch, the more of the
  target forward the drafted tokens get for free. **MTP is worth enabling at every concurrency
  measured** — it never goes negative on this model — but the case is overwhelming at low batch and
  merely good at high batch.
- **Acceptance ~52%, flat again.** Steady-state 50.1–56.5%, mean acceptance length **~2.6**,
  per-position **0.73 / 0.50 / 0.35**. Across the whole sweep acceptance sits in a **~52–57% band
  regardless of concurrency (1/8/32) or target quant (NVFP4/FP8)** — five independent MTP runs. That is
  textbook behaviour per `notes/BENCHMARKING.md` (acceptance is workload-driven), and it makes the
  ~13-point shortfall against the Qwen3.6-27B sibling's 67% a solid, reproducible property of this
  model's head rather than a measurement artifact. The precision-mismatch explanation was tested and
  ruled out in [`qwen3-8-27b-fp8-vllm-mtp-c32`](qwen3-8-27b-fp8-vllm-mtp-c32).
- **TTFT cost:** 345.3 → **476.1 ms** (+38%), the same shape as c1 (+49%) and c32 (+88%). The draft
  overhead per request is roughly constant; what grows with batch is the queueing on top of it.
- **Memory 105.4 GB**, indistinguishable from the other points in the sweep.
