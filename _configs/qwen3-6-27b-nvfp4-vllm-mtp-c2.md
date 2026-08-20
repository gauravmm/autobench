---
title: Qwen3.6-27B · vLLM · NVFP4 + MTP · conc 2
model: Qwen/Qwen3.6-27B
company: Alibaba
family: Qwen
params: 27B (dense)
engine: vLLM
speculative: MTP (num_speculative_tokens=3)
quant: NVFP4
quant_rationale: conc-2 MTP point of the Qwen3.6-27B NVFP4 sweep — the base+MTP speedup-decay curve (EXPERIMENTS.md #14). Unsloth NVFP4 with the repo's native MTP module; same recipe as the -mtp-c8 row, only --max-num-seqs differs. Pairs with the matched base -c2.
source_repo: unsloth/Qwen3.6-27B-NVFP4
download_url: https://huggingface.co/unsloth/Qwen3.6-27B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 2
tags: [qwen3.6-27b, Alibaba, Qwen, NVFP4, 16-40B, conc-2]
status: done
prefill_toks: 56.13
decode_toks: 35.68
mem_gb: 109.42
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85) + MTP head
spec_acceptance: mean acceptance length ~3.0 (2.92–3.25) · avg draft acceptance ~68% (64–75%) · per-position 0.85/0.69/0.55 (num_speculative_tokens=3)
measured_on: 2026-07-01
completed_at: 2026-07-01 23:14 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:68e23ddd982ad5642e21354c2242a3a86d31a3ea83f5937e5c3867942dc6595b
run_command: |
  # conc-2 MTP. Same recipe as -mtp-c8 — only --max-num-seqs differs.
  scripts/bench-vllm-serving.sh unsloth/Qwen3.6-27B-NVFP4 65536 2 1000 600 256 \
    --trust-remote-code --dtype bfloat16 \
    --speculative-config '{"method":"mtp","num_speculative_tokens":3}'
---

**conc-2 MTP point of the Qwen3.6-27B NVFP4 sweep** — paired with the matched base [`-c2`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-c2/)
for the base-vs-MTP speedup-decay curve (EXPERIMENTS.md #14).

- **Result (conc 2):** prefill 56.13 / decode **35.68** tok/s aggregate; **0 errors**; peak mem 109.4 GB.
- **MTP speedup at conc-2: +97.0%** (35.68 vs base 18.11) — nearly a **2× single-stream-ish win** on the dense
  27B. The dense MTP advantage is largest at low batch: **+80.6% (c1) → +97.0% (c2) → +62.6% (c8)**, far above
  the 35B-A3B MoE's ~+25–40%, because a dense target has essentially no spare compute for the batch to reclaim.
- **Acceptance ~68%, accept-len ~3.0-of-3** — the MTP draft is highly efficient (per-position 0.85/0.69/0.55),
  matching the -c8 row's ~71%. Acceptance is workload-driven and batch-stable here (unlike the gpt-oss EAGLE3
  low-batch pathology).
- Sweep: base [`-c2`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-c2/) · MTP [`-c1`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-mtp-c1/) ·
  [`-c4`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-mtp-c4/) · [`-c8`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-mtp-c8/) · [`c32`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-mtp/).
