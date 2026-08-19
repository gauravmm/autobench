---
title: Qwen3.8-27B · SGLang · NVFP4 + DFlash2 · conc-4
model: Qwen/Qwen3.8-27B
company: Alibaba
family: Qwen
params: 27B (dense, hybrid linear-attn)
engine: SGLang
speculative: DFlash2
quant: NVFP4
quant_rationale: Same Spark-recipe NVFP4 target (RadixArk/Qwen3.8-27B-NVFP4) as the DSpark line, but DFlash2 block-diffusion draft (z-lab/Qwen3.8-27B-DFlash2 @50307d4) on the derived lmsysorg/sglang:qwen38-27b-dflash2 image. mem-fraction-static 0.90. conc-4 point of the ShareGPT sweep (client conc 1/2/4/8/16/32).
source_repo: RadixArk/Qwen3.8-27B-NVFP4
download_url: https://huggingface.co/RadixArk/Qwen3.8-27B-NVFP4
context: 262144
modalities: [text, image, video]
mm_served: false
concurrency: 4
tags: [qwen3.8-27b, Alibaba, Qwen, NVFP4, 16-40B, Spark recipe, conc-4]
status: done
prefill_toks: 32.26
decode_toks: 85.09
mem_gb: 110.61
mem_source: system MemAvailable delta (10s sampling) over the DFlash2 boot (MAX_CONCURRENT_REQUESTS=5)
spec_acceptance: "accept len ~3.2\u20134.0 of 8 draft tokens \xB7 accept rate ~0.32\u20130.43 on ShareGPT\
  \ (decode-batch logs). Higher than DSpark's ~0.25 on the same workload; still well\
  \ below 70\u201385% MTP/EAGLE3."
measured_on: 2026-08-20
completed_at: 2026-08-20 05:24 +0800
engine_image: lmsysorg/sglang:qwen38-27b-dflash2@sha256:8a1a8f540fae7b1b9d1e8ee72ff279dc5ae3a9a3e4f83172f659b11d76f6f175
run_command: |
  # MiaAI-Lab Spark recipe, native 262K, YaRN off, mem-fraction-static 0.90.
  cd ~/Desktop/Qwen3.8-27B-SGLang-DGX-Spark
  MAX_CONCURRENT_REQUESTS=5 ./start-dflash.sh
  python3 ~/Desktop/autobench/scripts/bench-serving.py \
    --base-url http://127.0.0.1:8888 --model qwen3.8-27b-sglang \
    --dataset ~/Desktop/autobench/benchmark_data/ShareGPT_V3_unfiltered_cleaned_split.json \
    --num-prompts 1000 --max-seconds 900 --concurrency 4 --max-tokens 256
  # RESULT prefill_toks=32.26 decode_toks=85.09 completed=27 errors=973 duration_s=68.6 hit_time_cap=False
  # image lmsysorg/sglang:qwen38-27b-dflash2@sha256:8a1a8f540fae7b1b9d1e8ee72ff279dc5ae3a9a3e4f83172f659b11d76f6f175
---

**conc-4 point of the Qwen3.8-27B SGLang NVFP4 + DFlash2 Spark-recipe line.**
MiaAI-Lab `start-dflash.sh` on derived `lmsysorg/sglang:qwen38-27b-dflash2` (upstream DFLASH2 overlay +
in-place quantized-head patch — **no dense lm_head dequant**; that path hard-rebooted this box). Draft
`z-lab/Qwen3.8-27B-DFlash2@50307d4`, 8 draft tokens, `--mem-fraction-static 0.90`, native 262K, YaRN
off. **This conc ran with `MAX_CONCURRENT_REQUESTS=5`** (DFLASH uses 5 mamba slots/req so
max_running_requests is `floor(MAX*4/5)`). CUDA-graph decode cap was pinned to the running-request
ceiling.

- **Result (conc 4):** prefill **32.26** / decode **85.09** tok/s aggregate;
  **27/1000 prompts, 973 errors**, duration 68.6s (engine SIGKILL mid-run (GC freeze / unified-mem spike); numbers are from completed requests only — treat as noisy if n is small). TTFT median 360.0 ms,
  TPOT median 40.0 ms, req throughput 0.394/s.
- **vs DSpark (same checkpoint, same ShareGPT):** DFlash2 c1 **30.0 vs DSpark 23.4** (+28%);
  c2 **56.2 vs 43.4** (+29%). c4 **85.1 vs 75.5** is a 69 s / 27-request snippet after the engine
  died — do not splice it onto the DSpark c4 15-min point as a clean race.
- **vs vLLM MTP** (unsloth NVFP4, ctx 65536): MTP c1 21.35. DFlash2 c1 **30.0** is the single-stream
  winner on this box; counting is `completion_tokens` (this DFlash2 image batches several tokens per
  SSE event — event-counting would under-read ~4×, as MiaAI documented).
- **Acceptance:** ~3.2–4.0 tokens/step of 8 (~32–43%). Better than DSpark's ~25% on ShareGPT; still
  far from 70–85% MTP/EAGLE3. Workload-driven, not a draft/target mismatch (official z-lab DFlash2
  against RadixArk NVFP4, quantized-head selector in-place).
- **Memory / crashes:** peak **110.61 GB**. First-request GC freeze (`Freezing GC in Scheduler
  process`) plus 0.90 reservation sits at ~7–9 GB free; the 6 GB watchdog SIGKILLs (exit 137). Recipe
  0.95 hard-rebooted this box at draft-graph capture before the quantized-head patch; we never went
  above 0.90. DFLASH `extra_buffer` (not lazy) + 5 state slots/req.
- Series: [`c1`](qwen3-8-27b-sglang-nvfp4-dflash-c1) · [`c2`](qwen3-8-27b-sglang-nvfp4-dflash-c2) · [`c4`](qwen3-8-27b-sglang-nvfp4-dflash-c4) · [`c8`](qwen3-8-27b-sglang-nvfp4-dflash-c8) · [`c16`](qwen3-8-27b-sglang-nvfp4-dflash-c16) · [`c32`](qwen3-8-27b-sglang-nvfp4-dflash-c32). Matched DSpark: [`c1`](qwen3-8-27b-sglang-nvfp4-dspark-c1) · [`c2`](qwen3-8-27b-sglang-nvfp4-dspark-c2) · [`c4`](qwen3-8-27b-sglang-nvfp4-dspark-c4) · [`c8`](qwen3-8-27b-sglang-nvfp4-dspark-c8) · [`c16`](qwen3-8-27b-sglang-nvfp4-dspark-c16) · [`c32`](qwen3-8-27b-sglang-nvfp4-dspark-c32).

