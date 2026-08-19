---
title: Qwen3.8-27B · SGLang · NVFP4 + DSpark · conc-4
model: Qwen/Qwen3.8-27B
company: Alibaba
family: Qwen
params: 27B (dense, hybrid linear-attn)
engine: SGLang
speculative: DSpark
quant: NVFP4
quant_rationale: MiaAI-Lab SGLang DGX Spark recipe (https://github.com/MiaAI-Lab/Qwen3.8-27B-SGLang-DGX-Spark). RadixArk NVFP4 W4A4 of Qwen3.8-27B on the cookbook-pinned lmsysorg/sglang:qwen38-27b image, DSpark block-7 / 8 draft tokens (RadixArk/Qwen3.8-27B-DSpark, unquant), mem-fraction-static 0.90, FP8 KV, GDN bf16, extra_buffer_lazy, native 262K, YaRN off. conc-4 point of the ShareGPT sweep (client conc 1/2/4/8/16/32).
source_repo: RadixArk/Qwen3.8-27B-NVFP4
download_url: https://huggingface.co/RadixArk/Qwen3.8-27B-NVFP4
context: 262144
modalities: [text, image, video]
mm_served: false
concurrency: 4
tags: [qwen3.8-27b, Alibaba, Qwen, NVFP4, 16-40B, Spark recipe, conc-4]
status: done
prefill_toks: 115.59
decode_toks: 75.49
mem_gb: 110.75
mem_source: system MemAvailable delta (10s sampling) over the DSpark boot (MAX_CONCURRENT_REQUESTS=16)
spec_acceptance: "accept len ~2.5\u20133.0 of 8 draft tokens \xB7 accept rate ~0.22\u20130.30 on ShareGPT\
  \ (decode-batch logs). Well below the 70\u201385% MTP/EAGLE3 rule of thumb \u2014\
  \ DSpark on this chat workload is weaker than MiaAI's code probe."
measured_on: 2026-08-20
completed_at: 2026-08-20 04:17 +0800
engine_image: lmsysorg/sglang:qwen38-27b@sha256:febfb971c7352570fc445c466ebd6ffc9d896024958e544a60f2137fd85856b1
run_command: |
  # MiaAI-Lab Spark recipe, native 262K, YaRN off, mem-fraction-static 0.90.
  cd ~/Desktop/Qwen3.8-27B-SGLang-DGX-Spark
  MAX_CONCURRENT_REQUESTS=16 ./start-dspark.sh
  python3 ~/Desktop/autobench/scripts/bench-serving.py \
    --base-url http://127.0.0.1:8888 --model qwen3.8-27b-sglang \
    --dataset ~/Desktop/autobench/benchmark_data/ShareGPT_V3_unfiltered_cleaned_split.json \
    --num-prompts 1000 --max-seconds 900 --concurrency 4 --max-tokens 256
  # RESULT prefill_toks=115.59 decode_toks=75.49 completed=286 errors=0 duration_s=911.2 hit_time_cap=True
  # image lmsysorg/sglang:qwen38-27b@sha256:febfb971c7352570fc445c466ebd6ffc9d896024958e544a60f2137fd85856b1
---

**conc-4 point of the Qwen3.8-27B SGLang NVFP4 + DSpark Spark-recipe line.**
MiaAI-Lab `start-dspark.sh` (block-7 / 8 draft, unquant `RadixArk/Qwen3.8-27B-DSpark`), native 262K,
YaRN off, `--mem-fraction-static 0.90`, FP8 KV, GDN bf16, `extra_buffer_lazy`. ShareGPT via
`scripts/bench-serving.py`. **This conc ran with `MAX_CONCURRENT_REQUESTS=16`** (mamba pool =
16×4 slots). Larger pools at 0.90 rest at ~7–9 GB free and the 6 GB watchdog SIGKILLs the
container (unified-memory GB10, no graceful OOM).

- **Result (conc 4):** prefill **115.59** / decode **75.49** tok/s aggregate;
  **286/1000 prompts, 0 errors**, duration 911.2s (hit the 900 s time cap). TTFT median 354.3 ms,
  TPOT median 50.7 ms, req throughput 0.314/s.
- **vs vLLM on this box** (unsloth NVFP4, ctx 65536 — not a matched pair, but the closest):
  vLLM base c1 decode 11.16 / c8 75.04; vLLM MTP c1 21.35 / c8 126.68. DSpark c1 **23.4** ties MTP
  (+110% vs base); DSpark c8 **118.3** is ~1.57× vLLM base and a hair under MTP 126.7. Context here is
  **262144 vs 65536**.
- **Acceptance:** ~2.5–3.0 tokens/step of 8 drafted (~22–30%). ShareGPT chat; MiaAI's LRUCache code
  probe was ~51 tok/s single-stream. Cross-check: far from 70–85% MTP/EAGLE3 — expected for DSpark on
  general chat, not a misconfig.
- **Memory:** peak **110.75 GB**. 32-running boot: weights ~22.6 GB + DSpark draft ~2.4 GB + GDN
  mamba ~28 GB (128 slots) + FP8 KV. Dropping `MAX_CONCURRENT_REQUESTS` shrinks mamba, not the 0.90
  reservation. Watchdog floor 6 GB.
- Series: [`c1`](qwen3-8-27b-sglang-nvfp4-dspark-c1) · [`c2`](qwen3-8-27b-sglang-nvfp4-dspark-c2) · [`c4`](qwen3-8-27b-sglang-nvfp4-dspark-c4) · [`c8`](qwen3-8-27b-sglang-nvfp4-dspark-c8) · [`c16`](qwen3-8-27b-sglang-nvfp4-dspark-c16) · [`c32`](qwen3-8-27b-sglang-nvfp4-dspark-c32). Matched DFlash2: [`c1`](qwen3-8-27b-sglang-nvfp4-dflash-c1) · [`c2`](qwen3-8-27b-sglang-nvfp4-dflash-c2) · [`c4`](qwen3-8-27b-sglang-nvfp4-dflash-c4) · [`c8`](qwen3-8-27b-sglang-nvfp4-dflash-c8) · [`c16`](qwen3-8-27b-sglang-nvfp4-dflash-c16) · [`c32`](qwen3-8-27b-sglang-nvfp4-dflash-c32).

