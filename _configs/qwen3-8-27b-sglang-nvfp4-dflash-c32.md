---
title: Qwen3.8-27B · SGLang · NVFP4 + DFlash2 · conc-32
model: Qwen/Qwen3.8-27B
company: Alibaba
family: Qwen
params: 27B (dense, hybrid linear-attn)
engine: SGLang
speculative: DFlash2
quant: NVFP4
quant_rationale: Same Spark-recipe NVFP4 target (RadixArk/Qwen3.8-27B-NVFP4) as the DSpark line, but DFlash2 block-diffusion draft (z-lab/Qwen3.8-27B-DFlash2 @50307d4) on the derived lmsysorg/sglang:qwen38-27b-dflash2 image. mem-fraction-static 0.90. conc-32 point of the ShareGPT sweep (client conc 1/2/4/8/16/32).
source_repo: RadixArk/Qwen3.8-27B-NVFP4
download_url: https://huggingface.co/RadixArk/Qwen3.8-27B-NVFP4
context: 262144
modalities: [text, image, video]
mm_served: false
concurrency: 32
tags: [qwen3.8-27b, Alibaba, Qwen, NVFP4, 16-40B, Spark recipe, conc-32]
status: blocked
measured_on: 2026-08-20
completed_at: 2026-08-20 05:25 +0800
engine_image: lmsysorg/sglang:qwen38-27b-dflash2@sha256:8a1a8f540fae7b1b9d1e8ee72ff279dc5ae3a9a3e4f83172f659b11d76f6f175
run_command: |
  # Not run — memory ceiling. Last attempted boot used MAX_CONCURRENT_REQUESTS=5.
  cd ~/Desktop/Qwen3.8-27B-SGLang-DGX-Spark
  MAX_CONCURRENT_REQUESTS=5 ./start-dflash.sh
  python3 ~/Desktop/autobench/scripts/bench-serving.py \
    --base-url http://127.0.0.1:8888 --model qwen3.8-27b-sglang \
    --dataset ~/Desktop/autobench/benchmark_data/ShareGPT_V3_unfiltered_cleaned_split.json \
    --num-prompts 1000 --max-seconds 900 --concurrency 32 --max-tokens 256
---

**BLOCKED — memory ceiling, same wall as [`c8`]({{ site.baseurl }}/configs/qwen3-8-27b-sglang-nvfp4-dflash-c8/).** A 32-running DFlash2 boot at 0.90 was never stable on this box (first-request SIGKILL even after the quantized-head patch). Not attempted.

- Series: [`c1`]({{ site.baseurl }}/configs/qwen3-8-27b-sglang-nvfp4-dflash-c1/) · [`c2`]({{ site.baseurl }}/configs/qwen3-8-27b-sglang-nvfp4-dflash-c2/) · [`c4`]({{ site.baseurl }}/configs/qwen3-8-27b-sglang-nvfp4-dflash-c4/) · [`c8`]({{ site.baseurl }}/configs/qwen3-8-27b-sglang-nvfp4-dflash-c8/) · [`c16`]({{ site.baseurl }}/configs/qwen3-8-27b-sglang-nvfp4-dflash-c16/) · [`c32`]({{ site.baseurl }}/configs/qwen3-8-27b-sglang-nvfp4-dflash-c32/).
