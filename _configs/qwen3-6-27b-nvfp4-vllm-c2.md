---
title: Qwen3.6-27B · vLLM · NVFP4 · conc 2
model: Qwen/Qwen3.6-27B
company: Alibaba
family: Qwen
params: 27B (dense)
engine: vLLM
quant: NVFP4
quant_rationale: conc-2 base (non-spec) point of the Qwen3.6-27B NVFP4 sweep — matched no-spec baseline for the MTP conc-2 row (EXPERIMENTS.md #4/#14). Unsloth NVFP4, same recipe as the published conc-32 base; only --max-num-seqs differs. Part of the base-vs-MTP speedup-decay curve.
source_repo: unsloth/Qwen3.6-27B-NVFP4
download_url: https://huggingface.co/unsloth/Qwen3.6-27B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 2
tags: [qwen3.6-27b, Alibaba, Qwen, NVFP4, 16-40B, conc-2]
status: done
prefill_toks: 30.58
decode_toks: 18.11
mem_gb: 105.92
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85)
measured_on: 2026-07-01
completed_at: 2026-07-01 22:00 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:68e23ddd982ad5642e21354c2242a3a86d31a3ea83f5937e5c3867942dc6595b
run_command: |
  # conc-2 base (no spec). Same recipe as the published conc-32 base — only --max-num-seqs differs.
  scripts/bench-vllm-serving.sh unsloth/Qwen3.6-27B-NVFP4 65536 2 1000 600 256 \
    --trust-remote-code --dtype bfloat16
---

**conc-2 base (no-spec) point of the Qwen3.6-27B NVFP4 sweep** — matched baseline for the MTP conc-2 row
(EXPERIMENTS.md #4/#14).

- **Result (conc 2):** prefill 30.58 / decode **18.11** tok/s aggregate; **0 errors**; peak mem 105.9 GB.
- **Clean ~2× scaling from conc-1** (9.33 → 18.11) — the dense 27B is still bandwidth-bound at conc-2, so
  doubling the batch nearly doubles aggregate decode. MTP-vs-base delta is on the [`-mtp-c2`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-mtp-c2/) page.
- Sweep siblings (base): [`-c1`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-c1/) · [`-c4`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-c4/) ·
  [`-c8`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-c8/) · [`-c16`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-c16/) · [`c32` (main)]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm/).
