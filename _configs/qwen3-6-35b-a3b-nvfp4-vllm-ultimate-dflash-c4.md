---
title: Qwen3.6-35B-A3B · vLLM-ultimate (AEON) · NVFP4 + DFlash · conc 4
model: nvidia/Qwen3.6-35B-A3B-NVFP4
company: Alibaba
family: Qwen
params: 35B / 3B (MoE, hybrid GDN+full-attn) + DFlash external drafter
engine: vLLM (aeon-vllm-ultimate custom container, v0.23.0+aeon.sm121a.dflash)
speculative: DFlash (z-lab/Qwen3.6-35B-A3B-DFlash @31977fbe small-page rev, num_speculative_tokens 11)
quant: NVFP4 (modelopt_mixed — W4A16_NVFP4 experts + FP8 GDN gates)
quant_rationale: conc-4 fine-grained point of the DFlash money-chart line, tracing the shallow-loss plateau between the 1→2 crossover and the conc-16/32 collapse. REVISED 2026-07-02 — re-run at ctx 65536 (was 40960) as part of the full ctx-matched six-point re-sweep. Same one-boot protocol (official checkpoint, small-page drafter, max-num-seqs 64). SAFETY — untrusted third-party image; NO credentials, weights + drafter READ-ONLY, port loopback-only.
source_repo: nvidia/Qwen3.6-35B-A3B-NVFP4
download_url: https://huggingface.co/nvidia/Qwen3.6-35B-A3B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 4
tags: [qwen3.6-35b-a3b, Alibaba, Qwen, NVFP4, 16-40B, Spark recipe, conc-4]
status: done
prefill_toks: 193.44
decode_toks: 210.73
mem_gb: 111.3
mem_source: system MemAvailable delta (idle baseline 118 GiB → 6.7 GiB available at load) over the one-boot conc-1/2/4/8/16/32 sweep — vLLM static KV (util 0.85) + DFlash drafter
spec_acceptance: mean acceptance length ~3.92 (range 2.67–4.62, n=60 samples) · avg draft acceptance ~26.5% (range 15.2–32.9%) · per-position 0.773/0.557/0.406/0.307/0.234/0.180/0.140/0.110/0.086/0.068/0.054
measured_on: 2026-07-02
completed_at: 2026-07-02 07:21 +0800
engine_image: ghcr.io/aeon-7/aeon-vllm-ultimate@sha256:be9e05a11da6e72607ab6f3e960993b253b673af0727005122a3266129a518e3
run_command: |
  # UNTRUSTED image — NO creds; weights + drafter READ-ONLY; loopback port. ONE boot (ctx 65536,
  # max-num-seqs 64, small-page drafter @31977fbe) sweeping client conc 1/2/4/8/16/32 — see the main
  # (c1) page for the full docker run command. Only the client --concurrency differs.
  python3 scripts/bench-serving.py --base-url http://127.0.0.1:8000 --model official \
    --dataset benchmark_data/ShareGPT_V3_unfiltered_cleaned_split.json --concurrency 4 --num-prompts 1000 --max-seconds 600 --max-tokens 256
  # 499/1000 prompts (hit 600 s cap), 0 errors.
---

**conc-4 point of the Qwen3.6-35B-A3B NVFP4 + DFlash line — REVISED 2026-07-02, now ctx-matched to
MTP/base (65536).** Official `nvidia/Qwen3.6-35B-A3B-NVFP4` on the AEON image, DFlash n=11 via the
small-page drafter, one-boot sweep. **0 errors.**

- **Result (conc 4):** prefill 193.44 / decode **210.73** tok/s aggregate; 499/1000 prompts (hit the 600 s
  cap), **0 errors**. **vs MTP conc-4 (232.43): −9.3%.**
- **The shallow-loss plateau, slightly steeper once ctx-matched.** Across the ctx-matched sweep DFlash sits
  ~−6 to −12% behind MTP through conc 2/4/8 (−6.1% / −9.3% / −12.0%) — a modest but now monotonically
  widening loss, not the flatter ~−7-8% plateau the old ctx-40960 numbers showed — before the batch-fill
  collapse at conc-16 (−21.5%) and conc-32 (−24.8%). So the DFlash penalty is closer to smooth-then-cliff
  than flat-then-cliff once context is controlled.
- **Why — wasted draft compute.** DFlash drafts **11** at **~26.5% acceptance / accept-len ~3.92** (~7
  wasted forward passes/step); MTP drafts 3 at ~67% / accept-len 3.0. On this compute-bound MoE the extra
  draft work already dominates by conc-2 and worsens as streams divide the GPU. Acceptance flat vs conc
  (workload-driven) — matches c1 (26.8%) and c2 (26.7%) within noise.
- One server lifetime for the whole six-point sweep → mem is the single ~111.3 GB reservation. TPOT 0.0 =
  `qwen3` reasoning-parser client artifact.
- Series: [`c1` (main)]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash/) ·
  [`c2`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash-c2/) ·
  [`c8`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash-c8/) ·
  [`c16`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash-c16/) ·
  [`c32`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash-c32/). Matched MTP:
  [`-mtp-c4`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-mtp-c4/).
