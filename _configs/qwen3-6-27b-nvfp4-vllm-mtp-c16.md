---
title: Qwen3.6-27B · vLLM · NVFP4 + MTP · conc 16
model: Qwen/Qwen3.6-27B
company: Alibaba
family: Qwen
params: 27B (dense)
engine: vLLM
speculative: MTP (num_speculative_tokens=3)
quant: NVFP4
quant_rationale: conc-16 MTP point of the Qwen3.6-27B NVFP4 sweep — the base+MTP speedup-decay curve (EXPERIMENTS.md #14). Unsloth NVFP4 with the repo's native MTP module; same recipe as the -mtp-c8 row, only --max-num-seqs differs. Pairs with the matched base -c16.
source_repo: unsloth/Qwen3.6-27B-NVFP4
download_url: https://huggingface.co/unsloth/Qwen3.6-27B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 16
tags: [qwen3.6-27b, Alibaba, Qwen, NVFP4, 16-40B, conc-16]
status: done
prefill_toks: 184.72
decode_toks: 192.23
mem_gb: 108.51
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85) + MTP head
spec_acceptance: mean acceptance length ~3.08 (2.98–3.22) · avg draft acceptance ~69% (66–74%) · per-position 0.855/0.68/0.55 (num_speculative_tokens=3)
measured_on: 2026-07-01
completed_at: 2026-07-01 23:54 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:68e23ddd982ad5642e21354c2242a3a86d31a3ea83f5937e5c3867942dc6595b
run_command: |
  # conc-16 MTP. Same recipe as -mtp-c8 — only --max-num-seqs differs.
  scripts/bench-vllm-serving.sh unsloth/Qwen3.6-27B-NVFP4 65536 16 1000 600 256 \
    --trust-remote-code --dtype bfloat16 \
    --speculative-config '{"method":"mtp","num_speculative_tokens":3}'
---

**conc-16 MTP point of the Qwen3.6-27B NVFP4 sweep** — paired with the matched base [`-c16`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-c16/)
for the base-vs-MTP speedup-decay curve (EXPERIMENTS.md #14), the last point before the published c32 row.

- **Result (conc 16):** prefill 184.72 / decode **192.23** tok/s aggregate; **0 errors**; peak mem 108.5 GB.
- **MTP speedup at conc-16: +64.9%** (192.23 vs base 116.57) — and note **MTP@c16 (192.2) already edges out
  base@c32 (187.7)**: the draft buys more than a 2× batch increase does. The full decay curve is now closed:
  **+80.6 (c1) → +97.0 (c2) → +90.7 (c4) → +62.6 (c8) → +64.9 (c16) → +46.0 (c32)%**. The dense 27B keeps a
  big MTP win far later than the 35B-A3B MoE (~+25–30%): it drops from the ~2× low-batch peak into a broad
  ~+60–65% plateau across c8–c16, then finally erodes toward +46% at c32 as the batch saturates compute.
- **Acceptance ~69%, accept-len ~3.08-of-3** (per-position 0.855/0.68/0.55) — flat across the whole sweep
  (c2 ~68% / c4 ~70% / c8 ~71% / c16 ~69%), confirming MTP acceptance is workload-driven, not concurrency-
  sensitive. The speedup decay is therefore pure batch-economics (shrinking spare compute), not draft quality.
- Sweep: base [`-c16`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-c16/) · MTP [`-c1`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-mtp-c1/) ·
  [`-c2`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-mtp-c2/) · [`-c4`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-mtp-c4/) ·
  [`-c8`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-mtp-c8/) · [`c32`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-mtp/).
