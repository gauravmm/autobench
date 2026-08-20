---
title: Qwen3.6-35B-A3B · vLLM · NVFP4 · conc 4
model: Qwen/Qwen3.6-35B-A3B
company: Alibaba
family: Qwen
params: 35B / 3B (MoE)
engine: vLLM
quant: NVFP4
quant_rationale: conc-4 base (non-spec) point of the Qwen3.6-35B-A3B NVFP4 sweep — matched no-spec baseline for the MTP/DFlash conc-4 rows (EXPERIMENTS.md #4/#14). NVIDIA official ModelOpt NVFP4, same recipe as the published conc-32 base; only --max-num-seqs differs. Part of the base-vs-MTP speedup-decay curve.
source_repo: nvidia/Qwen3.6-35B-A3B-NVFP4
download_url: https://huggingface.co/nvidia/Qwen3.6-35B-A3B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 4
tags: [qwen3.6-35b-a3b, Alibaba, Qwen, NVFP4, 16-40B, Spark recipe, conc-4]
status: done
prefill_toks: 181.46
decode_toks: 173.76
mem_gb: 107.73
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85)
measured_on: 2026-07-01
completed_at: 2026-07-01 14:24 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:68e23ddd982ad5642e21354c2242a3a86d31a3ea83f5937e5c3867942dc6595b
run_command: |
  # conc-4 base (no spec). Same recipe as the published conc-32 base — only --max-num-seqs differs.
  scripts/bench-vllm-serving.sh nvidia/Qwen3.6-35B-A3B-NVFP4 65536 4 1000 600 256 \
    --quantization modelopt --trust-remote-code --reasoning-parser qwen3
  # 411/1000 prompts (hit 600 s cap), 0 errors. ready after 385 s.
---

**conc-4 base (no-spec) point of the Qwen3.6-35B-A3B NVFP4 sweep** — matched baseline for the MTP/DFlash
conc-4 rows (EXPERIMENTS.md #4/#14). Same NVIDIA ModelOpt NVFP4 recipe as the published conc-32 base; only
`--max-num-seqs` changes.

- **Result (conc 4):** prefill 181.46 / decode **173.76** tok/s aggregate; 411/1000 prompts (hit the 600 s
  cap), **0 errors**; peak mem 107.7 GB.
- **MTP speedup at conc-4:** MTP 232.4 vs this base 173.76 = **+33.8%**. Across the full sweep the MTP-vs-base
  ratio is non-monotone (+25.6/+42.4/+33.8/+19.5/+30.3/+25.7% at c1/2/4/8/16/32), which turns out to be an
  MTP-measurement-window artifact rather than a real curve shape — see the [`-c16`
  page]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-c16/). Net: MTP wins a robust ~+20–42% (centered ~+30%), and the
  single-stream +25.6% is not the maximum.
- TPOT 0.0 = `qwen3` reasoning-parser client artifact — decode tok/s is the reported metric.
- Sweep siblings: [`-c1`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-c1/) · [`-c2`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-c2/) ·
  [`-c8`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-c8/) · [`-c16`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-c16/) ·
  [`c32` (main)]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm/). MTP counterpart: [`-mtp-c4`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-mtp-c4/).
