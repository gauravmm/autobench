---
title: Qwen3.6-27B · vLLM · NVFP4 · conc 16
model: Qwen/Qwen3.6-27B
company: Alibaba
family: Qwen
params: 27B (dense)
engine: vLLM
quant: NVFP4
quant_rationale: conc-16 base (non-spec) point of the Qwen3.6-27B NVFP4 sweep — matched no-spec baseline for the MTP conc-16 row (EXPERIMENTS.md #4/#14), completing the base curve at c1/2/4/8/16/32. Unsloth NVFP4, same recipe as the published conc-32 base; only --max-num-seqs differs.
source_repo: unsloth/Qwen3.6-27B-NVFP4
download_url: https://huggingface.co/unsloth/Qwen3.6-27B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 16
tags: [qwen3.6-27b, Alibaba, Qwen, NVFP4, 16-40B, conc-16]
status: done
prefill_toks: 147.97
decode_toks: 116.57
mem_gb: 107.72
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85)
measured_on: 2026-07-01
completed_at: 2026-07-01 22:58 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:68e23ddd982ad5642e21354c2242a3a86d31a3ea83f5937e5c3867942dc6595b
run_command: |
  # conc-16 base (no spec). Same recipe as the published conc-32 base — only --max-num-seqs differs.
  scripts/bench-vllm-serving.sh unsloth/Qwen3.6-27B-NVFP4 65536 16 1000 600 256 \
    --trust-remote-code --dtype bfloat16
---

**conc-16 base (no-spec) point of the Qwen3.6-27B NVFP4 sweep** — completes the base curve at c1/2/4/8/16/32
(matched baseline for the MTP conc-16 row, EXPERIMENTS.md #4/#14).

- **Result (conc 16):** prefill 147.97 / decode **116.57** tok/s aggregate; **0 errors**; peak mem 107.7 GB.
- **The full base decode curve:** 9.33 → 18.11 → 35.54 → 67.06 → 116.57 → 187.74 tok/s at c1/2/4/8/16/32.
  Scaling factor per doubling falls from ~1.94 (c1→2) to **1.74** (c8→16) to **1.61** (c16→32) — the dense 27B
  transitions from bandwidth-bound (near-linear) toward compute-bound (diminishing returns) as the batch fills.
- **MTP-vs-base delta** on the [`-mtp-c16`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-mtp-c16/) page — this is where spec-decode's
  edge is expected to compress, since a filling dense batch leaves less spare compute for the draft.
- Sweep siblings (base): [`-c1`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-c1/) · [`-c2`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-c2/) ·
  [`-c4`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-c4/) · [`-c8`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-c8/) · [`c32` (main)]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm/).
