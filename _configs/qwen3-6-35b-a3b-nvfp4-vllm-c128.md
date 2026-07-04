---
title: Qwen3.6-35B-A3B · vLLM · NVFP4 · conc 128
model: Qwen/Qwen3.6-35B-A3B
company: Alibaba
family: Qwen
params: 35B / 3B (MoE)
engine: vLLM
quant: NVFP4
quant_rationale: NVIDIA's OFFICIAL NVFP4 of the Qwen3.6-35B-A3B sparse-MoE (nvidia/Qwen3.6-35B-A3B-NVFP4, ModelOpt v0.44.0). Autoregressive base line (no drafter). c128 point of the beyond-c32 ceiling-finding extension.
source_repo: nvidia/Qwen3.6-35B-A3B-NVFP4
download_url: https://huggingface.co/nvidia/Qwen3.6-35B-A3B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 128
tags: [qwen3.6-35b-a3b, Alibaba, Qwen, NVFP4, 16-40B, Spark recipe, conc-128]
status: done
prefill_toks: 696.3
decode_toks: 675.86
mem_gb: 108.94
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85), no drafter; ~9.7 GB free at peak
measured_on: 2026-07-04
completed_at: 2026-07-04 13:50 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:68e23ddd982ad5642e21354c2242a3a86d31a3ea83f5937e5c3867942dc6595b
run_command: |
  # Run under scripts/mem-watchdog.sh (floor 3.5 GB) — GB10 unified memory; see notes/BENCHMARKING.md.
  VLLM_IMAGE=vllm/vllm-openai@sha256:68e23ddd982ad5642e21354c2242a3a86d31a3ea83f5937e5c3867942dc6595b \
  scripts/bench-vllm-serving.sh nvidia/Qwen3.6-35B-A3B-NVFP4 65536 128 1000 900 256 \
    --quantization modelopt --trust-remote-code --reasoning-parser qwen3
  # 1000/1000 prompts (clean full run), 0 errors, 378.5s. ready after 361s. req thr 2.642/s. Watchdog no trip (9.7 GB free).
  # TPOT median 0.0 / TTFT median 45.4s = qwen3 reasoning-parser client artifacts — trust aggregate decode tok/s.
---

**Decode 675.86 tok/s aggregate at concurrency 128.** Autoregressive NVFP4 MoE base (no drafter), top of the beyond-c32 base sweep (context held at 65536).

- **Still mildly climbing:** decode **675.86 tok/s** vs c64 (547.89) = **1.23× per doubling** — unlike the MTP line (which plateaued to 1.12× here), the base line has NOT fully kneed at c128 and is memory-comfortable, so it has residual headroom (c256 unexplored for this line — capped at c128 per the sweep plan). Base c128 (676) essentially matches MTP c64 (671).
- **Memory-comfortable, no draft buffers:** peak **108.94 GB delta = ~9.7 GB free** — ~5 GB more headroom than qwen-mtp c128 (~4.5 GB). This is the base-vs-spec memory divergence: the MTP head's per-seq draft buffers eat headroom as concurrency rises; base does not. Watchdog (floor 3.5 GB) armed, did not trip.
- **Image (pinned):** `vllm/vllm-openai@sha256:68e23dd…` — same image as the c1–c64 Qwen cells. Ready after 361 s.
- **Workload:** ShareGPT V3, concurrency 128. **1000/1000, 0 errors** in **378.5 s** (no time cap). TPOT/TTFT medians are the usual `qwen3` reasoning-parser client artifacts.
</content>
</invoke>
