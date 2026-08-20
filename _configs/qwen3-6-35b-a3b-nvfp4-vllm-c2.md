---
title: Qwen3.6-35B-A3B · vLLM · NVFP4 · conc 2
model: Qwen/Qwen3.6-35B-A3B
company: Alibaba
family: Qwen
params: 35B / 3B (MoE)
engine: vLLM
quant: NVFP4
quant_rationale: conc-2 base (non-spec) point of the Qwen3.6-35B-A3B NVFP4 sweep — matched no-spec baseline for the MTP/DFlash conc-2 rows (EXPERIMENTS.md #4/#14). NVIDIA official ModelOpt NVFP4, same recipe as the published conc-32 base; only --max-num-seqs differs. Part of the base-vs-MTP speedup-decay curve.
source_repo: nvidia/Qwen3.6-35B-A3B-NVFP4
download_url: https://huggingface.co/nvidia/Qwen3.6-35B-A3B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 2
tags: [qwen3.6-35b-a3b, Alibaba, Qwen, NVFP4, 16-40B, Spark recipe, conc-2]
status: done
prefill_toks: 147.36
decode_toks: 113.19
mem_gb: 107.80
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85)
measured_on: 2026-07-01
completed_at: 2026-07-01 14:07 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:68e23ddd982ad5642e21354c2242a3a86d31a3ea83f5937e5c3867942dc6595b
run_command: |
  # conc-2 base (no spec). Same recipe as the published conc-32 base — only --max-num-seqs differs.
  scripts/bench-vllm-serving.sh nvidia/Qwen3.6-35B-A3B-NVFP4 65536 2 500 600 256 \
    --quantization modelopt --trust-remote-code --reasoning-parser qwen3
  # 267/500 prompts (hit 600 s cap), 0 errors. ready after 404 s.
---

**conc-2 base (no-spec) point of the Qwen3.6-35B-A3B NVFP4 sweep** — matched baseline for the MTP/DFlash
conc-2 rows (EXPERIMENTS.md #4/#14). Same NVIDIA ModelOpt NVFP4 recipe as the published conc-32 base; only
`--max-num-seqs` changes.

- **Result (conc 2):** prefill 147.36 / decode **113.19** tok/s aggregate; 267/500 prompts (hit the 600 s
  cap), **0 errors**; peak mem 107.8 GB.
- **MTP speedup at conc-2:** MTP 161.2 vs this base 113.19 = **+42.4%** — *larger* than the conc-1 speedup
  (+25.6%). The base-vs-MTP win is **not monotone-decaying** from conc-1; it rises into low-batch before
  decaying at high concurrency (see the c4/c8/c16 siblings for the full curve). Worth flagging against the
  post's "MTP win shrinks as the batch fills" framing — the shrink is real at the *high* end, but there's a
  low-batch *peak* first.
- TPOT 0.0 = `qwen3` reasoning-parser client artifact — decode tok/s is the reported metric.
- Sweep siblings: [`-c1`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-c1/) · [`-c4`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-c4/) ·
  [`-c8`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-c8/) · [`-c16`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-c16/) ·
  [`c32` (main)]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm/). MTP counterpart: [`-mtp-c2`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-mtp-c2/).
