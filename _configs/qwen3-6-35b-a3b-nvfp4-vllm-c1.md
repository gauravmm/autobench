---
title: Qwen3.6-35B-A3B · vLLM · NVFP4 · conc 1
model: Qwen/Qwen3.6-35B-A3B
company: Alibaba
family: Qwen
params: 35B / 3B (MoE)
engine: vLLM
quant: NVFP4
quant_rationale: conc-1 base (non-spec) point of the Qwen3.6-35B-A3B NVFP4 sweep — the matched no-spec baseline for the MTP/DFlash conc-1 rows (EXPERIMENTS.md #4/#14). NVIDIA official ModelOpt NVFP4, same recipe as the published conc-32 base (marlin dequant MoE, --reasoning-parser qwen3, no --speculative-config); only --max-num-seqs differs. Gives the base-vs-MTP speedup at single stream.
source_repo: nvidia/Qwen3.6-35B-A3B-NVFP4
download_url: https://huggingface.co/nvidia/Qwen3.6-35B-A3B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 1
tags: [qwen3.6-35b-a3b, Alibaba, Qwen, NVFP4, 16-40B, Spark recipe, conc-1]
status: done
prefill_toks: 93.25
decode_toks: 74.74
mem_gb: 108.53
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85)
measured_on: 2026-07-01
completed_at: 2026-07-01 13:50 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:68e23ddd982ad5642e21354c2242a3a86d31a3ea83f5937e5c3867942dc6595b
run_command: |
  # conc-1 base (no spec). Same recipe as the published conc-32 base — only --max-num-seqs differs.
  scripts/bench-vllm-serving.sh nvidia/Qwen3.6-35B-A3B-NVFP4 65536 1 400 600 256 \
    --quantization modelopt --trust-remote-code --reasoning-parser qwen3
  # 176/400 prompts (hit 600 s cap), 0 errors. ready after 362 s.
---

**conc-1 base (no-spec) point of the Qwen3.6-35B-A3B NVFP4 sweep** — the matched single-stream baseline the
post needed to quote MTP/DFlash speedups at conc-1 (EXPERIMENTS.md #4/#14). Same NVIDIA ModelOpt NVFP4 recipe
as the published conc-32 base; only `--max-num-seqs` changes.

- **Result (conc 1):** prefill 93.25 / decode **74.74** tok/s aggregate; 176/400 prompts (hit the 600 s cap),
  **0 errors**; peak mem 108.5 GB.
- **MTP speedup at conc-1:** against a **matched 600 s-cap MTP recheck (99.04 tok/s)** this base gives
  **+32.5%** (the published MTP c1 of 93.9 was a 300 s-cap run, ~5% under-measured; see
  [`-mtp-c1`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-mtp-c1/)). **DFlash at conc-1** (101.9) = **+36.4%** over base.
- **Consequence for the money chart:** DFlash's single-stream *edge over MTP* is only **~+2.9%** (101.9 vs the
  matched MTP 99.04), not the +8.5% quoted against the short-cap MTP — and even that is ctx-confounded (DFlash
  ran ctx 40960 vs MTP 65536). So DFlash barely leads MTP at conc-1 and loses from conc-2 on. TPOT 0.0 =
  `qwen3` reasoning-parser client artifact — decode tok/s is real.
- Sweep siblings: [`-c2`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-c2/) · [`-c4`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-c4/) ·
  [`-c8`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-c8/) · [`-c16`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-c16/) ·
  [`c32` (main)]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm/). MTP counterpart: [`-mtp-c1`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-mtp-c1/).
