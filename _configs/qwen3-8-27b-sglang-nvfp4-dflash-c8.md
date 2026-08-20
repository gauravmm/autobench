---
title: Qwen3.8-27B · SGLang · NVFP4 + DFlash2 · conc-8
model: Qwen/Qwen3.8-27B
company: Alibaba
family: Qwen
params: 27B (dense, hybrid linear-attn)
engine: SGLang
speculative: DFlash2
quant: NVFP4
quant_rationale: Same Spark-recipe NVFP4 target (RadixArk/Qwen3.8-27B-NVFP4) as the DSpark line, but DFlash2 block-diffusion draft (z-lab/Qwen3.8-27B-DFlash2 @50307d4) on the derived lmsysorg/sglang:qwen38-27b-dflash2 image. mem-fraction-static 0.90. conc-8 point of the ShareGPT sweep (client conc 1/2/4/8/16/32).
source_repo: RadixArk/Qwen3.8-27B-NVFP4
download_url: https://huggingface.co/RadixArk/Qwen3.8-27B-NVFP4
context: 262144
modalities: [text, image, video]
mm_served: false
concurrency: 8
tags: [qwen3.8-27b, Alibaba, Qwen, NVFP4, 16-40B, Spark recipe, conc-8]
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
    --num-prompts 1000 --max-seconds 900 --concurrency 8 --max-tokens 256
---

**BLOCKED — memory ceiling above DFlash2 conc-4.** The 4-running boot (`MAX_CONCURRENT_REQUESTS=5`, 5 mamba slots/req → 4 running, `--cuda-graph-max-bs-decode 4`) SIGKILL'd 69 s into conc-4 (27 ok / 973 err, exit 137) after a scheduler GC freeze on top of the 0.90 reservation (~7 GB free at ready). The 8-running DFlash2 boot already died mid conc-2. Do not retry conc-8 at 0.90.

- Last partial point: [`c4`]({{ site.baseurl }}/configs/qwen3-8-27b-sglang-nvfp4-dflash-c4/) decode **85.1** tok/s (n=27, noisy).
- Clean last point: [`c1`]({{ site.baseurl }}/configs/qwen3-8-27b-sglang-nvfp4-dflash-c1/) decode **30.0** (116/1000, 0 errors).
- Series: [`c1`]({{ site.baseurl }}/configs/qwen3-8-27b-sglang-nvfp4-dflash-c1/) · [`c2`]({{ site.baseurl }}/configs/qwen3-8-27b-sglang-nvfp4-dflash-c2/) · [`c4`]({{ site.baseurl }}/configs/qwen3-8-27b-sglang-nvfp4-dflash-c4/) · [`c8`]({{ site.baseurl }}/configs/qwen3-8-27b-sglang-nvfp4-dflash-c8/) · [`c16`]({{ site.baseurl }}/configs/qwen3-8-27b-sglang-nvfp4-dflash-c16/) · [`c32`]({{ site.baseurl }}/configs/qwen3-8-27b-sglang-nvfp4-dflash-c32/).
