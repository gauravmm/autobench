---
title: Qwen3.8-27B · vLLM · NVFP4 + MTP · conc-2
model: Qwen/Qwen3.8-27B
company: Alibaba
family: Qwen
params: 27B (dense, hybrid linear-attn)
engine: vLLM
speculative: MTP
quant: NVFP4
quant_rationale: Same unsloth NVFP4 checkpoint plus its in-repo BF16 MTP head, at conc-2 — the near-idle end of the speculative-speedup-vs-batch curve, where drafted tokens ride along most cheaply.
source_repo: unsloth/Qwen3.8-27B-NVFP4
download_url: https://huggingface.co/unsloth/Qwen3.8-27B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 2
tags: [qwen3.8-27b, Alibaba, Qwen, NVFP4, 16-40B, conc-2]
status: done
prefill_toks: 49.08
decode_toks: 38.95
mem_gb: 106.55
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85) + MTP head
spec_acceptance: ~58% avg draft acceptance (last-20 samples 48.0–73.6%, median 58.4%) · mean acceptance length ~2.8 (of a possible 4.0) · per-position ~0.78 / 0.57 / 0.41 (num_speculative_tokens=3)
measured_on: 2026-08-21
completed_at: 2026-08-21 01:06 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:677afd5bf3b4bb9881f91e107af7098f8410726b4c05b25cb4a815900b398204
run_command: |
  # conc-2 point with the in-repo MTP head. Same recipe as conc-32 except --max-num-seqs.
  scripts/bench-vllm-serving.sh unsloth/Qwen3.8-27B-NVFP4 65536 2 1000 900 256 \
    --trust-remote-code --dtype bfloat16 \
    --speculative-config '{"method":"mtp","num_speculative_tokens":3}'
  # 151/1000 prompts in the 900 s window (vs 80 for the non-spec baseline), 0 errors. ready after 342 s.
  # TTFT median 408.2 ms, TPOT median 48.9 ms.
---

**+94% decode at conc-2 — the peak of the MTP speedup curve.**

- **Result (conc 2):** decode **38.95** tok/s vs the
  [conc-2 base]({{ site.baseurl }}/configs/qwen3-8-27b-nvfp4-vllm-c2/)'s 20.11 — **+93.7%**. TPOT median
  **96.3 → 48.9 ms** (**1.97× faster per token**). Prefill 49.1 vs 40.4. **151/1000 completed vs 80** in
  the same window. 0 errors, load 342 s.
- **c2 is where MTP pays best, not c1.** The speedup runs +91% (c1) → **+94% (c2)** → +69% (c8) → +31%
  (c32). The c1 and c2 points are within each other's noise — c1 completed only 41 requests — so the
  honest reading is a **flat ~90–95% plateau below c4 that then decays with batch**, not a strict
  monotonic decline from c1. Below c4 the target forward is memory-bound with idle compute, so the
  drafted tokens are nearly free; past that the batch fills the tensor cores and speculation starts
  competing for them.
- **Acceptance ~58%, the high end of the model's band.** Last-20 samples 48.0–73.6% (median 58.4%),
  mean acceptance length **~2.8** of a possible 4.0, per-position **0.78 / 0.57 / 0.41**. That sits
  above the ~52% seen at c8/c32 — consistent with acceptance being workload-driven
  (`notes/BENCHMARKING.md`): the 900 s window at c2 admits only 151 requests, so a handful of
  easy-to-draft conversations move the average more than they do at c32. It does **not** overturn the
  cross-sweep conclusion that this head's acceptance sits ~13 points below the Qwen3.6-27B sibling's
  67%; see [`qwen3-8-27b-fp8-vllm-mtp-c32`]({{ site.baseurl }}/configs/qwen3-8-27b-fp8-vllm-mtp-c32/),
  where the precision-mismatch explanation was tested and ruled out.
- **TTFT cost:** 301.1 → **408.2 ms** (+36%), the same roughly-constant per-request draft overhead seen
  at c1 (+49%), c8 (+38%) and c32 (+88%).
- **Memory 106.6 GB**, within the sweep's 103–107 GB band.
