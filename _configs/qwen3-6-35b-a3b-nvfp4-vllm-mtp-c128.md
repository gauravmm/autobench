---
title: Qwen3.6-35B-A3B · vLLM · NVFP4 + MTP · conc 128 (the knee)
model: Qwen/Qwen3.6-35B-A3B
company: Alibaba
family: Qwen
params: 35B / 3B (MoE)
engine: vLLM
speculative: MTP
quant: NVFP4
quant_rationale: NVIDIA's official NVFP4 (nvidia/Qwen3.6-35B-A3B-NVFP4, ModelOpt v0.44.0) + the checkpoint's own MTP module, NVIDIA DGX Spark recipe (marlin base + triton MTP head). c128 point of the beyond-c32 ceiling-finding extension — this is where the line plateaus.
source_repo: nvidia/Qwen3.6-35B-A3B-NVFP4
download_url: https://huggingface.co/nvidia/Qwen3.6-35B-A3B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 128
tags: [qwen3.6-35b-a3b, Alibaba, Qwen, NVFP4, 16-40B, Spark recipe, conc-128]
status: done
prefill_toks: 773.19
decode_toks: 749.92
mem_gb: 114.15
mem_source: system MemAvailable delta (10s sampling) — NVFP4 MoE + in-repo MTP head; only ~4.5 GB free at peak (util 0.85, near the 121 GB ceiling)
spec_acceptance: mean acceptance length 2.99 (2.90-3.10) · avg draft acceptance ~66% (63-70%) · per-position 0.84/0.66/0.51
measured_on: 2026-07-04
completed_at: 2026-07-04 12:31 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:68e23ddd982ad5642e21354c2242a3a86d31a3ea83f5937e5c3867942dc6595b
run_command: |
  # Run under scripts/mem-watchdog.sh — GB10 unified memory. NOTE: a first attempt at floor 6 GB tripped
  # protectively at 5.95 GB free (premature — the run stabilises at ~4.5 GB); re-run at floor 3.5 GB
  # (below gemma c128's demonstrated-safe ~4 GB, above the ~0 crash zone) completed clean. util held 0.85.
  VLLM_IMAGE=vllm/vllm-openai@sha256:68e23ddd982ad5642e21354c2242a3a86d31a3ea83f5937e5c3867942dc6595b \
  scripts/bench-vllm-serving.sh nvidia/Qwen3.6-35B-A3B-NVFP4 65536 128 1000 900 256 \
    --quantization modelopt --trust-remote-code --reasoning-parser qwen3 --moe-backend marlin \
    --speculative-config '{"method":"mtp","num_speculative_tokens":3,"moe_backend":"triton"}'
  # 1000/1000 prompts (clean full run), 0 errors, 340.9s. ready after 374s. req thr 2.934/s. ~4.5 GB free at peak.
  # SpecDecoding: mean acceptance length 2.99 · avg draft acceptance ~66% · per-position 0.84/0.66/0.51.
---

**Decode 749.92 tok/s aggregate at concurrency 128 — this is the knee for the Qwen 35B-A3B MTP line.** NVFP4 MoE + native MTP, second point of the beyond-c32 ceiling-finding sweep (context held at 65536, util 0.85, splices onto the c1–c32 curve).

- **Compute has plateaued:** decode **749.92 tok/s** vs c64 (670.82) = **1.118× per doubling** — right at the ~1.1× plateau threshold (the stopping rule for this sweep). The chain 541 → 671 (1.24×) → 750 (1.12×) shows the 35B-A3B line flattening by c128, unlike gemma-4 26B-A4B which was still at 1.34× here. **c128 is the practical top; c256 was not run** (compute is flat and memory is already tight).
- **Memory is also near the wall:** peak **114.15 GB delta = only ~4.5 GB free** against the 121 GB unified ceiling. A first attempt under the watchdog at a 6 GB floor **tripped protectively at 5.95 GB free** (SIGKILL, box safe); the re-run at a 3.5 GB floor — below gemma-4 c128's demonstrated-safe ~4 GB and above the ~0 crash zone — completed cleanly with 0 errors. So both walls (compute plateau + memory) converge on c128 as the top.
- **Acceptance healthy and flat:** mean acceptance length **2.99**, avg draft acceptance **~66%**, per-position **0.84/0.66/0.51** — identical to c1–c64, confirming draft quality is workload-driven not concurrency-driven; the plateau is throughput economics, not a draft collapse.
- **Image (pinned):** `vllm/vllm-openai@sha256:68e23dd…` — same image as the c1–c64 Qwen cells. Ready after 374 s.
- **Workload:** ShareGPT V3, concurrency 128. **1000/1000, 0 errors** in **340.9 s** (no time cap). TPOT/TTFT medians are the usual `qwen3` reasoning-parser client artifacts.
</content>
</invoke>
