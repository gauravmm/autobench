---
title: Qwen3.6-35B-A3B · vLLM-ultimate (AEON) · NVFP4 + DFlash · conc 1
model: nvidia/Qwen3.6-35B-A3B-NVFP4
company: Alibaba
family: Qwen
params: 35B / 3B (MoE, hybrid GDN+full-attn) + DFlash external drafter
engine: vLLM (aeon-vllm-ultimate custom container, v0.23.0+aeon.sm121a.dflash)
speculative: DFlash (z-lab/Qwen3.6-35B-A3B-DFlash @31977fbe small-page rev, num_speculative_tokens 11)
quant: NVFP4 (modelopt_mixed — W4A16_NVFP4 experts + FP8 GDN gates)
quant_rationale: The PRODUCTION checkpoint (the one llm.manek.sg actually serves) under DFlash spec-decode, to test whether the AEON DFlash win transfers off the abliterated heretic onto the official ModelOpt weights — and whether the FP8-quantized GDN gates nose-dive draft acceptance (Vassallo). Loaded the production way (`--quantization modelopt --moe-backend marlin`, NO `VLLM_TEST_FORCE_FP8_MARLIN` — that env crashes the FP8 dense layers via an `AttributeError` on `orig_dtype`). REVISED 2026-07-02 — re-run at ctx 65536 (was 40960) to match the base/MTP lines exactly, removing the context confound noted on the money chart. SAFETY — untrusted third-party image; run with NO credentials, official weights mounted READ-ONLY from the HF cache, drafter READ-ONLY, port loopback-only.
source_repo: nvidia/Qwen3.6-35B-A3B-NVFP4
download_url: https://huggingface.co/nvidia/Qwen3.6-35B-A3B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 1
tags: [qwen3.6-35b-a3b, Alibaba, Qwen, NVFP4, 16-40B, Spark recipe, conc-1]
status: done
prefill_toks: 140.82
decode_toks: 99.76
mem_gb: 111.3
mem_source: system MemAvailable delta (idle baseline 118 GiB → 6.7 GiB available at load) over the one-boot conc-1/2/4/8/16/32 sweep — vLLM static KV (util 0.85) + DFlash drafter
spec_acceptance: mean acceptance length ~3.95 (range 3.22–4.96) · avg draft acceptance ~26.8% (range 20.1–36.0%, n=56 samples) · per-position 0.782/0.568/0.413/0.307/0.234/0.182/0.144/0.112/0.087/0.068/0.052
measured_on: 2026-07-02
completed_at: 2026-07-02 07:21 +0800
engine_image: ghcr.io/aeon-7/aeon-vllm-ultimate@sha256:be9e05a11da6e72607ab6f3e960993b253b673af0727005122a3266129a518e3
run_command: |
  # UNTRUSTED image — NO creds; official weights + drafter READ-ONLY; loopback port. ONE boot (ctx 65536,
  # max-num-seqs 64, small-page drafter @31977fbe) sweeping client conc 1/2/4/8/16/32 — REVISED from the
  # original ctx-40960 run to match base/MTP context exactly.
  docker run -d --name aeon-dflash-65536 --gpus all --ipc=host \
    -e TORCH_CUDA_ARCH_LIST=12.1a -e ENABLE_NVFP4_SM100=0 \
    -e VLLM_ALLOW_LONG_MAX_MODEL_LEN=1 -e PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
    -v ~/.cache/huggingface/hub/models--nvidia--Qwen3.6-35B-A3B-NVFP4:/officialmodel:ro \
    -v ~/ornith/drafter-smallpage:/drafter:ro -p 127.0.0.1:8000:8000 \
    --entrypoint vllm ghcr.io/aeon-7/aeon-vllm-ultimate:2026-06-18-v0.23.0-dflashfix \
    serve /officialmodel/snapshots/491c2f1ea524c639598bf8fa787a93fed5a6fbce --served-model-name official --host 0.0.0.0 --port 8000 \
    --quantization modelopt --moe-backend marlin --trust-remote-code --attention-backend flash_attn \
    --reasoning-parser qwen3 --tool-call-parser qwen3_coder --enable-auto-tool-choice \
    --max-model-len 65536 --gpu-memory-utilization 0.85 --enable-chunked-prefill --enable-prefix-caching \
    --max-num-seqs 64 --max-num-batched-tokens 32768 \
    --speculative-config '{"method":"dflash","model":"/drafter","num_speculative_tokens":11}'
  python3 scripts/bench-serving.py --base-url http://127.0.0.1:8000 --model official \
    --dataset benchmark_data/ShareGPT_V3_unfiltered_cleaned_split.json --num-prompts 1000 --max-seconds 600 \
    --concurrency 1 --max-tokens 256
  # 234/1000 prompts (hit 600 s cap), 0 errors. TTFT median 2404.9 ms.
