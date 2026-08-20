---
title: Qwen3.6-27B · vLLM · NVFP4 + MTP · conc 4
model: Qwen/Qwen3.6-27B
company: Alibaba
family: Qwen
params: 27B (dense)
engine: vLLM
speculative: MTP (num_speculative_tokens=3)
quant: NVFP4
quant_rationale: conc-4 MTP point of the Qwen3.6-27B NVFP4 sweep — the base+MTP speedup-decay curve (EXPERIMENTS.md #14). Unsloth NVFP4 with the repo's native MTP module; same recipe as the -mtp-c8 row, only --max-num-seqs differs. Pairs with the matched base -c4.
source_repo: unsloth/Qwen3.6-27B-NVFP4
download_url: https://huggingface.co/unsloth/Qwen3.6-27B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 4
tags: [qwen3.6-27b, Alibaba, Qwen, NVFP4, 16-40B, conc-4]
status: done
prefill_toks: 68.39
decode_toks: 67.76
mem_gb: 108.06
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85) + MTP head
spec_acceptance: mean acceptance length ~3.1 (2.82–3.39) · avg draft acceptance ~70% (61–80%) · per-position 0.86/0.70/0.55 (num_speculative_tokens=3)
measured_on: 2026-07-01
completed_at: 2026-07-01 23:35 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:68e23ddd982ad5642e21354c2242a3a86d31a3ea83f5937e5c3867942dc6595b
run_command: |
  # conc-4 MTP. Same recipe as -mtp-c8 — only --max-num-seqs differs.
  scripts/bench-vllm-serving.sh unsloth/Qwen3.6-27B-NVFP4 65536 4 1000 600 256 \
    --trust-remote-code --dtype bfloat16 \
    --speculative-config '{"method":"mtp","num_speculative_tokens":3}'
---

**conc-4 MTP point of the Qwen3.6-27B NVFP4 sweep** — paired with the matched base [`-c4`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-c4/)
for the base-vs-MTP speedup-decay curve (EXPERIMENTS.md #14).

- **Result (conc 4):** prefill 68.39 / decode **67.76** tok/s aggregate; **0 errors**; peak mem 108.1 GB.
- **MTP speedup at conc-4: +90.7%** (67.76 vs base 35.54) — the dense 27B holds a near-2× MTP win right up
  through conc-4. The decay is now traced end to end: **+80.6% (c1) → +97.0% (c2) → +90.7% (c4) → +62.6% (c8)**
  — the win stays huge while the base is still bandwidth-bound (c1–c4) and only starts eroding once the batch
  begins filling the compute at c8, far above the 35B-A3B MoE's ~+20–40% band.
- **Acceptance ~70%, accept-len ~3.1-of-3** (per-position 0.86/0.70/0.55) — batch-stable vs the -c2 (~68%) and
  -c8 (~71%) rows; MTP acceptance here is workload-driven, not concurrency-sensitive.
- Sweep: base [`-c4`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-c4/) · MTP [`-c1`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-mtp-c1/) ·
  [`-c2`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-mtp-c2/) · [`-c8`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-mtp-c8/) ·
  [`-c16`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-mtp-c16/) · [`c32`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-mtp/).
