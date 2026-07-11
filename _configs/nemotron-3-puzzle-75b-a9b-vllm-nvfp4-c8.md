---
title: Nemotron-3 Puzzle 75B-A9B · vLLM · NVFP4 · conc 8
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
concurrency: 8
tags: [nvidia-nemotron-3-puzzle-75b-a9b, NVIDIA, Nemotron, NVFP4, 41-130B, Spark recipe, conc-8]
status: done
prefill_toks: 112.82
decode_toks: 94.04
mem_gb: 108.86
mem_source: system MemAvailable delta (10s sampling) — vLLM 0.85 reservation; real NVFP4 weights ~53.5 GB
measured_on: 2026-07-11
completed_at: 2026-07-11 16:54 +08
engine_image: vllm/vllm-openai:nightly-aarch64
run_command: |
  # vllm/vllm-openai:nightly-aarch64 — loads this NVFP4 checkpoint cleanly. ENTRYPOINT ["vllm","serve"].
  scripts/bench-vllm-serving.sh nvidia/NVIDIA-Nemotron-Labs-3-Puzzle-75B-A9B-NVFP4 \
    65536 8 1000 900 256 --trust-remote-code --reasoning-parser nemotron_v3
---

**Nemotron-3 Puzzle 75B-A9B (NVFP4) — conc 8.** Compressed variant of Nemotron-3-Super (75.3B total /
9.3B active, hybrid Mamba-Transformer MoE: 40 Mamba + 40 MoE + 8 attention blocks). Benchmarked as the
DGX-Spark-suitable variant (Blackwell-native FP4).

- **Load:** 535 s on `nightly-aarch64`. NVFP4 weights ~53.5 GB.
- **Workload:** ShareGPT V3, concurrency 8. **Hit the 15-min cap at 340/1000 prompts, 0 errors** (912.6 s).
- **Throughput (aggregate, conc 8):** prefill **112.82 tok/s**, decode **94.04 tok/s**; median TTFT 21.1 s.
  ~4.7× the conc-1 decode (19.84 → 94.04) — near-linear batch scaling on the 9.3B active params. TTFT
  rises (12.8 s → 21.1 s) as 8 prompts queue their prefills; still 0 errors.
