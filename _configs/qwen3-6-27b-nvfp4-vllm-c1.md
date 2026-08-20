---
title: Qwen3.6-27B · vLLM · NVFP4 · conc 1
model: Qwen/Qwen3.6-27B
company: Alibaba
family: Qwen
params: 27B (dense)
engine: vLLM
quant: NVFP4
quant_rationale: conc-1 base (non-spec) point of the Qwen3.6-27B NVFP4 sweep — matched no-spec baseline for the MTP conc-1 row (EXPERIMENTS.md #4/#14). Unsloth NVFP4 (W4A4), same recipe as the published conc-32 base; only --max-num-seqs differs. Anchors the base-vs-MTP speedup-decay curve at single-stream.
source_repo: unsloth/Qwen3.6-27B-NVFP4
download_url: https://huggingface.co/unsloth/Qwen3.6-27B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 1
tags: [qwen3.6-27b, Alibaba, Qwen, NVFP4, 16-40B, conc-1]
status: done
prefill_toks: 1.81
decode_toks: 9.33
mem_gb: 108.48
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85)
measured_on: 2026-07-01
completed_at: 2026-07-01 21:44 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:68e23ddd982ad5642e21354c2242a3a86d31a3ea83f5937e5c3867942dc6595b
run_command: |
  # conc-1 base (no spec). Same recipe as the published conc-32 base — only --max-num-seqs differs.
  scripts/bench-vllm-serving.sh unsloth/Qwen3.6-27B-NVFP4 65536 1 500 600 256 \
    --trust-remote-code --dtype bfloat16
  # 22/500 prompts (hit 600 s cap; dense 27B is slow single-stream), 0 errors. ready after 396 s.
---

**conc-1 base (no-spec) point of the Qwen3.6-27B NVFP4 sweep** — matched baseline for the MTP conc-1 row
(EXPERIMENTS.md #4/#14). Same Unsloth NVFP4 recipe as the published conc-32 base; only `--max-num-seqs` changes.

- **Result (conc 1):** prefill 1.81 / decode **9.33** tok/s; 22/500 prompts (hit the 600 s cap), **0 errors**;
  peak mem 108.5 GB.
- **Dense, so slow single-stream — the point of the curve.** At conc-1 this **dense 27B** decodes 9.33 tok/s,
  ~8× slower than the **MoE** 35B-A3B NVFP4's 74.7 (which activates only ~3B/token) — the expected dense-vs-MoE
  gap when every token pays the full 27B. This is why MTP matters more here.
- **MTP speedup at conc-1:** MTP 16.85 vs this base 9.33 = **+80.6%** — the tree-free MTP draft nearly doubles
  single-stream decode on the dense model (vs the MoE's more modest +25.6%), because the dense target has the
  spare-nothing single-stream that spec-decode helps most.
- TPOT/TTFT are the usual conc-1 single-stream figures; decode tok/s is the reported metric.
- Sweep siblings (base): [`-c2`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-c2/) · [`-c4`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-c4/) ·
  [`-c8`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-c8/) · [`-c16`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-c16/) · [`c32` (main)]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm/).
  MTP counterpart: [`-mtp-c1`]({{ site.baseurl }}/configs/qwen3-6-27b-nvfp4-vllm-mtp-c1/).
