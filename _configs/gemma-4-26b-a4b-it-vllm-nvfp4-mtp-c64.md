---
title: Gemma 4 26B-A4B · vLLM · NVFP4 + MTP · conc 64
model: google/gemma-4-26B-A4B-it
company: Google
family: Gemma
params: 26B / 4B (MoE)
engine: vLLM
speculative: MTP (Google assistant drafter)
quant: NVFP4
quant_rationale: NVIDIA NVFP4 base (modelopt) + Google's official MTP assistant drafter (google/gemma-4-26B-A4B-it-assistant) via vLLM's native gemma-4 MTP path — the near-free-drafter line of the crossover figure. c64 point of the beyond-c32 ceiling-finding extension.
source_repo: nvidia/Gemma-4-26B-A4B-NVFP4
download_url: https://huggingface.co/nvidia/Gemma-4-26B-A4B-NVFP4
context: 65536
modalities: [text, image]
mm_served: false
concurrency: 64
tags: [gemma-4-26b-a4b, Google, Gemma, NVFP4, 16-40B, conc-64]
status: done
prefill_toks: 1175.76
decode_toks: 1027.53
mem_gb: 110.59
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85) + Gemma4 MTP head
spec_acceptance: mean acceptance length 2.72 (2.69-2.85) · avg draft acceptance 57% (56-62%) · per-position ~0.76/0.55/0.40
measured_on: 2026-07-04
completed_at: 2026-07-04 10:25 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:e414712fdc04f61d98ccc58cb61232a0587a8c024544e9e6cf12f97b19b38172
run_command: |
  VLLM_IMAGE=vllm/vllm-openai:nightly-aarch64 scripts/bench-vllm-serving.sh nvidia/Gemma-4-26B-A4B-NVFP4 65536 64 1000 900 256 \
    --speculative-config '{"method":"mtp","model":"google/gemma-4-26B-A4B-it-assistant","num_speculative_tokens":3}'
  # 1000/1000 prompts (clean full run), 0 errors, 229.2s. ready after 319s. TTFT median 423.7 ms, TPOT median 55.4 ms, req thr 4.363/s.
  # SpecDecoding: mean acceptance length 2.72 (2.69-2.85) · avg draft acceptance 57% (56-62%) · per-position ~0.76/0.55/0.40.
---

**Decode 1027.53 tok/s aggregate at concurrency 64 — the MTP line is still climbing hard past c32.** NVFP4 + Google MTP assistant drafter, first point of the beyond-c32 ceiling-finding sweep (context held at 65536 so it splices onto the c1–c32 curve).

- **Still rising, not saturated:** decode **1027.53 tok/s** vs the c32 point (696.98) = **1.47× per doubling** — barely decelerating from the c16→c32 step (1.60×). At c64 this MTP line is nowhere near a compute plateau; the ceiling is further out.
- **Memory 110.59 GB** against the 121 GB unified limit — the vLLM `--gpu-memory-utilization 0.85` reservation (fixed regardless of `--max-num-seqs`), essentially unchanged from c32 (108.92). Raising the seq cap does not raise the reservation; headroom to the ceiling is ~10 GB.
- **Image (pinned):** `vllm/vllm-openai:nightly-aarch64` @ `sha256:e414712fdc04…` — same single image as the c1–c32 cells. Ready after **319 s**.
- **Workload:** ShareGPT V3, concurrency 64. **1000/1000, 0 errors** in **229.2 s** (clean full run, no time cap). TTFT median 423.7 ms, TPOT median 55.4 ms, req throughput 4.363/s.
- **Spec-decode acceptance:** mean acceptance length 2.72 · avg draft acceptance 57% · per-position ~0.76/0.55/0.40 (num_speculative_tokens=3) — flat vs the c1–c32 points, confirming acceptance is workload-driven not concurrency-driven.
</content>
</invoke>
