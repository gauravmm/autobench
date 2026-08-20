---
title: Nemotron-3 Puzzle 75B-A9B · vLLM · NVFP4 · conc 1
model: nvidia/NVIDIA-Nemotron-Labs-3-Puzzle-75B-A9B-NVFP4
company: NVIDIA
family: Nemotron
params: 75.3B / 9.3B (MoE, hybrid Mamba-Transformer)
engine: vLLM
quant: NVFP4
quant_rationale: Blackwell-native FP4 (W4A4) — GB10 gets native FP4 compute; FP8 targets Hopper, BF16 (~150 GB) won't fit 121 GB. NVIDIA's own quant, ~44.5 GB. Same Nemotron-3-Super family/quant as the 120B sibling (served on cu130-nightly; older images reject its quant_algo whitelist).
source_repo: nvidia/NVIDIA-Nemotron-Labs-3-Puzzle-75B-A9B-NVFP4
download_url: https://huggingface.co/nvidia/NVIDIA-Nemotron-Labs-3-Puzzle-75B-A9B-NVFP4
context: 65536
modalities: [text]
concurrency: 1
tags: [nvidia-nemotron-3-puzzle-75b-a9b, NVIDIA, Nemotron, NVFP4, 41-130B, Spark recipe, conc-1]
status: done
prefill_toks: 35.0
decode_toks: 19.84
mem_gb: 108.43
mem_source: system MemAvailable delta (10s sampling) — vLLM 0.85 reservation; real NVFP4 weights ~53.5 GB
measured_on: 2026-07-11
completed_at: 2026-07-11 16:29 +08
engine_image: vllm/vllm-openai:nightly-aarch64
run_command: |
  # vllm/vllm-openai:nightly-aarch64 — loads this NVFP4 checkpoint cleanly (no quant_algo whitelist
  # rejection, unlike the older images that blocked the Super-120B sibling). ENTRYPOINT ["vllm","serve"].
  scripts/bench-vllm-serving.sh nvidia/NVIDIA-Nemotron-Labs-3-Puzzle-75B-A9B-NVFP4 \
    65536 1 1000 900 256 --trust-remote-code --reasoning-parser nemotron_v3
---

**Nemotron-3 Puzzle 75B-A9B (NVFP4) — conc 1 (single-stream).** Compressed variant of Nemotron-3-Super
(75.3B total / 9.3B active, hybrid Mamba-Transformer MoE: 40 Mamba + 40 MoE + 8 attention blocks).
Benchmarked as the DGX-Spark-suitable variant (Blackwell-native FP4).

- **Load:** 524 s on `nightly-aarch64` (incl. torch.compile cold boot). NVFP4 weights ~53.5 GB (6 shards).
- **Workload:** ShareGPT V3, concurrency 1. **Hit the 15-min cap at 72/1000 prompts, 0 errors** (911.8 s).
- **Throughput (single-stream):** prefill **35.0 tok/s**, decode **19.84 tok/s**; median **TTFT 12.8 s**.
  Decode tracks the 9.3B active params — in line with the Super-120B sibling's single-stream range
  (~22–24 tok/s for 12B active per the vLLM DGX Spark blog; this 75B/9.3B lands a touch lower at 19.8).
