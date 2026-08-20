---
title: Qwen3.6-27B · vLLM · NVFP4 · conc 8
model: Qwen/Qwen3.6-27B
company: Alibaba
family: Qwen
params: 27B (dense)
engine: vLLM
quant: NVFP4
quant_rationale: conc-8 base (non-spec) point of the Qwen3.6-27B NVFP4 sweep — matched no-spec baseline for the MTP conc-8 row (EXPERIMENTS.md #4/#14). Unsloth NVFP4, same recipe as the published conc-32 base; only --max-num-seqs differs. Part of the base-vs-MTP speedup-decay curve.
source_repo: unsloth/Qwen3.6-27B-NVFP4
download_url: https://huggingface.co/unsloth/Qwen3.6-27B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 8
tags: [qwen3.6-27b, Alibaba, Qwen, NVFP4, 16-40B, conc-8]
status: done
prefill_toks: 68.25
decode_toks: 67.06
mem_gb: 107.09
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85)
measured_on: 2026-07-01
completed_at: 2026-07-01 22:32 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:68e23ddd982ad5642e21354c2242a3a86d31a3ea83f5937e5c3867942dc6595b
run_command: |
  # conc-8 base (no spec). Same recipe as the published conc-32 base — only --max-num-seqs differs.
  scripts/bench-vllm-serving.sh unsloth/Qwen3.6-27B-NVFP4 65536 8 1000 600 256 \
    --trust-remote-code --dtype bfloat16
---

**conc-8 base (no-spec) point of the Qwen3.6-27B NVFP4 sweep** — matched baseline for the MTP conc-8 row
(EXPERIMENTS.md #4/#14).

- **Result (conc 8):** prefill 68.25 / decode **67.06** tok/s aggregate; **0 errors**; peak mem 107.1 GB.
- **Scaling starts to bend by conc-8** (9.33 → 18.11 → 35.54 → 67.06 at c1/2/4/8 ≈ ×1.94/×1.96/×1.89) — still
  strong but no longer perfectly linear as the dense 27B begins to fill the compute.
- **MTP speedup at conc-8:** MTP [`-mtp-c8`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-mtp-c8/) 109.05 vs this base 67.06 =
  **+62.6%** — the dense model keeps a large MTP win at moderate batch (vs the 35B-A3B MoE's ~+20% at c8),
  because a dense target has less spare compute to lose to draft overhead. MTP accepts ~71% / accept-len ~3.1.
- Sweep siblings (base): [`-c1`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-c1/) · [`-c2`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-c2/) ·
  [`-c4`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-c4/) · [`-c16`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-c16/) · [`c32` (main)]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm/).
