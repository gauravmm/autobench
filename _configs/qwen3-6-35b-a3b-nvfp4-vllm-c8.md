---
title: Qwen3.6-35B-A3B · vLLM · NVFP4 · conc 8
model: Qwen/Qwen3.6-35B-A3B
company: Alibaba
family: Qwen
params: 35B / 3B (MoE)
engine: vLLM
quant: NVFP4
quant_rationale: conc-8 base (non-spec) point of the Qwen3.6-35B-A3B NVFP4 sweep — matched no-spec baseline for the MTP/DFlash conc-8 rows (EXPERIMENTS.md #4/#14). NVIDIA official ModelOpt NVFP4, same recipe as the published conc-32 base; only --max-num-seqs differs. Part of the base-vs-MTP speedup-decay curve.
source_repo: nvidia/Qwen3.6-35B-A3B-NVFP4
download_url: https://huggingface.co/nvidia/Qwen3.6-35B-A3B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 8
tags: [qwen3.6-35b-a3b, Alibaba, Qwen, NVFP4, 16-40B, Spark recipe, conc-8]
status: done
prefill_toks: 264.33
decode_toks: 241.82
mem_gb: 107.94
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85)
measured_on: 2026-07-01
completed_at: 2026-07-01 14:39 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:68e23ddd982ad5642e21354c2242a3a86d31a3ea83f5937e5c3867942dc6595b
run_command: |
  # conc-8 base (no spec). Same recipe as the published conc-32 base — only --max-num-seqs differs.
  scripts/bench-vllm-serving.sh nvidia/Qwen3.6-35B-A3B-NVFP4 65536 8 1000 600 256 \
    --quantization modelopt --trust-remote-code --reasoning-parser qwen3
  # 574/1000 prompts (hit 600 s cap), 0 errors. ready after 385 s.
---

**conc-8 base (no-spec) point of the Qwen3.6-35B-A3B NVFP4 sweep** — matched baseline for the MTP/DFlash
conc-8 rows (EXPERIMENTS.md #4/#14), so the post can quote the MTP/DFlash speedups at conc-8 against a real
base instead of only conc-32. Same NVIDIA ModelOpt NVFP4 recipe as the published conc-32 base.

- **Result (conc 8):** prefill 264.33 / decode **241.82** tok/s aggregate; 574/1000 prompts (hit the 600 s
  cap), **0 errors**; peak mem 107.9 GB.
- **MTP speedup at conc-8:** the original June MTP c8 (289.1, a 300 s-cap run) gave +19.5%, but a **matched
  600 s-cap recheck (2026-07-01) measured MTP c8 = 304.0**, i.e. **+25.7%** over this base — the +19.5% "dip"
  was a short-cap sampling artifact. With that correction the MTP-vs-base ratio is a **robust ~+25–30%**
  across the sweep — +32.5% (c1) / +42.4% (c2) / +33.8% (c4) / **+25.7% (c8)** / +30.3% (c16) / +25.7% (c32)
  — essentially flat with a modest **low-batch (c2–c4) bump**, NOT a monotone decay (full discussion on the
  [`-c16` page]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-c16/)). **DFlash at conc-8** (269.9) = +11.6% over base, positive
  but below MTP.
- TPOT 0.0 = `qwen3` reasoning-parser client artifact — decode tok/s is the reported metric.
- Sweep siblings: [`-c1`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-c1/) · [`-c2`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-c2/) ·
  [`-c4`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-c4/) · [`-c16`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-c16/) ·
  [`c32` (main)]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm/). MTP counterpart: [`-mtp-c8`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-mtp-c8/).
