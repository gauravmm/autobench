---
title: Qwen3.6-35B-A3B · vLLM-ultimate (AEON) · NVFP4 + DFlash · conc 32
model: nvidia/Qwen3.6-35B-A3B-NVFP4
company: Alibaba
family: Qwen
params: 35B / 3B (MoE, hybrid GDN+full-attn) + DFlash external drafter
engine: vLLM (aeon-vllm-ultimate custom container, v0.23.0+aeon.sm121a.dflash)
speculative: DFlash (z-lab/Qwen3.6-35B-A3B-DFlash @31977fbe small-page rev, num_speculative_tokens 11)
quant: NVFP4 (modelopt_mixed — W4A16_NVFP4 experts + FP8 GDN gates)
quant_rationale: conc-32 point of the ctx-matched (65536) DFlash money-chart sweep — the last, highest-batch endpoint (2026-07-02). Completes the six-point line matched exactly to base/MTP context. Same one-boot protocol (official checkpoint, small-page drafter, max-num-seqs 64). SAFETY — untrusted third-party image; NO credentials, weights + drafter READ-ONLY, port loopback-only.
source_repo: nvidia/Qwen3.6-35B-A3B-NVFP4
download_url: https://huggingface.co/nvidia/Qwen3.6-35B-A3B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 32
tags: [qwen3.6-35b-a3b, Alibaba, Qwen, NVFP4, 16-40B, Spark recipe, conc-32]
status: done
prefill_toks: 406.34
decode_toks: 407.07
mem_gb: 111.3
mem_source: system MemAvailable delta (idle baseline 118 GiB → 6.7 GiB available at load) over the one-boot conc-1/2/4/8/16/32 sweep — vLLM static KV (util 0.85) + DFlash drafter
spec_acceptance: mean acceptance length ~3.87 (range 3.31–5.86, n=61 samples) · avg draft acceptance ~26.1% (range 21.0–44.2%) · per-position 0.770/0.551/0.398/0.299/0.228/0.177/0.138/0.107/0.085/0.068/0.053
measured_on: 2026-07-02
completed_at: 2026-07-02 07:21 +0800
engine_image: ghcr.io/aeon-7/aeon-vllm-ultimate@sha256:be9e05a11da6e72607ab6f3e960993b253b673af0727005122a3266129a518e3
run_command: |
  # UNTRUSTED image — NO creds; weights + drafter READ-ONLY; loopback port. ONE boot (ctx 65536,
  # max-num-seqs 64, small-page drafter @31977fbe) sweeping client conc 1/2/4/8/16/32 — see the main
  # (c1) page for the full docker run command. Only the client --concurrency differs.
  python3 scripts/bench-serving.py --base-url http://127.0.0.1:8000 --model official \
    --dataset benchmark_data/ShareGPT_V3_unfiltered_cleaned_split.json --concurrency 32 --num-prompts 1000 --max-seconds 600 --max-tokens 256
  # 979/1000 prompts (hit 600 s cap), 0 errors.
---

**conc-32 point of the Qwen3.6-35B-A3B NVFP4 + DFlash line — NEW page, completes the ctx-matched
(65536) six-point sweep.** Official `nvidia/Qwen3.6-35B-A3B-NVFP4` on the AEON image, DFlash n=11 via
the small-page drafter, one-boot sweep. **0 errors.**

- **Result (conc 32):** prefill 406.34 / decode **407.07** tok/s aggregate; 979/1000 prompts (nearly full
  coverage, 600 s cap), **0 errors**. **vs MTP conc-32 (541.26): −24.8%.**
- **The DFlash money chart is now a fully-sampled, fully ctx-matched curve.** Six points, one boot, one
  context (65536), one client protocol: decode 99.76 (c1) → 151.3 (c2) → 210.7 (c4) → 267.4 (c8) →
  340.2 (c16) → **407.1 (c32)**; vs MTP: +0.7% → −6.1% → −9.3% → −12.0% → −21.5% → **−24.8%**. This is
  within 1.5% of the old ctx-40960 conc-32 reading (401.2, −25.9% vs the same MTP baseline) — at this
  batch size the extra 24576 tokens of context barely move the needle; the compute-bound collapse is a
  genuine property of the draft, not a context artifact. The only real correction from the ctx fix is at
  the *low* end: **DFlash's conc-1 "win" was entirely a context-length artifact — matched, it's a wash.**
- **Why — wasted draft compute.** DFlash drafts **11** at **~26.1% acceptance / accept-len ~3.87** vs MTP's
  3 at ~67% / 3.0 — ≈7 wasted drafter forward passes per step. At conc-32 those wasted passes compete
  directly with real decode work for every available GPU cycle, and DFlash falls furthest behind MTP here.
  Acceptance stays flat vs conc across the whole sweep (~26–27% throughout, workload-driven) — the collapse
  is pure draft-efficiency economics, not an acceptance drop under load.
- **Bottom line, footnote removed:** the money chart's DFlash line is now complete and matched to base/MTP
  at every point (context 65536, one client protocol, one boot). **Native MTP wins at every concurrency**
  — DFlash ties at best (c1) and loses increasingly from c2 onward. Keep MTP for any mixed-workload gateway
  on this hybrid-GDN 35B-A3B target.
- One server lifetime for the whole six-point sweep → mem is the single ~111.3 GB reservation. TPOT 0.0 =
  `qwen3` reasoning-parser client artifact.
- Series: [`c1` (main)]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash/) ·
  [`c2`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash-c2/) ·
  [`c4`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash-c4/) ·
  [`c8`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash-c8/) ·
  [`c16`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash-c16/). Matched MTP:
  [`-mtp`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-mtp/) (the no-suffix MTP page is conc-32).
