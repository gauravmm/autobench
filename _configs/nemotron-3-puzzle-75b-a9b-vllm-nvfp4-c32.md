---
title: Nemotron-3 Puzzle 75B-A9B · vLLM · NVFP4 · conc 32
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
concurrency: 32
tags: [nvidia-nemotron-3-puzzle-75b-a9b, NVIDIA, Nemotron, NVFP4, 41-130B, Spark recipe, conc-32]
status: done
prefill_toks: 186.99
decode_toks: 177.79
mem_gb: 109.10
mem_source: system MemAvailable delta (10s sampling) — vLLM 0.85 reservation; real NVFP4 weights ~53.5 GB
measured_on: 2026-07-11
completed_at: 2026-07-11 17:21 +08
engine_image: vllm/vllm-openai:nightly-aarch64
run_command: |
  # vllm/vllm-openai:nightly-aarch64 — loads this NVFP4 checkpoint cleanly. ENTRYPOINT ["vllm","serve"].
  # Run under scripts/mem-watchdog.sh (6 GB floor) — conc 32 piles graph-capture/activation buffers on
  # the util-0.85 reservation. It did NOT trip (survived at ~12 GB free).
  scripts/bench-vllm-serving.sh nvidia/NVIDIA-Nemotron-Labs-3-Puzzle-75B-A9B-NVFP4 \
    65536 32 1000 900 256 --trust-remote-code --reasoning-parser nemotron_v3
---

**Nemotron-3 Puzzle 75B-A9B (NVFP4) — conc 32.** Compressed variant of Nemotron-3-Super (75.3B total /
9.3B active, hybrid Mamba-Transformer MoE: 40 Mamba + 40 MoE + 8 attention blocks). Benchmarked as the
DGX-Spark-suitable variant (Blackwell-native FP4).

- **Load:** 565 s on `nightly-aarch64`. NVFP4 weights ~53.5 GB. Run under `mem-watchdog.sh` (6 GB floor) —
  **did not trip** (peak ~109.1 GB used, ~12 GB free), so conc 32 at ctx 65536 is safe for this model.
- **Workload:** ShareGPT V3, concurrency 32. **Hit the 15-min cap at 647/1000 prompts, 0 errors** (920.3 s).
- **Throughput (aggregate, conc 32):** prefill **186.99 tok/s**, decode **177.79 tok/s**; median TTFT 44.9 s.
- **Sweep scaling (conc 1 → 8 → 32):** decode **19.84 → 94.04 → 177.79 tok/s**, prefill **35.0 → 112.82 →
  186.99**. Aggregate decode keeps scaling with batch (9× from conc 1 to 32) but sub-linearly past conc 8;
  TTFT climbs **12.8 → 21.1 → 44.9 s** as more prompts queue their prefills. 0 errors at every level.
