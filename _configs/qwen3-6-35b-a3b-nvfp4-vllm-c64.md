---
title: Qwen3.6-35B-A3B · vLLM · NVFP4 · conc 64
model: Qwen/Qwen3.6-35B-A3B
company: Alibaba
family: Qwen
params: 35B / 3B (MoE)
engine: vLLM
quant: NVFP4
quant_rationale: NVIDIA's OFFICIAL NVFP4 of the Qwen3.6-35B-A3B sparse-MoE (nvidia/Qwen3.6-35B-A3B-NVFP4, ModelOpt v0.44.0). Autoregressive base line (no drafter). c64 point of the beyond-c32 ceiling-finding extension.
source_repo: nvidia/Qwen3.6-35B-A3B-NVFP4
download_url: https://huggingface.co/nvidia/Qwen3.6-35B-A3B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 64
tags: [qwen3.6-35b-a3b, Alibaba, Qwen, NVFP4, 16-40B, Spark recipe, conc-64]
status: done
prefill_toks: 564.58
decode_toks: 547.89
mem_gb: 106.26
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85), no drafter; ~12.3 GB free at peak
measured_on: 2026-07-04
completed_at: 2026-07-04 13:41 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:68e23ddd982ad5642e21354c2242a3a86d31a3ea83f5937e5c3867942dc6595b
run_command: |
  # Run under scripts/mem-watchdog.sh (floor 3.5 GB) — GB10 unified memory; see notes/BENCHMARKING.md.
  VLLM_IMAGE=vllm/vllm-openai@sha256:68e23ddd982ad5642e21354c2242a3a86d31a3ea83f5937e5c3867942dc6595b \
  scripts/bench-vllm-serving.sh nvidia/Qwen3.6-35B-A3B-NVFP4 65536 64 1000 900 256 \
    --quantization modelopt --trust-remote-code --reasoning-parser qwen3
  # 1000/1000 prompts (clean full run), 0 errors, 466.8s. ready after 422s. req thr 2.142/s. Watchdog no trip (12.3 GB free).
  # TPOT median 0.0 / TTFT median 27.2s = qwen3 reasoning-parser client artifacts — trust aggregate decode tok/s.
---

**Decode 547.89 tok/s aggregate at concurrency 64.** Autoregressive NVFP4 MoE base (no drafter), first point of the beyond-c32 ceiling-finding sweep (context held at 65536; splices onto the c1–c32 curve).

- **Still climbing:** decode **547.89 tok/s** vs the c32 base point (430.76) = **1.27× per doubling** — close to MTP's c32→c64 (1.24×). Note base c64 (547.89) ≈ MTP c32 (541.26): the added concurrency roughly buys what the drafter bought at lower batch.
- **Roomiest of the Qwen lines:** peak **106.26 GB delta = ~12.3 GB free** — no draft head/buffers, so ~3.6 GB more headroom than qwen-mtp c64 (~8.7 GB free). Watchdog (floor 3.5 GB) armed, did not trip.
- **Image (pinned):** `vllm/vllm-openai@sha256:68e23dd…` — same image as the c1–c32 Qwen cells. Ready after 422 s.
- **Workload:** ShareGPT V3, concurrency 64. **1000/1000, 0 errors** in **466.8 s** (no time cap). TPOT/TTFT medians are the usual `qwen3` reasoning-parser client artifacts.
</content>
</invoke>
