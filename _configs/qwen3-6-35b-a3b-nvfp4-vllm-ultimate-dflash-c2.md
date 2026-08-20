---
title: Qwen3.6-35B-A3B · vLLM-ultimate (AEON) · NVFP4 + DFlash · conc 2
model: nvidia/Qwen3.6-35B-A3B-NVFP4
company: Alibaba
family: Qwen
params: 35B / 3B (MoE, hybrid GDN+full-attn) + DFlash external drafter
engine: vLLM (aeon-vllm-ultimate custom container, v0.23.0+aeon.sm121a.dflash)
speculative: DFlash (z-lab/Qwen3.6-35B-A3B-DFlash @31977fbe small-page rev, num_speculative_tokens 11)
quant: NVFP4 (modelopt_mixed — W4A16_NVFP4 experts + FP8 GDN gates)
quant_rationale: conc-2 fine-grained point of the DFlash money-chart line. REVISED 2026-07-02 — re-run at ctx 65536 (was 40960) as part of the full ctx-matched six-point re-sweep, removing the context confound vs the matched MTP series. Same one-boot protocol (official checkpoint, small-page drafter, max-num-seqs 64). SAFETY — untrusted third-party image; run with NO credentials, official weights + drafter READ-ONLY, port loopback-only.
source_repo: nvidia/Qwen3.6-35B-A3B-NVFP4
download_url: https://huggingface.co/nvidia/Qwen3.6-35B-A3B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 2
tags: [qwen3.6-35b-a3b, Alibaba, Qwen, NVFP4, 16-40B, Spark recipe, conc-2]
status: done
prefill_toks: 168.05
decode_toks: 151.3
mem_gb: 111.3
mem_source: system MemAvailable delta (idle baseline 118 GiB → 6.7 GiB available at load) over the one-boot conc-1/2/4/8/16/32 sweep — vLLM static KV (util 0.85) + DFlash drafter
spec_acceptance: mean acceptance length ~3.94 (range 3.25–4.79, n=59 samples) · avg draft acceptance ~26.7% (range 20.5–34.4%) · per-position 0.788/0.559/0.409/0.309/0.239/0.184/0.139/0.107/0.085/0.067/0.052
measured_on: 2026-07-02
completed_at: 2026-07-02 07:21 +0800
engine_image: ghcr.io/aeon-7/aeon-vllm-ultimate@sha256:be9e05a11da6e72607ab6f3e960993b253b673af0727005122a3266129a518e3
run_command: |
  # UNTRUSTED image — NO creds; official weights + drafter READ-ONLY; loopback port. ONE boot (ctx 65536,
  # max-num-seqs 64, small-page drafter @31977fbe) sweeping client conc 1/2/4/8/16/32 — see the main
  # (c1) page for the full docker run command. Only the client --concurrency differs.
  python3 scripts/bench-serving.py --base-url http://127.0.0.1:8000 --model official \
    --dataset benchmark_data/ShareGPT_V3_unfiltered_cleaned_split.json --concurrency 2 --num-prompts 1000 --max-seconds 600 --max-tokens 256
  # 356/1000 prompts (hit 600 s cap), 0 errors.
---

**conc-2 point of the Qwen3.6-35B-A3B NVFP4 + DFlash line — REVISED 2026-07-02, now ctx-matched to
MTP/base (65536).** Official `nvidia/Qwen3.6-35B-A3B-NVFP4` on the AEON image, DFlash n=11 via the
small-page drafter, one-boot sweep. **0 errors.**

- **Result (conc 2):** prefill 168.05 / decode **151.3** tok/s aggregate; 356/1000 prompts (hit the 600 s
  cap), **0 errors**. **vs MTP conc-2 (161.21): −6.1%.**
- **The crossover is already behind by conc-2, ctx-matched.** DFlash's conc-1 point is now a wash (+0.7%
  vs matched-cap MTP — see [`c1` (main)]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash/)), so the sign flip
  effectively happens *at* conc-1→2 rather than DFlash holding a real lead first. The old ctx-40960
  measurement (147.61 decode, same absolute number as this run within noise) read −8.4% against the same
  MTP baseline — the ctx fix barely moved this point (−8.4% → −6.1%), confirming most of the c2 loss was
  real, not a context artifact.
- **Why — wasted draft compute.** DFlash drafts **11** tokens at only **~27% acceptance / accept-len ~3.94**
  → ~7 wasted drafter forward passes per step. Even at conc-2 that extra compute already outweighs the
  bandwidth saving; MTP's 3-token / ~67%-accept / accept-len-3.0 draft has almost no waste. Acceptance is
  workload-driven (flat vs conc — matches c1's 26.8% almost exactly).
- One server lifetime for the whole six-point sweep → mem is the single ~111.3 GB reservation
  (max-num-seqs 64). TPOT 0.0 is the `qwen3` reasoning-parser client artifact — decode tok/s is the real
  number.
- Series: [`c1` (main)]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash/) ·
  [`c4`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash-c4/) ·
  [`c8`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash-c8/) ·
  [`c16`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash-c16/) ·
  [`c32`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash-c32/). Matched MTP:
  [`-mtp-c2`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-mtp-c2/).
