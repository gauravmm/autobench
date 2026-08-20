---
title: Qwen3.6-35B-A3B · vLLM · NVFP4 + MTP · conc 16
model: Qwen/Qwen3.6-35B-A3B
company: Alibaba
family: Qwen
params: 35B / 3B (MoE)
engine: vLLM
speculative: MTP
quant: NVFP4
quant_rationale: conc-16 fine-grained point of the Qwen3.6-35B-A3B NVFP4 + native-MTP sweep — same stack as conc-1/8/32 (nvidia ModelOpt NVFP4 base on marlin + in-repo MTP head on triton). Traces the 8→32 region of the money chart (EXPERIMENTS.md #13/#14) where MTP's aggregate throughput keeps climbing. Acceptance should hold ~constant vs the other conc points (workload-driven).
source_repo: nvidia/Qwen3.6-35B-A3B-NVFP4
download_url: https://huggingface.co/nvidia/Qwen3.6-35B-A3B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 16
tags: [qwen3.6-35b-a3b, Alibaba, Qwen, NVFP4, 16-40B, Spark recipe, conc-16]
status: done
prefill_toks: 446.25
decode_toks: 433.28
mem_gb: 107.34
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV (util 0.85) + MTP head
spec_acceptance: mean acceptance length ~3.0 (range 2.96–3.06) · avg draft acceptance ~65–69% · per-position 0.84/0.66/0.51 (3 spec tokens)
measured_on: 2026-07-01
completed_at: 2026-07-01 12:54 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:68e23ddd982ad5642e21354c2242a3a86d31a3ea83f5937e5c3867942dc6595b
run_command: |
  # conc-16 fine-grained point. Same NVIDIA DGX Spark MTP recipe as conc-1/8/32 — only --max-num-seqs differs.
  scripts/bench-vllm-serving.sh nvidia/Qwen3.6-35B-A3B-NVFP4 65536 16 1000 600 256 \
    --quantization modelopt --trust-remote-code --reasoning-parser qwen3 --moe-backend marlin \
    --speculative-config '{"method":"mtp","num_speculative_tokens":3,"moe_backend":"triton"}'
  # 1000/1000 prompts (did NOT hit the 600 s cap; finished 590.6 s), 0 errors. ready after 440 s.
---

**conc-16 point of the Qwen3.6-35B-A3B NVFP4 + MTP sweep** — fine-grained resolution for the money chart's
8→32 region (EXPERIMENTS.md #13/#14). Same NVIDIA ModelOpt NVFP4 base (marlin) + in-repo MTP head (triton)
as the published conc-1/8/32 rows; only `--max-num-seqs` changes.

- **Result (conc 16):** prefill 446.25 / decode **433.28** tok/s aggregate; **1000/1000 prompts, 0 errors**
  (a full-coverage measurement — did not hit the 600 s cap); peak mem 107.3 GB. Sits between conc-8 (289.1)
  and conc-32 (541.3) — the MTP decode curve is monotonic across the entire 1→32 sweep.
- **Acceptance holds ~constant:** mean accept-len **~3.0** (2.96–3.06), avg draft acceptance **~65–69%**,
  per-position 0.84 / 0.66 / 0.51 — indistinguishable from every other conc point. **Workload-driven, not
  concurrency-driven**, confirming the rule at the high-batch end too.
- **Completes the MTP line of the money chart:** decode 93.9 (c1) → 161.2 (c2) → 232.4 (c4) → 289.1 (c8) →
  **433.3 (c16)** → 541.3 (c32) tok/s, acceptance flat ~3.0/~67% throughout. Pair against the DFlash line
  (which peaks at conc-1 then decays under load) to locate the crossover.
- **TPOT median reads 0.0** — the usual `qwen3` reasoning-parser client artifact; trust the aggregate decode
  tok/s and the in-engine SpecDecoding throughput.
- Sweep siblings: [`-c1`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-mtp-c1/) · [`-c2`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-mtp-c2/) ·
  [`-c4`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-mtp-c4/) · [`-c8`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-mtp-c8/) ·
  [`maxctx/c32`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-mtp/).
