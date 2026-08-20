---
title: Qwen3.6-35B-A3B · vLLM · NVFP4 + MTP · conc 2
model: Qwen/Qwen3.6-35B-A3B
company: Alibaba
family: Qwen
params: 35B / 3B (MoE)
engine: vLLM
speculative: MTP
quant: NVFP4
quant_rationale: conc-2 fine-grained point of the Qwen3.6-35B-A3B NVFP4 + native-MTP sweep — same stack as conc-1/8/32 (nvidia ModelOpt NVFP4 base on marlin + in-repo MTP head on triton). Fills the 1→8 crossover region for the money chart (EXPERIMENTS.md #13/#14) — where does MTP's single-stream win start decaying as the batch fills. Acceptance should hold ~constant vs the other conc points (workload-driven).
source_repo: nvidia/Qwen3.6-35B-A3B-NVFP4
download_url: https://huggingface.co/nvidia/Qwen3.6-35B-A3B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 2
tags: [qwen3.6-35b-a3b, Alibaba, Qwen, NVFP4, 16-40B, Spark recipe, conc-2]
status: done
prefill_toks: 176.53
decode_toks: 161.21
mem_gb: 106.00
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV (util 0.85) + MTP head
spec_acceptance: mean acceptance length ~3.0 (range 2.86–3.18) · avg draft acceptance ~66–69% · per-position 0.84/0.67/0.53 (3 spec tokens)
measured_on: 2026-07-01
completed_at: 2026-07-01 12:20 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:68e23ddd982ad5642e21354c2242a3a86d31a3ea83f5937e5c3867942dc6595b
run_command: |
  # conc-2 fine-grained point. Same NVIDIA DGX Spark MTP recipe as conc-1/8/32 — only --max-num-seqs differs.
  scripts/bench-vllm-serving.sh nvidia/Qwen3.6-35B-A3B-NVFP4 65536 2 1000 900 256 \
    --quantization modelopt --trust-remote-code --reasoning-parser qwen3 --moe-backend marlin \
    --speculative-config '{"method":"mtp","num_speculative_tokens":3,"moe_backend":"triton"}'
  # 569/1000 prompts (hit 900 s time cap), 0 errors. ready after 433 s. TTFT median 2996 ms.
---

**conc-2 point of the Qwen3.6-35B-A3B NVFP4 + MTP sweep** — fine-grained resolution for the money chart's
1→8 crossover region (EXPERIMENTS.md #13/#14). Boots the same NVIDIA ModelOpt NVFP4 base (marlin) + in-repo
MTP head (triton) as the published conc-1/8/32 rows; only `--max-num-seqs` changes.

- **Result (conc 2):** prefill 176.53 / decode **161.21** tok/s aggregate; 569/1000 prompts (hit the 900 s
  time cap), **0 errors**; peak mem 106.0 GB. Sits cleanly between conc-1 (93.9) and conc-8 (289.1), so the
  MTP decode curve is monotonic through the low-batch region — no anomaly.
- **Acceptance holds ~constant:** mean accept-len **~3.0** (2.86–3.18), avg draft acceptance **~66–69%**,
  per-position 0.84 / 0.67 / 0.53 — indistinguishable from conc-8 (~3.0 / ~67%) and conc-32 (~3.0 / 66–69%).
  Confirms the **workload-driven, not concurrency-driven** acceptance rule for the in-repo MTP head.
- **TPOT median reads 0.0** — the usual `qwen3` reasoning-parser client artifact; trust the aggregate decode
  tok/s and the in-engine SpecDecoding throughput (~116 tok/s accepted).
- Sweep siblings: [`-c1`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-mtp-c1/) · [`-c4`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-mtp-c4/) ·
  [`-c8`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-mtp-c8/) · [`-c16`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-mtp-c16/) ·
  [`maxctx/c32`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-mtp/).
