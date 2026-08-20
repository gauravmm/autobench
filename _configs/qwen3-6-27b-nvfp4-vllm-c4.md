---
title: Qwen3.6-27B · vLLM · NVFP4 · conc 4
model: Qwen/Qwen3.6-27B
company: Alibaba
family: Qwen
params: 27B (dense)
engine: vLLM
quant: NVFP4
quant_rationale: conc-4 base (non-spec) point of the Qwen3.6-27B NVFP4 sweep — matched no-spec baseline for the MTP conc-4 row (EXPERIMENTS.md #4/#14). Unsloth NVFP4, same recipe as the published conc-32 base; only --max-num-seqs differs. Part of the base-vs-MTP speedup-decay curve.
source_repo: unsloth/Qwen3.6-27B-NVFP4
download_url: https://huggingface.co/unsloth/Qwen3.6-27B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 4
tags: [qwen3.6-27b, Alibaba, Qwen, NVFP4, 16-40B, conc-4]
status: done
prefill_toks: 56.89
decode_toks: 35.54
mem_gb: 106.39
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85)
measured_on: 2026-07-01
completed_at: 2026-07-01 22:16 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:68e23ddd982ad5642e21354c2242a3a86d31a3ea83f5937e5c3867942dc6595b
run_command: |
  # conc-4 base (no spec). Same recipe as the published conc-32 base — only --max-num-seqs differs.
  scripts/bench-vllm-serving.sh unsloth/Qwen3.6-27B-NVFP4 65536 4 1000 600 256 \
    --trust-remote-code --dtype bfloat16
---

**conc-4 base (no-spec) point of the Qwen3.6-27B NVFP4 sweep** — matched baseline for the MTP conc-4 row
(EXPERIMENTS.md #4/#14).

- **Result (conc 4):** prefill 56.89 / decode **35.54** tok/s aggregate; **0 errors**; peak mem 106.4 GB.
- **Still near-linear** (9.33 → 18.11 → 35.54 at c1/2/4 ≈ ×1.94/×1.96) — the dense 27B stays bandwidth-bound
  through conc-4, so the batch buys almost proportional aggregate decode. MTP-vs-base delta on the
  [`-mtp-c4`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-mtp-c4/) page.
- Sweep siblings (base): [`-c1`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-c1/) · [`-c2`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-c2/) ·
  [`-c8`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-c8/) · [`-c16`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-c16/) · [`c32` (main)]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm/).
