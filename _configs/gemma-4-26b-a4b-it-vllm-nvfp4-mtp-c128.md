---
title: Gemma 4 26B-A4B · vLLM · NVFP4 + MTP · conc 128
model: google/gemma-4-26B-A4B-it
company: Google
family: Gemma
params: 26B / 4B (MoE)
engine: vLLM
speculative: MTP (Google assistant drafter)
quant: NVFP4
quant_rationale: NVIDIA NVFP4 base (modelopt) + Google's official MTP assistant drafter (google/gemma-4-26B-A4B-it-assistant) via vLLM's native gemma-4 MTP path — the near-free-drafter line of the crossover figure. c128 point of the beyond-c32 ceiling-finding extension.
source_repo: nvidia/Gemma-4-26B-A4B-NVFP4
download_url: https://huggingface.co/nvidia/Gemma-4-26B-A4B-NVFP4
context: 65536
modalities: [text, image]
mm_served: false
concurrency: 128
tags: [gemma-4-26b-a4b, Google, Gemma, NVFP4, 16-40B, conc-128]
status: done
prefill_toks: 1577.85
decode_toks: 1380.09
mem_gb: 114.40
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85) + Gemma4 MTP head + larger-batch runtime buffers
spec_acceptance: mean acceptance length 2.70 (2.51-2.79) · avg draft acceptance 57% (50-60%) · per-position ~0.76/0.55/0.40
measured_on: 2026-07-04
completed_at: 2026-07-04 10:32 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:e414712fdc04f61d98ccc58cb61232a0587a8c024544e9e6cf12f97b19b38172
run_command: |
  VLLM_IMAGE=vllm/vllm-openai:nightly-aarch64 scripts/bench-vllm-serving.sh nvidia/Gemma-4-26B-A4B-NVFP4 65536 128 1000 900 256 \
    --speculative-config '{"method":"mtp","model":"google/gemma-4-26B-A4B-it-assistant","num_speculative_tokens":3}'
  # 1000/1000 prompts (clean full run), 0 errors, 170.8s. ready after 309s. TTFT median 631.6 ms, TPOT median 80.8 ms, req thr 5.855/s.
  # SpecDecoding: mean acceptance length 2.70 (2.51-2.79) · avg draft acceptance 57% (50-60%) · per-position ~0.76/0.55/0.40.
---

**Decode 1380.09 tok/s aggregate at concurrency 128 — still climbing, but memory is now the binding constraint.** NVFP4 + Google MTP assistant drafter, second point of the beyond-c32 ceiling-finding sweep (context held at 65536).

- **Compute still has headroom, memory does not:** decode **1380.09 tok/s** vs c64 (1027.53) = **1.34× per doubling** — decelerating (1.60× → 1.47× → 1.34×) but still well above the ~1.1× plateau threshold. The line has NOT topped out on compute.
- **Memory 114.40 GB** vs c64's 110.59 — the headline is now climbing ~4 GB per doubling (larger-batch CUDA graphs + activation/scheduler buffers on top of the fixed 0.85 KV reservation). **Only ~6.6 GB of headroom left to the 121 GB unified ceiling** → c256 is the memory-ceiling test.
- **Image (pinned):** `vllm/vllm-openai:nightly-aarch64` @ `sha256:e414712fdc04…` — same single image as the c1–c64 cells. Ready after **309 s**.
- **Workload:** ShareGPT V3, concurrency 128. **1000/1000, 0 errors** in **170.8 s** (clean full run, no time cap). TTFT median 631.6 ms, TPOT median 80.8 ms, req throughput 5.855/s.
- **Spec-decode acceptance:** mean acceptance length 2.70 · avg draft acceptance 57% · per-position ~0.76/0.55/0.40 — still flat vs the lower-concurrency points (a few windows dipped to ~50% under peak batch pressure but recovered).
</content>
</invoke>
