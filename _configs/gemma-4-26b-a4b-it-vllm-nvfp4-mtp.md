---
title: Gemma 4 26B-A4B · vLLM · NVFP4 + MTP
model: google/gemma-4-26B-A4B-it
company: Google
family: Gemma
params: 26B / 4B (MoE)
engine: vLLM
speculative: MTP (Google assistant drafter)
quant: NVFP4
quant_rationale: NVIDIA NVFP4 base (modelopt) + Google's official MTP assistant drafter (google/gemma-4-26B-A4B-it-assistant) via vLLM's native gemma-4 MTP path — the near-free-drafter line of the crossover figure.
source_repo: nvidia/Gemma-4-26B-A4B-NVFP4
download_url: https://huggingface.co/nvidia/Gemma-4-26B-A4B-NVFP4
context: 65536
modalities: [text, image]
mm_served: false
concurrency: 32
tags: [gemma-4-26b-a4b, Google, Gemma, NVFP4, 16-40B, conc-32]
status: done
prefill_toks: 796.2
decode_toks: 696.98
mem_gb: 108.92
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85) + Gemma4 MTP head
spec_acceptance: mean acceptance length 2.66 (2.26-2.86) · avg draft acceptance 56% (42-62%) · per-position ~0.74/0.54/0.38
measured_on: 2026-07-03
completed_at: 2026-07-03 16:32 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:e414712fdc04f61d98ccc58cb61232a0587a8c024544e9e6cf12f97b19b38172
run_command: |
  VLLM_IMAGE=vllm/vllm-openai:nightly-aarch64 scripts/bench-vllm-serving.sh nvidia/Gemma-4-26B-A4B-NVFP4 65536 32 1000 900 256 \
    --speculative-config '{"method":"mtp","model":"google/gemma-4-26B-A4B-it-assistant","num_speculative_tokens":3}'
  # 1000/1000 prompts (clean full run), 0 errors, 338.5s. ready after 288s. TTFT median 333.3 ms, TPOT median 42.1 ms, req thr 2.954/s.
  # SpecDecoding: mean acceptance length 2.66 (2.26-2.86) · avg draft acceptance 56% (42-62%) · per-position ~0.74/0.54/0.38.
---

**Decode 696.98 tok/s aggregate at concurrency 32.** NVFP4 + Google MTP assistant drafter, conc 32 — the near-free-drafter line of the crossover figure.

- **Image (pinned):** `vllm/vllm-openai:nightly-aarch64` @ `sha256:e414712fdc04…` — the SINGLE image for all 24 cells of this figure. Ready after **288 s**.
- **Workload:** ShareGPT V3, concurrency 32. **1000/1000, 0 errors** in **338.5 s** (clean full run).
- **Throughput:** decode **696.98 tok/s** aggregate, prefill 796.2 tok/s. TTFT median 333.3 ms, TPOT median 42.1 ms, req throughput 2.954/s.
- **Spec-decode acceptance:** mean acceptance length 2.66 (2.26-2.86) · avg draft acceptance 56% (42-62%) · per-position ~0.74/0.54/0.38 (num_speculative_tokens=3).
- **Memory: 108.92 GB** = vLLM `--gpu-memory-utilization 0.85` reservation, not the model footprint.
