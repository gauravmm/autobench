---
title: Qwen3.6-35B-A3B · vLLM-ultimate (AEON) · NVFP4 + DFlash · conc 8
model: nvidia/Qwen3.6-35B-A3B-NVFP4
company: Alibaba
family: Qwen
params: 35B / 3B (MoE, hybrid GDN+full-attn) + DFlash external drafter
engine: vLLM (aeon-vllm-ultimate custom container, v0.23.0+aeon.sm121a.dflash)
speculative: DFlash (z-lab/Qwen3.6-35B-A3B-DFlash @31977fbe small-page rev, num_speculative_tokens 11)
quant: NVFP4 (modelopt_mixed — W4A16_NVFP4 experts + FP8 GDN gates)
quant_rationale: conc-8 point of the ctx-matched (65536) DFlash money-chart sweep — new endpoint (2026-07-02), the original series only sampled c1/c8/c32 with c8 at ctx 40960 embedded in the main page's table, not as its own config page. This standalone page + the ctx-65536 re-run of c1/c2/c4/c16 together give a single fully-matched six-point line. Same one-boot protocol (official checkpoint, small-page drafter, max-num-seqs 64). SAFETY — untrusted third-party image; NO credentials, weights + drafter READ-ONLY, port loopback-only.
source_repo: nvidia/Qwen3.6-35B-A3B-NVFP4
download_url: https://huggingface.co/nvidia/Qwen3.6-35B-A3B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 8
tags: [qwen3.6-35b-a3b, Alibaba, Qwen, NVFP4, 16-40B, Spark recipe, conc-8]
status: done
prefill_toks: 273.06
decode_toks: 267.43
mem_gb: 111.3
mem_source: system MemAvailable delta (idle baseline 118 GiB → 6.7 GiB available at load) over the one-boot conc-1/2/4/8/16/32 sweep — vLLM static KV (util 0.85) + DFlash drafter
spec_acceptance: mean acceptance length ~3.82 (range 2.73–4.53, n=62 samples) · avg draft acceptance ~25.6% (range 15.8–32.1%) · per-position 0.752/0.544/0.393/0.294/0.225/0.174/0.136/0.105/0.081/0.064/0.051
measured_on: 2026-07-02
completed_at: 2026-07-02 07:21 +0800
engine_image: ghcr.io/aeon-7/aeon-vllm-ultimate@sha256:be9e05a11da6e72607ab6f3e960993b253b673af0727005122a3266129a518e3
run_command: |
  # UNTRUSTED image — NO creds; weights + drafter READ-ONLY; loopback port. ONE boot (ctx 65536,
  # max-num-seqs 64, small-page drafter @31977fbe) sweeping client conc 1/2/4/8/16/32 — see the main
  # (c1) page for the full docker run command. Only the client --concurrency differs.
  python3 scripts/bench-serving.py --base-url http://127.0.0.1:8000 --model official \
    --dataset benchmark_data/ShareGPT_V3_unfiltered_cleaned_split.json --concurrency 8 --num-prompts 1000 --max-seconds 600 --max-tokens 256
  # 633/1000 prompts (hit 600 s cap), 0 errors.
---

**conc-8 point of the Qwen3.6-35B-A3B NVFP4 + DFlash line — NEW page, ctx-matched to MTP/base (65536).**
Official `nvidia/Qwen3.6-35B-A3B-NVFP4` on the AEON image, DFlash n=11 via the small-page drafter,
one-boot sweep across conc 1/2/4/8/16/32. **0 errors.**

- **Result (conc 8):** prefill 273.06 / decode **267.43** tok/s aggregate; 633/1000 prompts (hit the 600 s
  cap), **0 errors**. **vs matched-cap MTP conc-8 (304.0, [`-mtp-c8`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-mtp-c8/)):
  −12.0%.**
- **Sits at the bottom of the shallow-loss zone before the c16 cliff.** The ctx-matched sweep now reads
  +0.7% (c1) → −6.1% (c2) → −9.3% (c4) → **−12.0% (c8)** → −21.5% (c16) → −24.8% (c32) — a smooth widening
  loss through c8 rather than a flat plateau, then the sharp step down at c16. This c8 point didn't exist
  as a separate page before (the original series folded c8 into the main c1/8/32 page at ctx 40960,
  269.9 tok/s, compared against the *short-cap* MTP c8 of 289.14 for −6.6% — this page uses the matched
  600 s-cap MTP recheck of 304.0 instead, which is why the delta widens to −12.0%).
- **Why — wasted draft compute.** DFlash drafts **11** at **~25.6% acceptance / accept-len ~3.82** (~7
  wasted forward passes/step); MTP drafts 3 at ~67% / accept-len 3.0. On this compute-bound MoE the extra
  draft work compounds as concurrency rises. Acceptance flat vs conc (workload-driven) — matches c1/c2/c4
  (all ~26–27%) within noise.
- One server lifetime for the whole six-point sweep → mem is the single ~111.3 GB reservation. TPOT 0.0 =
  `qwen3` reasoning-parser client artifact.
- Series: [`c1` (main)]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash/) ·
  [`c2`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash-c2/) ·
  [`c4`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash-c4/) ·
  [`c16`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash-c16/) ·
  [`c32`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash-c32/). Matched MTP:
  [`-mtp-c8`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-mtp-c8/).
