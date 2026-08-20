---
title: Qwen3.6-27B AEON Uncensored · vLLM-ultimate (custom) · NVFP4 + DFlash · conc 32
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
concurrency: 32
tags: [qwen3.6-27b-aeon-uncensored, Alibaba, Qwen, NVFP4, 16-40B, conc-32]
status: done
prefill_toks: 180.99
decode_toks: 184.21
mem_gb: 111.34
mem_source: system MemAvailable delta (10s sampling) — custom vLLM static KV reservation (util 0.85)
spec_acceptance: 16-28% avg draft acceptance · mean acceptance length ~2.9-4.4 · per-position decay across 12 draft tokens
measured_on: 2026-06-24
completed_at: 2026-06-24 01:35 +0800
engine_image: ghcr.io/aeon-7/aeon-vllm-ultimate:latest@sha256:be9e05a11da6e72607ab6f3e960993b253b673af0727005122a3266129a518e3
run_command: |
  # UNTRUSTED third-party container — NO creds, full cached repo root + drafter mounted READ-ONLY.
  scripts/bench-aeon-ultimate-serving.sh 65536 32 1000 900 256
  # 668 prompts completed before the 900 s cap (0 errors). TTFT median 41115.7 ms.
---

**Custom AEON-ultimate container + DFlash, conc 32.** Part of the 1/8/32 sweep on the card's "DGX Spark
production" recipe (custom vLLM 0.23.0 + external z-lab DFlash drafter). Direct A/B vs the native-MTP-on-stock-vLLM result (**303 tok/s @ conc-32**) — does the custom container + DFlash beat stock + MTP at the same batch? The card claims ~340 tok/s @ c=64 / ~45% DFlash accept. See the
[conc-1 page]({{ site.baseurl }}/configs/qwen3-6-27b-aeon-uncensored-vllm-ultimate-dflash-c1/) for the safety posture (untrusted
image, no creds, models read-only) and drafter details.

- **Result (conc 32):** prefill **180.99** tok/s, decode **184.21** tok/s aggregate; **668 prompts**
  completed before the **900 s** cap, with **0 errors**. Median **TTFT 41115.7 ms**. This is the best
  aggregate throughput of the custom AEON sweep, but it still falls well short of both the benchmark
  completion target and the card's own production claims.
- **Acceptance:** DFlash remained in roughly the same regime as the lower-concurrency points:
  **mean acceptance length ~2.9-4.4** and **avg draft acceptance ~16-28%**. The first draft positions
  accept reasonably, later positions decay quickly. So the custom drafter is doing work, but it is not
  achieving the kind of acceptance profile that would justify a 12-token speculative budget.
- **Bottom line vs the stock path:** this custom container + external DFlash run does **not** beat the
  already-recorded native-MTP-on-stock-vLLM path at the same concurrency. It stays cap-bound and
  under-delivers on throughput even at the most favorable point of its own 1/8/32 sweep.
