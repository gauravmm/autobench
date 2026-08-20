---
title: Qwen3.6-27B AEON Uncensored · vLLM-ultimate (custom) · NVFP4 + DFlash · conc 8
model: AEON-7/Qwen3.6-27B-AEON-Ultimate-Uncensored
company: Alibaba
family: Qwen
params: 27B (dense) + DFlash external drafter
engine: vLLM (aeon-vllm-ultimate custom container)
speculative: DFlash (z-lab drafter, num_speculative_tokens 12)
quant: NVFP4 (XS mixed-precision)
quant_rationale: Same AEON NVFP4-XS model served via the card's "DGX Spark production" recipe — custom container ghcr.io/aeon-7/aeon-vllm-ultimate:latest (vLLM 0.23.0) + external z-lab/Qwen3.6-27B-DFlash drafter, DFlash num_speculative_tokens=12. User's explicit request. SAFETY — untrusted image; NO creds, models READ-ONLY.
source_repo: AEON-7/Qwen3.6-27B-AEON-Ultimate-Uncensored-Multimodal-NVFP4-MTP-XS
download_url: https://huggingface.co/AEON-7/Qwen3.6-27B-AEON-Ultimate-Uncensored-Multimodal-NVFP4-MTP-XS
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 8
tags: [qwen3.6-27b-aeon-uncensored, Alibaba, Qwen, NVFP4, 16-40B, conc-8]
status: done
prefill_toks: 124.32
decode_toks: 127.14
mem_gb: 106.17
mem_source: system MemAvailable delta (10s sampling) — custom vLLM static KV reservation (util 0.85)
spec_acceptance: 19-28% avg draft acceptance · mean acceptance length ~3.3-4.3 · per-position decay across 12 draft tokens
measured_on: 2026-06-24
completed_at: 2026-06-24 01:11 +0800
engine_image: ghcr.io/aeon-7/aeon-vllm-ultimate:latest@sha256:be9e05a11da6e72607ab6f3e960993b253b673af0727005122a3266129a518e3
run_command: |
  # UNTRUSTED third-party container — NO creds, full cached repo root + drafter mounted READ-ONLY.
  scripts/bench-aeon-ultimate-serving.sh 65536 8 1000 900 256
  # 456 prompts completed before the 900 s cap (0 errors). TTFT median 14875.8 ms.
---

**Custom AEON-ultimate container + DFlash, conc 8.** Part of the 1/8/32 sweep on the card's "DGX Spark
production" recipe (custom vLLM 0.23.0 + external z-lab DFlash drafter). Mid-point between single-stream and the c=32 throughput point. See the
[conc-1 page]({{ site.baseurl }}/configs/qwen3-6-27b-aeon-uncensored-vllm-ultimate-dflash-c1/) for the safety posture (untrusted
image, no creds, models read-only) and drafter details.

- **Result (conc 8):** prefill **124.32** tok/s, decode **127.14** tok/s aggregate; **456 prompts**
  completed before the **900 s** cap, with **0 errors**. Median **TTFT 14875.8 ms**. So batching helps
  aggregate throughput relative to `conc=1`, but the path still misses the benchmark target badly.
- **Acceptance:** DFlash again showed a front-loaded 12-token draft profile with **mean acceptance
  length ~3.3-4.3** and **avg draft acceptance ~19-28%**. That is consistent with the `conc=1` page:
  some speculative work is paying off, but not nearly enough to justify the observed latency and cap
  behavior.
- **Takeaway:** the custom AEON container is not rescuing throughput under moderate batch either. It
  remains a stable but slow serving path on this workload.
