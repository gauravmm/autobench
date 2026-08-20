---
title: MiniMax-M2.7-REAP 172B · vLLM · NVFP4 (W4A4)
model: saricles/MiniMax-M2.7-REAP-172B-A10B-NVFP4-GB10
company: MiniMax (base) · saricles (REAP + NVFP4)
family: MiniMax
params: 172B / ~10B (MoE, REAP-pruned from 230B/10B — 256→192 experts, 62 layers)
engine: vLLM
quant: NVFP4 (W4A4)
quant_rationale: Community modelopt NVFP4 of a 25%-REAP-pruned MiniMax-M2.7 (saricles upload), produced with NVIDIA TensorRT-Model-Optimizer (mtq.NVFP4_DEFAULT_CFG, 6-dataset agentic calibration, GB10-tuned ignore list). Unlike the self-quantized M2.5 REAP sibling (compressed-tensors W4A16), this is real W4A4 NVFP4 (FP4 weights AND dynamic FP4 activations) — which is exactly the format flashinfer_cutlass accepts, so it loads on the native FlashInferCutlassNvFp4 GEMM + FLASHINFER_CUTLASS MoE backend with NO --moe-backend marlin override. vLLM auto-detects it as modelopt_fp4.
source_repo: saricles/MiniMax-M2.7-REAP-172B-A10B-BF16
download_url: https://huggingface.co/saricles/MiniMax-M2.7-REAP-172B-A10B-NVFP4-GB10
hf_repo: saricles/MiniMax-M2.7-REAP-172B-A10B-NVFP4-GB10
hf_url: https://huggingface.co/saricles/MiniMax-M2.7-REAP-172B-A10B-NVFP4-GB10
context: 65536
modalities: [text]
mm_served: true
concurrency: 32
tags: [minimax-m27-reap-172b, MiniMax, MiniMax-M2, NVFP4, 130B+, Spark recipe, REAP, conc-32]
status: done
prefill_toks: 124.22
decode_toks: 111.91
mem_gb: 116
mem_source: system MemAvailable peak (10s sampling) — used ~116/127.6 GB at util 0.90 (weights 92.2 GiB + KV/activations/CUDA)
measured_on: 2026-06-27
completed_at: 2026-06-27 19:22 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:68e23ddd982ad5642e21354c2242a3a86d31a3ea83f5937e5c3867942dc6595b
run_command: |
  # Community saricles modelopt NVFP4 (W4A4), mounted as a LOCAL path. vLLM auto-detects
  # quant_algo=NVFP4 -> quantization=modelopt_fp4 and picks FlashInferCutlassNvFp4LinearKernel
  # + FLASHINFER_CUTLASS MoE with NO marlin override (W4A4 is the format cutlass wants — the
  # opposite of the M2.5 self-quant, which is W4A16 and REQUIRES --moe-backend marlin).
  # MiniMaxM2ForCausalLM resolves natively. --kv-cache-dtype fp8 keeps KV tiny.
  docker run -d --gpus all --ipc=host -p 8000:8000 --name bench-m27 \
    -v ~/Desktop/reap-nvfp8/models/MiniMax-M2.7-REAP-172B-A10B-NVFP4-GB10:/model:ro \
    vllm/vllm-openai:nightly-aarch64 \
    /model \
    --host 0.0.0.0 --port 8000 --max-model-len 65536 \
    --gpu-memory-utilization 0.90 --max-num-seqs 32 \
    --kv-cache-dtype fp8 \
    --trust-remote-code \
    --served-model-name minimax-m27-reap-nvfp4
  python3 scripts/bench-serving.py --base-url http://localhost:8000 \
    --model minimax-m27-reap-nvfp4 \
    --dataset benchmark_data/ShareGPT_V3_unfiltered_cleaned_split.json \
    --num-prompts 1000 --max-seconds 900 --concurrency 32 --max-tokens 256
---

**Done — community NVFP4 (W4A4), serves on vLLM with the NATIVE flashinfer_cutlass backend.** This is
the **REAP-pruned** MiniMax-M2.7 (`saricles/MiniMax-M2.7-REAP-172B-A10B-NVFP4-GB10`: 172B total / ~10B
active, **192 experts** (pruned from 256), 62 layers, `MiniMaxM2ForCausalLM`, a reasoning/agentic model).
Lineage: **MiniMaxAI/MiniMax-M2.7** (230B, 256 experts, FP8) → saricles dequantizes FP8→BF16, REAP-prunes
to 75%-keep (192/256 experts) with a 6-dataset agentic calibration → BF16 → saricles NVFP4-quantizes
(modelopt `mtq.NVFP4_DEFAULT_CFG` + GB10-tuned ignore list, same agentic calibration). **98.9 GB on the
hub / 95 GB on disk (92.08 GiB loaded).**

**Result (conc-32 ShareGPT, 65536 ctx):** prefill **124.22 tok/s**, decode **111.91 tok/s**,
ttft_median 1214 ms, tpot_median 276 ms, **0 errors** (423/1000 prompts in the 900 s cap). Runtime
footprint **~116 GB** = util-0.90 reservation (92.2 GiB weights + 13.65 GiB KV/115k tokens + activations
+ CUDA). A touch slower than the smaller self-quantized [M2.5 REAP sibling] (decode 120, prefill 128) —
expected: more total weight mass (92 vs 75 GiB) and 192 vs 154 experts cost more memory-bandwidth per
decoded token, and the two checkpoints use different NVFP4 schemes (W4A4 cutlass here vs W4A16 marlin there).

**Serve recipe (GB10) — the key difference from the M2.5 REAP:** because this is genuine **W4A4**
NVFP4 (modelopt format), vLLM loads it on `FlashInferCutlassNvFp4LinearKernel` + the `FLASHINFER_CUTLASS`
MoE backend with **no `--moe-backend marlin` needed**. The M2.5 self-quant is W4A16 (weight-only), which
flashinfer_cutlass *rejects* — so it is forced onto marlin. Same architecture, opposite backend, purely
because of the activation-quant choice. `--quantization` is auto-detected as `modelopt_fp4`; only
`--trust-remote-code` + `--kv-cache-dtype fp8` are passed explicitly.

**Pair:** single-stream sibling at [conc-1 / 160K]({{ '/configs/minimax-m27-reap-172b-vllm-nvfp4-c1/' | relative_url }})
— the live `:4000` interactive gateway. Same `engine_image`, same checkpoint, same cutlass recipe; only
the operating point (context / concurrency / util / parsers) differs.
