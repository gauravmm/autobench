---
title: Gemma 4 26B-A4B · vLLM · NVFP4 + EAGLE3 · conc 256 (memory ceiling — watchdog trip)
model: google/gemma-4-26B-A4B-it
company: Google
family: Gemma
params: 26B / 4B (MoE)
engine: vLLM
speculative: EAGLE3
quant: NVFP4
quant_rationale: NVIDIA NVFP4 base (modelopt) + RedHatAI's official EAGLE3 speculator. c256 point of the beyond-c32 ceiling-finding extension — this run FOUND the EAGLE3 line's memory ceiling (watchdog trip at 3.42 GB free).
source_repo: nvidia/Gemma-4-26B-A4B-NVFP4
download_url: https://huggingface.co/nvidia/Gemma-4-26B-A4B-NVFP4
context: 65536
modalities: [text, image]
mm_served: false
concurrency: 256
tags: [gemma-4-26b-a4b, Google, Gemma, NVFP4, 16-40B, conc-256]
status: done
prefill_toks: 6.41
decode_toks: 1.96
mem_gb: 117.9
mem_source: system MemAvailable delta — watchdog SIGKILLed at 3.42 GB free (117.9 GB used), i.e. the memory ceiling; wrapper 10s sampler had only reached 113.21 before the kill
spec_acceptance: n/a — killed 18 s into serving (memory ceiling), before a stable acceptance window
measured_on: 2026-07-04
completed_at: 2026-07-04 13:26 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:e414712fdc04f61d98ccc58cb61232a0587a8c024544e9e6cf12f97b19b38172
run_command: |
  # Run under scripts/mem-watchdog.sh (floor 3.5 GB). WATCHDOG TRIPPED at MemAvailable=3.42 GB (18 s into
  # serving) → SIGKILL, box safe. 259/1000 completed, 741 errors. This trip IS the memory ceiling.
  VLLM_IMAGE=vllm/vllm-openai:nightly-aarch64 scripts/bench-vllm-serving.sh nvidia/Gemma-4-26B-A4B-NVFP4 65536 256 1000 900 256 \
    --speculative-config '{"model":"RedHatAI/gemma-4-26B-A4B-it-speculator.eagle3","method":"eagle3","num_speculative_tokens":3}'
---

**c256 is the EAGLE3 line's ceiling — a memory wall, caught by the watchdog at 3.42 GB free.** Context held at 65536, same recipe as c1–c128. **Not a throughput point** — excluded from the curve; c128 (1210 tok/s) is the last healthy EAGLE3 reading.

- **What happened:** ~18 s into serving at conc 256, MemAvailable fell to **3.42 GB** (117.9 GB used) — below the 3.5 GB watchdog floor — and `scripts/mem-watchdog.sh` SIGKILLed the container. **259/1000 completed, 741 errored**; the machine stayed up. Without the watchdog this is exactly the allocation that hard-rebooted the box earlier in the session (qwen-mtp c64 cascade).
- **Same failure family as MTP c256, different trigger point:** both spec lines carry a growing per-seq **draft buffer** that scales with `--max-num-seqs`, so by c256 they exhaust the 121 GB pool (EAGLE3 tripped on memory at 3.42 GB free; MTP additionally hit the `max_num_scheduled_tokens=2496` scheduler throttle). **Base, which has no draft buffers, ran c256 clean at ~10 GB free (1366 tok/s).** That is the whole point of the extension: *the drafter's memory footprint — not compute — is what ends the spec lines' scaling on GB10.*
- **Practical top for the EAGLE3 line at 65536 ctx: c128.** To push further you would need a lower `--gpu-memory-utilization` (util-adjusted regime, doesn't splice onto the 0.85 curve) or a smaller context.
- **Image (pinned):** `vllm/vllm-openai:nightly-aarch64` @ `sha256:e414712fdc04…`. Ready after 296 s (load was fine — the wall is at serving time).
</content>
</invoke>
