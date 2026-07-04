---
title: Qwen3.6-35B-A3B · vLLM-ultimate (AEON) · NVFP4 + DFlash · conc 128 (memory ceiling — watchdog trip)
model: nvidia/Qwen3.6-35B-A3B-NVFP4
company: Alibaba
family: Qwen
params: 35B / 3B (MoE, hybrid GDN+full-attn) + DFlash external drafter
engine: vLLM (aeon-vllm-ultimate custom container, v0.23.0+aeon.sm121a.dflash)
speculative: DFlash (z-lab/Qwen3.6-35B-A3B-DFlash @31977fbe small-page rev, num_speculative_tokens 11)
quant: NVFP4 (modelopt_mixed — W4A16_NVFP4 experts + FP8 GDN gates)
quant_rationale: c128 point of the beyond-c32 ceiling-finding extension of the DFlash line — this run FOUND the DFlash memory ceiling (watchdog trip at 3.50 GB free). Same one-boot (max-num-seqs 128, ctx 65536) as the c64 point. SAFETY — untrusted third-party image; NO credentials, weights + drafter READ-ONLY, port loopback-only. Under scripts/mem-watchdog.sh (pattern aeon, floor 3.5 GB).
source_repo: nvidia/Qwen3.6-35B-A3B-NVFP4
download_url: https://huggingface.co/nvidia/Qwen3.6-35B-A3B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 128
tags: [qwen3.6-35b-a3b, Alibaba, Qwen, NVFP4, 16-40B, Spark recipe, conc-128]
status: done
prefill_toks: 389.6
decode_toks: 425.71
mem_gb: 115.2
mem_source: system MemAvailable delta — watchdog SIGKILLed at 3.50 GB free (~115 GB used); one-boot reservation at max-num-seqs 128 (util 0.85 + DFlash n=11 drafter)
spec_acceptance: mean acceptance length ~3.85 (3.74-4.11) · avg draft acceptance ~26% (25-28%) · per-position 0.78/0.55/0.40/0.30/0.23/0.17/0.13/0.10/0.08/0.06/0.05 (n=11)
measured_on: 2026-07-04
completed_at: 2026-07-04 14:17 +0800
engine_image: ghcr.io/aeon-7/aeon-vllm-ultimate@sha256:be9e05a11da6e72607ab6f3e960993b253b673af0727005122a3266129a518e3
run_command: |
  # UNTRUSTED image — NO creds; weights + drafter READ-ONLY; loopback port. Same one-boot as c64
  # (max-num-seqs 128, ctx 65536). Under mem-watchdog (pattern aeon, floor 3.5 GB).
  # WATCHDOG TRIPPED at MemAvailable=3.50 GB → SIGKILL, box safe. 668/1000 completed, 332 errors.
  python3 scripts/bench-serving.py --base-url http://127.0.0.1:8000 --model official \
    --dataset benchmark_data/ShareGPT_V3_unfiltered_cleaned_split.json --concurrency 128 --num-prompts 1000 --max-seconds 900 --max-tokens 256
---

**c128 is the DFlash line's ceiling — and it's a double ceiling: already compute-plateaued at c64, now memory-capped at c128.** Not a clean throughput point (watchdog killed it at 668/1000). Context held at 65536, one-boot with c64.

- **Memory wall, caught by the watchdog:** during the c128 client run free headroom fell to **3.50 GB** (~115 GB used) — the 3.5 GB floor — and `scripts/mem-watchdog.sh` (pattern `aeon`) SIGKILLed the container. **668/1000 completed, 332 errored**; machine stayed up. The DFlash n=11 drafter carries a large per-seq draft state, so at max-num-seqs 128 it exhausts the pool where MTP (3 draft tokens) still had ~4.5 GB.
- **No throughput to gain anyway:** the partial decode reading (**425.71 tok/s**, contaminated by the kill) is essentially flat vs c64 (420.35) — **~1.0× per doubling**. DFlash was already compute-saturated at c64 (1.03×); c128 adds nothing but memory pressure. Contrast MTP, which climbed to 750 tok/s at c128 in ~4.5 GB.
- **Acceptance unchanged ~26%** (mean accept-len ~3.85-of-11, per-position 0.78/0.55/0.40/0.30/…/0.05) — flat across the whole c1→c128 DFlash sweep, workload-driven. The ceiling is draft-efficiency economics + drafter memory, never draft quality.
- **Bottom line for the post:** across the full extended ladder DFlash **tops out first and lowest** of the six lines — plateaus by c64 and can't hold c128 in memory — while native MTP keeps climbing to c128 in a fraction of the memory. Stay on native MTP.
- **Image (UNTRUSTED, pinned):** `ghcr.io/aeon-7/aeon-vllm-ultimate@sha256:be9e05a1…`, NO creds, read-only mounts, loopback port.
- Series: [`c1`](qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash) … [`c32`](qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash-c32) · [`c64`](qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash-c64) · matched MTP [`-mtp-c128`](qwen3-6-35b-a3b-nvfp4-vllm-mtp-c128).
</content>
</invoke>
