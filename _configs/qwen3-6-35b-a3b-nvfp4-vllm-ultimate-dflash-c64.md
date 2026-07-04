---
title: Qwen3.6-35B-A3B · vLLM-ultimate (AEON) · NVFP4 + DFlash · conc 64
model: nvidia/Qwen3.6-35B-A3B-NVFP4
company: Alibaba
family: Qwen
params: 35B / 3B (MoE, hybrid GDN+full-attn) + DFlash external drafter
engine: vLLM (aeon-vllm-ultimate custom container, v0.23.0+aeon.sm121a.dflash)
speculative: DFlash (z-lab/Qwen3.6-35B-A3B-DFlash @31977fbe small-page rev, num_speculative_tokens 11)
quant: NVFP4 (modelopt_mixed — W4A16_NVFP4 experts + FP8 GDN gates)
quant_rationale: c64 point of the beyond-c32 ceiling-finding extension of the DFlash line. Fresh one-boot at max-num-seqs 128 (ctx 65536) sweeping client conc 64 then 128, to see where the wasted-draft-compute line tops out. SAFETY — untrusted third-party image; NO credentials, weights + drafter READ-ONLY, port loopback-only. Run under scripts/mem-watchdog.sh (pattern aeon, floor 3.5 GB).
source_repo: nvidia/Qwen3.6-35B-A3B-NVFP4
download_url: https://huggingface.co/nvidia/Qwen3.6-35B-A3B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 64
tags: [qwen3.6-35b-a3b, Alibaba, Qwen, NVFP4, 16-40B, Spark recipe, conc-64]
status: done
prefill_toks: 433.3
decode_toks: 420.35
mem_gb: 111.3
mem_source: system MemAvailable delta — single one-boot reservation at max-num-seqs 128 (util 0.85 + DFlash n=11 drafter); free headroom fell to ~4.1 GB by the c128 client run
spec_acceptance: avg draft acceptance ~26% · mean accept-len ~3.9-of-11 (consistent with the c1–c32 DFlash sweep; workload-driven, flat across concurrency)
measured_on: 2026-07-04
completed_at: 2026-07-04 14:11 +0800
engine_image: ghcr.io/aeon-7/aeon-vllm-ultimate@sha256:be9e05a11da6e72607ab6f3e960993b253b673af0727005122a3266129a518e3
run_command: |
  # UNTRUSTED image — NO creds; weights + drafter READ-ONLY; loopback port. ONE boot (ctx 65536,
  # max-num-seqs 128, small-page drafter @31977fbe) sweeping client conc 64 then 128. Under mem-watchdog
  # (pattern aeon, floor 3.5 GB). See the c1 page for the full docker run; only max-num-seqs (64→128)
  # and the client --concurrency differ.
  python3 scripts/bench-serving.py --base-url http://127.0.0.1:8000 --model official \
    --dataset benchmark_data/ShareGPT_V3_unfiltered_cleaned_split.json --concurrency 64 --num-prompts 1000 --max-seconds 900 --max-tokens 256
  # 1000/1000 prompts, 0 errors, 608.2s. ready after 342s. req thr 1.644/s. TPOT 0.0 = qwen3 reasoning-parser artifact.
---

**Decode 420.35 tok/s at concurrency 64 — DFlash has already flat-lined.** Official `nvidia/Qwen3.6-35B-A3B-NVFP4` on the AEON image, DFlash n=11 via the small-page drafter, one-boot sweep (context held at 65536, splices onto the c1–c32 DFlash line).

- **The DFlash line tops out earliest of all six:** decode **420.35 tok/s** vs the c32 DFlash point (407.07) = **just 1.03× per doubling** — already below the ~1.1× plateau threshold at c64, while base (1.62×), MTP (1.24×) and EAGLE3 (1.49×) were all still climbing hard here. **DFlash is compute-saturated by c64.**
- **Why — wasted draft compute, exactly as at low batch.** DFlash drafts **11** tokens at **~26% acceptance** (accept-len ~3.9); ≈7 of those forward passes are thrown away every step. At conc 64 those wasted passes compete directly with real decode for GPU cycles, so added concurrency buys almost no throughput. It is now **~1.6× slower than MTP at the same concurrency** (MTP c64 670.82 vs DFlash 420.35, −37%).
- **Slowest per-request too:** 608.2 s for 1000 prompts (req thr 1.644/s) vs base c64's 466.8 s (2.142/s) — the drafter overhead shows up as latency as well as ceiling.
- **Memory is tight at this max-num-seqs 128 boot:** the DFlash draft state is large, and by the c128 client run free headroom fell to **~4.1 GB** (util 0.85 + n=11 drafter). The [`mem-watchdog`](https://github.com/gauravmm/autobench) (pattern `aeon`, floor 3.5 GB) was armed throughout.
- **Image (UNTRUSTED, pinned):** `ghcr.io/aeon-7/aeon-vllm-ultimate@sha256:be9e05a1…`, run with NO creds, read-only weight+drafter mounts, loopback-only port. Ready after 342 s.
- Series: [`c1`](qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash) … [`c32`](qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash-c32) · matched MTP [`-mtp-c64`](qwen3-6-35b-a3b-nvfp4-vllm-mtp-c64).
</content>
</invoke>
