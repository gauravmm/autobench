---
title: Qwen3.8-27B · vLLM · FP8 + MTP
model: Qwen/Qwen3.8-27B
company: Alibaba
family: Qwen
params: 27B (dense, hybrid linear-attn)
engine: vLLM
speculative: MTP
quant: FP8
quant_rationale: Official Alibaba FP8 plus the in-repo MTP head. Run specifically as the matched-precision control for the low MTP acceptance seen on the NVFP4+MTP config — the FP8 target sits much closer to the BF16 draft head than an NVFP4 W4A4 target does, so if the draft/target precision-mismatch hypothesis were right, acceptance should have risen here.
source_repo: Qwen/Qwen3.8-27B-FP8
download_url: https://huggingface.co/Qwen/Qwen3.8-27B-FP8
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 32
tags: [qwen3.8-27b, Alibaba, Qwen, FP8, 16-40B, conc-32]
status: done
prefill_toks: 264.55
decode_toks: 203.01
mem_gb: 107.57
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85) + MTP head
spec_acceptance: ~56% avg draft acceptance (steady-state range 47.5–63.1%) · mean acceptance length ~2.7 (of a possible 4.0) · per-position ~0.76 / 0.54 / 0.39 (num_speculative_tokens=3)
measured_on: 2026-08-15
completed_at: 2026-08-15 11:13 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:677afd5bf3b4bb9881f91e107af7098f8410726b4c05b25cb4a815900b398204
run_command: |
  # Official FP8 + the in-repo MTP head (Resolved architecture: Qwen3_5MTP) on vLLM nightly-aarch64. conc-32.
  scripts/bench-vllm-serving.sh Qwen/Qwen3.8-27B-FP8 65536 32 1000 900 256 \
    --trust-remote-code --dtype bfloat16 \
    --speculative-config '{"method":"mtp","num_speculative_tokens":3}'
  # 793/1000 prompts, 0 errors, hit the 900 s cap (925.8 s; cold load 433 s with weights cached).
  # TTFT median 1073.5 ms, TPOT median 137.1 ms.
  # SpecDecoding (steady-state): mean acceptance length ~2.7, avg draft acceptance ~56%,
  # per-position ~0.76 / 0.54 / 0.39 (num_speculative_tokens=3).
---

**The control run — and it refutes the precision-mismatch hypothesis. Acceptance is ~56% here vs ~54%
on NVFP4: statistically the same. The Qwen3.8 MTP head is simply weaker on ShareGPT than Qwen3.6's,
independent of target quant.**

- **Why this run exists.** [`qwen3-8-27b-nvfp4-vllm-mtp-c32`]({{ site.baseurl }}/configs/qwen3-8-27b-nvfp4-vllm-mtp-c32/) measured
  ~54% draft acceptance against the 70–85% rule of thumb and the Qwen3.6-27B sibling's 67%. The leading
  explanation was a **draft/target precision mismatch**: unsloth leaves `re:^mtp.*` in BF16 while the
  target MLPs are NVFP4 W4A4. This config swaps the target to official FP8 — a far smaller gap to a
  BF16 draft — holding the harness, workload, engine image, context and concurrency fixed.
- **Result of the test: no lift.** Acceptance **~56%** (steady-state 47.5–63.1%), mean acceptance length
  **~2.7**, per-position **0.76 / 0.54 / 0.39** — within run-to-run noise of NVFP4's ~54% / 2.6 /
  0.75 / 0.51 / 0.36. **The hypothesis does not hold.** Remaining explanation: the day-one Qwen3.8-27B
  MTP head just predicts general chat worse than Qwen3.6's did (~13 points worse). Recorded as a
  model property, not a serving misconfiguration. Nothing to fix on the run side.
- **Throughput (conc 32):** prefill **264.6** / decode **203.0** tok/s; **793/1000, 0 errors**, hit the
  900 s cap. Versus [FP8 base]({{ site.baseurl }}/configs/qwen3-8-27b-fp8-vllm-c32/)'s 196.3 / 143.9 that is **+34.8% prefill,
  +41.1% decode**.
- **MTP pays off MORE on the slower quant — +41% on FP8 vs +31% on NVFP4.** Same head, same acceptance,
  different base: FP8 decode is the more compute-bound path, so replacing decode steps with drafted
  ones recovers more of the deficit. It does not close the gap, though — FP8+MTP (203.0) still lands
  **below plain NVFP4 with no speculation at all (210.0)**. On GB10 the quant choice beats the
  speculation choice; NVFP4+MTP (274.7) remains the fastest configuration by a wide margin.
- **Memory (vLLM log):** weights + non-torch **32.31 GiB** (+0.13 for the MTP head), peak activation
  **2.55 GiB**, CUDA-graph pool **0.10 GiB**, KV **68.57 GiB** = **892,505 tokens** → max concurrency
  **13.62×** at 65536 ctx (FP8 base was 15.97×). Lowest KV headroom of the four configs; still no
  preemptions on ShareGPT's short prompts, but this is the config that would break first on long
  context.
- **TTFT is the cost:** median **1073.5 ms** here vs **601.2 ms** for the FP8 base — the same pattern as
  the NVFP4 pair (456 → 857 ms). TPOT moves the other way, 188.9 → **137.1 ms**. Drafting adds
  per-request first-token latency even where it raises aggregate throughput; a latency-sensitive
  deployment should weigh that against the +41%.
