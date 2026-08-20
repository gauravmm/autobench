---
title: Qwen3.6-35B-A3B · vLLM · NVFP4 + MTP · conc 4
model: Qwen/Qwen3.6-35B-A3B
company: Alibaba
family: Qwen
params: 35B / 3B (MoE)
engine: vLLM
speculative: MTP
quant: NVFP4
quant_rationale: conc-4 fine-grained point of the Qwen3.6-35B-A3B NVFP4 + native-MTP sweep — same stack as conc-1/8/32 (nvidia ModelOpt NVFP4 base on marlin + in-repo MTP head on triton). With conc-2 it pins the 1→8 crossover region for the money chart (EXPERIMENTS.md #13/#14). Acceptance should hold ~constant vs the other conc points (workload-driven).
source_repo: nvidia/Qwen3.6-35B-A3B-NVFP4
download_url: https://huggingface.co/nvidia/Qwen3.6-35B-A3B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 4
tags: [qwen3.6-35b-a3b, Alibaba, Qwen, NVFP4, 16-40B, Spark recipe, conc-4]
status: done
prefill_toks: 218.82
decode_toks: 232.43
mem_gb: 109.13
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV (util 0.85) + MTP head
spec_acceptance: mean acceptance length ~3.0 (range 2.99–3.17) · avg draft acceptance ~66–69% · per-position 0.84/0.66/0.52 (3 spec tokens)
measured_on: 2026-07-01
completed_at: 2026-07-01 12:37 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:68e23ddd982ad5642e21354c2242a3a86d31a3ea83f5937e5c3867942dc6595b
run_command: |
  # conc-4 fine-grained point. Same NVIDIA DGX Spark MTP recipe as conc-1/8/32 — only --max-num-seqs differs.
  scripts/bench-vllm-serving.sh nvidia/Qwen3.6-35B-A3B-NVFP4 65536 4 1000 600 256 \
    --quantization modelopt --trust-remote-code --reasoning-parser qwen3 --moe-backend marlin \
    --speculative-config '{"method":"mtp","num_speculative_tokens":3,"moe_backend":"triton"}'
  # 548/1000 prompts (hit 600 s time cap), 0 errors. ready after 379 s.
---

**conc-4 point of the Qwen3.6-35B-A3B NVFP4 + MTP sweep** — fine-grained resolution for the money chart's
1→8 crossover region (EXPERIMENTS.md #13/#14). Same NVIDIA ModelOpt NVFP4 base (marlin) + in-repo MTP head
(triton) as the published conc-1/8/32 rows; only `--max-num-seqs` changes.

- **Result (conc 4):** prefill 218.82 / decode **232.43** tok/s aggregate; 548/1000 prompts (hit the 600 s
  time cap), **0 errors**; peak mem 109.1 GB. Sits between conc-2 (161.2) and conc-8 (289.1) — the MTP
  decode curve stays monotonic through the low-batch region.
- **Acceptance holds ~constant:** mean accept-len **~3.0** (2.99–3.17), avg draft acceptance **~66–69%**,
  per-position 0.84 / 0.66 / 0.52 — indistinguishable from the other conc points. **Workload-driven, not
  concurrency-driven**, as expected for the in-repo MTP head.
- **TPOT median reads 0.0** — the usual `qwen3` reasoning-parser client artifact; trust the aggregate decode
  tok/s and the in-engine SpecDecoding throughput.
- Sweep siblings: [`-c1`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-mtp-c1/) · [`-c2`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-mtp-c2/) ·
  [`-c8`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-mtp-c8/) · [`-c16`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-mtp-c16/) ·
  [`maxctx/c32`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-mtp/).
