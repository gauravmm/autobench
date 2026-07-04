---
title: Gemma 4 26B-A4B · vLLM · NVFP4 + EAGLE3 · conc 128
model: google/gemma-4-26B-A4B-it
company: Google
family: Gemma
params: 26B / 4B (MoE)
engine: vLLM
speculative: EAGLE3
quant: NVFP4
quant_rationale: NVIDIA NVFP4 base (modelopt) + RedHatAI's official EAGLE3 speculator (RedHatAI/gemma-4-26B-A4B-it-speculator.eagle3) — the EAGLE3 line of the crossover figure. c128 point of the beyond-c32 ceiling-finding extension.
source_repo: nvidia/Gemma-4-26B-A4B-NVFP4
download_url: https://huggingface.co/nvidia/Gemma-4-26B-A4B-NVFP4
context: 65536
modalities: [text, image]
mm_served: false
concurrency: 128
tags: [gemma-4-26b-a4b, Google, Gemma, NVFP4, 16-40B, conc-128]
status: done
prefill_toks: 1384.59
decode_toks: 1210.22
mem_gb: 111.88
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85) + EAGLE3 head + draft buffers; ~6.6 GB free at peak
spec_acceptance: mean acceptance length 2.11 (2.11-2.12) · avg draft acceptance 37% (37%) · per-position ~0.59/0.34/0.19
measured_on: 2026-07-04
completed_at: 2026-07-04 13:20 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:e414712fdc04f61d98ccc58cb61232a0587a8c024544e9e6cf12f97b19b38172
run_command: |
  # Run under scripts/mem-watchdog.sh (floor 3.5 GB) — GB10 unified memory; see notes/BENCHMARKING.md.
  VLLM_IMAGE=vllm/vllm-openai:nightly-aarch64 scripts/bench-vllm-serving.sh nvidia/Gemma-4-26B-A4B-NVFP4 65536 128 1000 900 256 \
    --speculative-config '{"model":"RedHatAI/gemma-4-26B-A4B-it-speculator.eagle3","method":"eagle3","num_speculative_tokens":3}'
  # 1000/1000 prompts (clean full run), 0 errors, 194.6s. ready after 287s. TTFT median 562.6 ms, TPOT median 94.0 ms, req thr 5.138/s. Watchdog no trip (6.6 GB free).
  # SpecDecoding: mean acceptance length 2.11 · avg draft acceptance 37% · per-position ~0.59/0.34/0.19.
---

**Decode 1210.22 tok/s aggregate at concurrency 128 — still climbing.** NVFP4 + RedHatAI EAGLE3 speculator, second point of the beyond-c32 ceiling-finding sweep (context held at 65536).

- **Compute still has headroom:** decode **1210.22 tok/s** vs c64 (888.98) = **1.36× per doubling** — matching base's deceleration curve. EAGLE3 tracks between base and MTP throughout (base 995 · **EAGLE3 1210** · MTP 1380 at c128).
- **Memory tightening (like MTP, unlike base):** peak **111.88 GB delta = ~6.6 GB free** — the EAGLE3 draft head + per-seq draft buffers climb with concurrency (base sat at ~9.4 GB here). This is why c256 is the danger point for the spec lines but not for base. Watchdog (floor 3.5 GB) armed, did not trip at c128.
- **Acceptance flat ~37%:** mean acceptance length **2.11**, per-position **0.59/0.34/0.19** — consistent with c1–c64; the weak-but-stable EAGLE3 draft.
- **Image (pinned):** `vllm/vllm-openai:nightly-aarch64` @ `sha256:e414712fdc04…`. Ready after 287 s.
- **Workload:** ShareGPT V3, concurrency 128. **1000/1000, 0 errors** in **194.6 s** (no time cap). TTFT median 562.6 ms, TPOT median 94.0 ms, req throughput 5.138/s.
</content>
</invoke>
