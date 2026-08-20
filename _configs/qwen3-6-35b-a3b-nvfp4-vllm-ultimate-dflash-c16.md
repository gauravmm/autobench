---
title: Qwen3.6-35B-A3B · vLLM-ultimate (AEON) · NVFP4 + DFlash · conc 16
model: nvidia/Qwen3.6-35B-A3B-NVFP4
company: Alibaba
family: Qwen
params: 35B / 3B (MoE, hybrid GDN+full-attn) + DFlash external drafter
engine: vLLM (aeon-vllm-ultimate custom container, v0.23.0+aeon.sm121a.dflash)
speculative: DFlash (z-lab/Qwen3.6-35B-A3B-DFlash @31977fbe small-page rev, num_speculative_tokens 11)
quant: NVFP4 (modelopt_mixed — W4A16_NVFP4 experts + FP8 GDN gates)
quant_rationale: conc-16 fine-grained point of the DFlash money-chart line, tracing the 8→32 batch-fill collapse where DFlash's wasted draft compute sinks aggregate throughput. REVISED 2026-07-02 — re-run at ctx 65536 (was 40960) as part of the full ctx-matched six-point re-sweep. Same one-boot protocol (official checkpoint, small-page drafter, max-num-seqs 64). SAFETY — untrusted third-party image; NO credentials, weights + drafter READ-ONLY, port loopback-only.
source_repo: nvidia/Qwen3.6-35B-A3B-NVFP4
download_url: https://huggingface.co/nvidia/Qwen3.6-35B-A3B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 16
tags: [qwen3.6-35b-a3b, Alibaba, Qwen, NVFP4, 16-40B, Spark recipe, conc-16]
status: done
prefill_toks: 355.12
decode_toks: 340.2
mem_gb: 111.3
mem_source: system MemAvailable delta (idle baseline 118 GiB → 6.7 GiB available at load) over the one-boot conc-1/2/4/8/16/32 sweep — vLLM static KV (util 0.85) + DFlash drafter
spec_acceptance: mean acceptance length ~3.86 (range 3.09–5.69, n=60 samples) · avg draft acceptance ~26.0% (range 19.0–42.7%) · per-position 0.766/0.547/0.398/0.298/0.226/0.175/0.137/0.106/0.084/0.067/0.053
measured_on: 2026-07-02
completed_at: 2026-07-02 07:21 +0800
engine_image: ghcr.io/aeon-7/aeon-vllm-ultimate@sha256:be9e05a11da6e72607ab6f3e960993b253b673af0727005122a3266129a518e3
run_command: |
  # UNTRUSTED image — NO creds; weights + drafter READ-ONLY; loopback port. ONE boot (ctx 65536,
  # max-num-seqs 64, small-page drafter @31977fbe) sweeping client conc 1/2/4/8/16/32 — see the main
  # (c1) page for the full docker run command. Only the client --concurrency differs.
  python3 scripts/bench-serving.py --base-url http://127.0.0.1:8000 --model official \
    --dataset benchmark_data/ShareGPT_V3_unfiltered_cleaned_split.json --concurrency 16 --num-prompts 1000 --max-seconds 600 --max-tokens 256
  # 810/1000 prompts (hit 600 s cap), 0 errors.
---

**conc-16 point of the Qwen3.6-35B-A3B NVFP4 + DFlash line — the batch-fill collapse, REVISED 2026-07-02
now ctx-matched to MTP/base (65536).** Official `nvidia/Qwen3.6-35B-A3B-NVFP4` on the AEON image, DFlash
n=11 via the small-page drafter, one-boot sweep. **0 errors.**

- **Result (conc 16):** prefill 355.12 / decode **340.2** tok/s aggregate; 810/1000 prompts (hit the 600 s
  cap), **0 errors**. **vs MTP conc-16 (433.28): −21.5%.**
- **The cliff, essentially unchanged by the ctx fix.** DFlash's loss vs MTP steepens from the shallow
  ~−6 to −12% plateau through conc-2/4/8 to **−21.5%** at conc-16, on toward −24.8% at conc-32. As the
  batch fills, the ~7 wasted drafter forward passes per step compete directly with real decode work on
  this compute-bound MoE, and aggregate throughput falls further behind MTP the more streams share the GPU.
  The absolute decode number (340.2) is within 1.2% of the old ctx-40960 run's 344.2 — at this batch size
  the KV-context difference barely mattered; the collapse is a genuine compute-bound effect, not a context
  artifact.
- **Why — wasted draft compute.** DFlash drafts **11** at **~26% acceptance / accept-len ~3.86** vs MTP's 3
  at ~67% / 3.0. Acceptance stays flat vs conc (workload-driven, matching every other point in this sweep
  within noise) — it's the *draft efficiency*, not a drop in acceptance, that drives the collapse.
- **Completes the ctx-matched DFlash money-chart line:** decode 99.76 (c1) → 151.3 (c2) → 210.7 (c4) →
  267.4 (c8) → **340.2 (c16)** → 407.1 (c32); vs MTP that's +0.7% → −6.1% → −9.3% → −12.0% → −21.5% → −24.8%.
  With context fully matched, DFlash's headline "conc-1 win" is a wash, not a lead — **the DFlash line never
  beats MTP at any concurrency** on this checkpoint. Cliff still lands at c16→c32. **Keep MTP** for a
  mixed-workload gateway — now with no context caveat.
- One server lifetime for the whole six-point sweep → mem is the single ~111.3 GB reservation. TPOT 0.0 =
  `qwen3` reasoning-parser client artifact.
- Series: [`c1` (main)]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash/) ·
  [`c2`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash-c2/) ·
  [`c4`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash-c4/) ·
  [`c8`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash-c8/) ·
  [`c32`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash-c32/). Matched MTP:
  [`-mtp-c16`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-mtp-c16/).
