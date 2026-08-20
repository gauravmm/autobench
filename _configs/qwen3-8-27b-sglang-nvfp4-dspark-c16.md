---
title: Qwen3.8-27B · SGLang · NVFP4 + DSpark · conc-16
model: Qwen/Qwen3.8-27B
company: Alibaba
family: Qwen
params: 27B (dense, hybrid linear-attn)
engine: SGLang
speculative: DSpark
quant: NVFP4
quant_rationale: MiaAI-Lab SGLang DGX Spark recipe (https://github.com/MiaAI-Lab/Qwen3.8-27B-SGLang-DGX-Spark). RadixArk NVFP4 W4A4 of Qwen3.8-27B on the cookbook-pinned lmsysorg/sglang:qwen38-27b image, DSpark block-7 / 8 draft tokens (RadixArk/Qwen3.8-27B-DSpark, unquant), mem-fraction-static 0.90, FP8 KV, GDN bf16, extra_buffer_lazy, native 262K, YaRN off. conc-16 point of the ShareGPT sweep (client conc 1/2/4/8/16/32).
source_repo: RadixArk/Qwen3.8-27B-NVFP4
download_url: https://huggingface.co/RadixArk/Qwen3.8-27B-NVFP4
context: 262144
modalities: [text, image, video]
mm_served: false
concurrency: 16
tags: [qwen3.8-27b, Alibaba, Qwen, NVFP4, 16-40B, Spark recipe, conc-16]
status: blocked
measured_on: 2026-08-20
completed_at: 2026-08-20 05:25 +0800
engine_image: lmsysorg/sglang:qwen38-27b@sha256:febfb971c7352570fc445c466ebd6ffc9d896024958e544a60f2137fd85856b1
run_command: |
  # Not run — memory ceiling. Last attempted boot used MAX_CONCURRENT_REQUESTS=8.
  cd ~/Desktop/Qwen3.8-27B-SGLang-DGX-Spark
  MAX_CONCURRENT_REQUESTS=8 ./start-dspark.sh
  python3 ~/Desktop/autobench/scripts/bench-serving.py \
    --base-url http://127.0.0.1:8888 --model qwen3.8-27b-sglang \
    --dataset ~/Desktop/autobench/benchmark_data/ShareGPT_V3_unfiltered_cleaned_split.json \
    --num-prompts 1000 --max-seconds 900 --concurrency 16 --max-tokens 256
---

**BLOCKED — memory ceiling above DSpark conc-8.** The 8-running boot (`MAX_CONCURRENT_REQUESTS=8`, mamba 32 slots) SIGKILL'd mid conc-8 after 406 successful requests (watchdog floor 6 GB, container exit 137, unified-memory GB10). 16- and 32-running boots already died *earlier* (32-boot during autotune at an 8 GB floor; 16-boot at the conc-8 *start*). Raising `max-mamba-cache-size` to actually admit 16 running requests adds ~7–14 GB of GDN state on top of the 0.90 reservation and is what takes the box down. Do not retry the identical 0.90 / conc-16 config. Dropping mem-fraction below 0.90 would be a separate util-adjusted regime.

- Last good point: [`c8`](qwen3-8-27b-sglang-nvfp4-dspark-c8) decode **118.3** tok/s (partial).
- Series: [`c1`](qwen3-8-27b-sglang-nvfp4-dspark-c1) · [`c2`](qwen3-8-27b-sglang-nvfp4-dspark-c2) · [`c4`](qwen3-8-27b-sglang-nvfp4-dspark-c4) · [`c8`](qwen3-8-27b-sglang-nvfp4-dspark-c8) · [`c16`](qwen3-8-27b-sglang-nvfp4-dspark-c16) · [`c32`](qwen3-8-27b-sglang-nvfp4-dspark-c32).