---

**conc-1 point of the Qwen3.6-35B-A3B NVFP4 + DFlash line — REVISED 2026-07-02, now ctx-matched to MTP/base
(65536).** Official `nvidia/Qwen3.6-35B-A3B-NVFP4` on the AEON image, DFlash n=11 via the small-page
drafter, one-boot sweep across conc 1/2/4/8/16/32. **0 errors at every concurrency.**

- **Result (conc 1):** prefill 140.82 / decode **99.76** tok/s single-stream aggregate; 234/1000 prompts
  (hit the 600 s cap), **0 errors**; TTFT median 2404.9 ms.
- **The ctx confound is gone — and DFlash's single-stream lead evaporates.** Against the matched 600 s-cap
  MTP c1 baseline (99.04, [`-mtp-c1`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-mtp-c1/)), DFlash is now **+0.7%** — a wash,
  not a win. The original ctx-40960 measurement (101.9, +2.9%) overstated DFlash's edge by giving it a
  shorter context (less KV overhead) than MTP's 65536. With context fully matched, **DFlash never leads MTP
  at any concurrency** — the crossover claim collapses to "DFlash ties at conc-1, then loses monotonically."
- **Acceptance ~27% avg, mean accept-len ~3.95-of-11** (per-position 0.782→0.052) — consistent with the
  ctx-40960 run's ~20–30% and flat across this entire six-point sweep (see siblings below), confirming
  acceptance is workload-driven, not context- or concurrency-driven.
- **Boot / kernel:** `modelopt_mixed`; **MARLIN** NVFP4 MoE + `FlashInferFP8ScaledMMLinearKernel` for the
  FP8 dense layers; FLASH_ATTN; attention block size **1136**. GPU KV cache **1,197,336 tokens**, max
  concurrency 18.27× @ 65536; peak mem **111.3 GB** (single one-boot reservation, util 0.85). Boot ~320 s
  (weight load 150 s + drafter load 6 s + torch.compile 47 s + KV profiling).
- **Loader gotcha (unchanged from the ctx-40960 run):** AEON's heretic recipe sets `VLLM_TEST_FORCE_FP8_MARLIN=1`;
  on this ModelOpt checkpoint that crashes the FP8 GDN-gate linears (`AttributeError: 'MergedColumnParallelLinear'
  object has no attribute 'orig_dtype'`). Use `--quantization modelopt --moe-backend marlin` without that env.
- **TPOT 0.0** is the usual `qwen3` reasoning-parser client artifact — decode tok/s is the real number.

**Trusted recommendation unchanged, now on firmer ground: stay on native MTP.** With the ctx confound
removed, DFlash doesn't even win single-stream — it's a wash at c1 and a growing loss from c2 onward. Not
worth an external drafter, a forbidden drafter revision, and an untrusted image replacing the pinned vLLM.
Full six-point sweep: **c1 (this page)** ·
[`c2`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash-c2/) ·
[`c4`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash-c4/) ·
[`c8`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash-c8/) ·
[`c16`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash-c16/) ·
[`c32`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash-c32/). Matched MTP:
[`-mtp-c1`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-mtp-c1/). Cross-ref:
[`…heretic…dflash`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-heretic-aeon-vllm-ultimate-dflash/),
[`…dflash-blocked`]({{ site.baseurl }}/configs/ornith-1-0-35b-aeon-vllm-nvfp4-dflash-blocked/), `notes/INCOMPATIBILITIES.md`.
