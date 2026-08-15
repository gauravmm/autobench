---
title: Qwen3.8-27B · vLLM · NVFP4 + MTP
model: Qwen/Qwen3.8-27B
company: Alibaba
family: Qwen
params: 27B (dense, hybrid linear-attn)
engine: vLLM
speculative: MTP
quant: NVFP4
quant_rationale: Same unsloth NVFP4 checkpoint as the base config, plus the checkpoint's own MTP head — the quant config puts `re:^mtp.*` in `ignore`, so the draft head stays BF16 while the target MLPs are W4A4. Native multi-token prediction, no separate draft model. vLLM resolves it as `Qwen3_5MTP`.
source_repo: unsloth/Qwen3.8-27B-NVFP4
download_url: https://huggingface.co/unsloth/Qwen3.8-27B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 32
tags: [qwen3.8-27b, Alibaba, Qwen, NVFP4, 16-40B, conc-32]
status: done
prefill_toks: 352.62
decode_toks: 274.74
mem_gb: 105.42
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85) + MTP head
spec_acceptance: ~54% avg draft acceptance (steady-state range 49.5–60%) · mean acceptance length 2.6 (of a possible 4.0) · per-position ~0.75 / 0.51 / 0.36 (num_speculative_tokens=3)
measured_on: 2026-08-15
completed_at: 2026-08-15 10:23 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:677afd5bf3b4bb9881f91e107af7098f8410726b4c05b25cb4a815900b398204
run_command: |
  # NVFP4 base + the in-repo MTP head (Resolved architecture: Qwen3_5MTP) on vLLM nightly-aarch64. conc-32.
  scripts/bench-vllm-serving.sh unsloth/Qwen3.8-27B-NVFP4 65536 32 1000 900 256 \
    --trust-remote-code --dtype bfloat16 \
    --speculative-config '{"method":"mtp","num_speculative_tokens":3}'
  # 1000/1000 prompts, 0 errors, 866.5 s — did NOT hit the 900 s cap (base run did).
  # TTFT median 857.2 ms, TPOT median 108.0 ms, req throughput 1.154/s.
  # SpecDecoding (steady-state): mean acceptance length ~2.6, avg draft acceptance ~54%,
  # per-position ~0.75 / 0.51 / 0.36 (num_speculative_tokens=3).
---

**MTP is worth +31% decode on day one — but its acceptance is notably worse than the Qwen3.6-27B
predecessor's, and that gap is the interesting result here.**

- **Result (conc 32):** prefill **352.6** / decode **274.7** tok/s aggregate vs the
  [NVFP4 base](qwen3-8-27b-nvfp4-vllm-c32)'s 270.6 / 210.0 — **+30.3% prefill, +30.8% decode**.
  **1000/1000, 0 errors, 866.5 s** — the full entry count inside the cap (the base run hit the cap only
  because of its 571 s cold download; here the weights were already cached, 440 s load). TPOT median
  drops 144.1 → **108.0 ms**; TTFT rises 456 → 857 ms (the draft head costs prefill latency per request
  even though aggregate prefill throughput goes up).
- **Acceptance — ~54%, below expectation. Flagged.** Steady-state avg draft acceptance ranged
  **49.5–60%** (typical ~53–55%), mean acceptance length **~2.6** out of a possible 4.0, per-position
  **0.75 / 0.51 / 0.36**. `notes/BENCHMARKING.md`'s rule of thumb for a well-matched MTP head is 70–85%
  (ShareGPT general chat runs at the low end), and the **Qwen3.6-27B NVFP4+MTP sibling measured 67% with
  mean length 3.0** on this exact harness and workload. So this head is ~13 points worse than its direct
  predecessor under identical conditions. Two candidate explanations, neither confirmed:
  1. **Draft/target precision mismatch.** unsloth leaves `re:^mtp.*` unquantized (BF16) while the target
     MLPs are NVFP4 W4A4. A BF16 draft predicting for a W4A4 target diverges more than a matched pair —
     this is the more likely cause, and it is testable by benchmarking MTP on the official
     `Qwen/Qwen3.8-27B-FP8` (uniform-ish FP8 target, smaller gap to a BF16 head).
  2. **Day-one MTP head.** The model is one day old; the head may simply be less trained than 3.6's.
  Worth re-running against a matched-precision checkpoint before drawing a conclusion about the model.
  The **+31% decode still lands** despite the mediocre acceptance, because the hybrid stack makes each
  drafted step cheap.
- **Memory (vLLM log):** weights + non-torch **25.67 GiB** (+0.52 over base — that is the MTP head),
  peak activation **3.92 GiB**, CUDA-graph pool effectively 0 (log reports −0.05 GiB), KV **73.85 GiB**.
  The KV *bytes* barely move but the **token capacity drops 2,128,554 → 1,665,316 (−22%)** — max
  concurrency at 65536 ctx falls **32.5× → 25.4×** — because the MTP layer adds its own KV group. At
  conc-32/65k this is still comfortable; it would matter for a long-context or high-concurrency sweep.
- **Graph capture took 24 s** here vs 7 s for the base (the MTP path captures more shapes), and the
  cold load was 440 s with weights already cached.
- **No DFlash / DDTree alternative exists for this model** — see the
  [base config](qwen3-8-27b-nvfp4-vllm-c32) for the checks. MTP is the only speculative path available
  for Qwen3.8-27B as of 2026-08-15.
