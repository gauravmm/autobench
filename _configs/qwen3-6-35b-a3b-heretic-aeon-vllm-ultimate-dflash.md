---
title: Qwen3.6-35B-A3B-heretic (AEON) · vLLM-ultimate · NVFP4 + DFlash · conc 1/8/32
model: AEON-7/Qwen3.6-35B-A3B-heretic-NVFP4
company: Alibaba
family: Qwen
params: 35B / 3B (MoE, hybrid GDN+full-attn) · AEON abliterated · + DFlash external drafter
engine: vLLM (aeon-vllm-ultimate custom container, v0.23.0+aeon.sm121a.dflash)
speculative: DFlash (z-lab/Qwen3.6-35B-A3B-DFlash @31977fbe small-page rev, num_speculative_tokens 11)
quant: NVFP4 (compressed-tensors, nvfp4-pack-quantized — GDN gates kept in BF16)
quant_rationale: AEON's headline DFlash checkpoint — the model whose card claims the recipe boots and scales to c=64. Run to settle whether AEON's "blocked four ways" DFlash actually works on this hybrid-GDN target. It does — with the pre-retrain small-page drafter (the post-04-19 main drafter AEON requires asserts on this box). heretic keeps the GDN gates in BF16 (unlike official's FP8), so this isolates the base-checkpoint variable vs the official-NVFP4 sibling. SAFETY — untrusted image + abliterated weights; NO credentials, model + drafter mounted READ-ONLY, loopback port.
source_repo: AEON-7/Qwen3.6-35B-A3B-heretic-NVFP4
download_url: https://huggingface.co/AEON-7/Qwen3.6-35B-A3B-heretic-NVFP4
context: 40960
modalities: [text, image, video]
mm_served: false
concurrency: 1
tags: [qwen3.6-35b-a3b, Alibaba, Qwen, NVFP4, 16-40B, conc-1]
status: done
prefill_toks: 114.71
decode_toks: 77.64
mem_gb: 111.0
mem_source: system `free -h` after load at util 0.85 (111 GiB used / ~9.7 GiB free); GPU KV cache 1,021,738 tokens (24.94× @ 40960)
spec_acceptance: ~22–31% avg draft acceptance · mean acceptance length ~3.4–4.4 of 11 drafted · per-position ~0.72–0.82 (pos0) decaying to ~0.03–0.09 (pos10)
measured_on: 2026-06-28
completed_at: 2026-06-28 20:52 +0800
engine_image: ghcr.io/aeon-7/aeon-vllm-ultimate:2026-06-18-v0.23.0-dflashfix@sha256:be9e05a11da6e72607ab6f3e960993b253b673af0727005122a3266129a518e3
run_command: |
  # UNTRUSTED image + abliterated weights — NO creds; model + drafter READ-ONLY; loopback port. Boots once, sweeps 1/8/32.
  # KEY: the small-page drafter (z-lab @31977fbe, 4 kv-heads / sw null) clears the kv_cache_utils.py:1064 page-size
  # assert; AEON's REQUIRED post-04-19 main drafter (sw 4096 / 8 kv-heads) asserts here (verified at ctx 65536 AND 40960).
  docker run -d --name serving-heretic --gpus all --ipc=host \
    -e TORCH_CUDA_ARCH_LIST=12.1a -e ENABLE_NVFP4_SM100=0 -e VLLM_TEST_FORCE_FP8_MARLIN=1 \
    -e VLLM_ALLOW_LONG_MAX_MODEL_LEN=1 -e PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
    -v ~/heretic/model:/model:ro -v ~/ornith/drafter-smallpage:/drafter:ro -p 127.0.0.1:8000:8000 \
    --entrypoint vllm ghcr.io/aeon-7/aeon-vllm-ultimate:2026-06-18-v0.23.0-dflashfix \
    serve /model --served-model-name heretic --host 0.0.0.0 --port 8000 \
    --quantization compressed-tensors --trust-remote-code --attention-backend flash_attn --reasoning-parser qwen3 \
    --max-model-len 40960 --gpu-memory-utilization 0.85 --enable-chunked-prefill --enable-prefix-caching \
    --max-num-seqs 64 --max-num-batched-tokens 32768 \
    --speculative-config '{"method":"dflash","model":"/drafter","num_speculative_tokens":11}'
  python3 scripts/bench-serving.py --base-url http://127.0.0.1:8000 --model heretic \
    --dataset benchmark_data/ShareGPT_V3_unfiltered_cleaned_split.json --concurrency {1,8,32} --max-tokens 256
---

**DONE — refutes the "DFlash blocked four ways on GDN" claim. It boots AND runs clean (0 errors, conc 1/8/32).**
AEON's `Qwen3.6-35B-A3B-heretic-NVFP4` (NVFP4 compressed-tensors, BF16 GDN gates) on the AEON image, ctx 40960,
DFlash n=11 via the small-page drafter, util 0.85.

| conc | prefill tok/s | decode tok/s (agg) | vs MTP decode | TTFT median |
|------|--------------:|-------------------:|--------------:|------------:|
| 1    | 114.71 | 77.64 | −17% (MTP 93.9) | 3337 ms |
| 8    | 266.15 | 246.45 | −15% (MTP 289.1) | 8019 ms |
| 32   | 400.60 | 398.11 | −26% (MTP 541.3) | 19827 ms |

- **The block was wrong — but the speedup isn't there either (on heretic).** No GDN-rollback crash (#39273), no
  prefix-cache IndexError (#41884, ran with prefix-caching ON), 0 errors. But decode trails native MTP at *every*
  concurrency. The abliterated heretic base is the worst of the two checkpoints under DFlash — its official-NVFP4
  sibling (true base, FP8 gates) drafts slightly better and at least wins conc-1; see that page.
- **Acceptance ~22–31% avg, mean accept-len ~3.4–4.4 of 11** drafted (per-position 0.72–0.82 → ~0.05 by pos10).
  Well below MTP's ~66%/accept-len-3-of-3 — the draft-efficiency gap that makes MTP faster despite drafting fewer tokens.
- **The drafter inversion (important).** AEON's card *requires* the post-2026-04-19 `main` drafter; that one (sw 4096 /
  8 kv-heads) trips `assert page_size_bytes == max_page_size` (`kv_cache_utils.py:1064`) on this box at BOTH ctx 65536 and
  40960 — i.e. AEON's published recipe does **not** reproduce verbatim on this DGX Spark. Only the *forbidden* pre-retrain
  small-page rev `31977fbe13a8` (4 kv-heads, sw null) clears the assert and serves.
- **Boot / kernel:** compressed-tensors NVFP4, **MARLIN** MoE, FLASH_ATTN, attention block size **1136** (draft small
  page unified with the mamba/GDN page). GPU KV cache **1,021,738 tokens, 24.94× @ 40960**; ~111 GiB at util 0.85. Boot 390 s.

**Recommendation: native MTP.** DFlash is *not blocked* on this hybrid target — that earlier conclusion is corrected —
but on a mixed (ShareGPT) workload it's net-negative vs MTP on the heretic checkpoint. Cross-ref:
[`…official…dflash`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash/) (the production checkpoint, wins conc-1),
[`…dflash-blocked`]({{ site.baseurl }}/configs/ornith-1-0-35b-aeon-vllm-nvfp4-dflash-blocked/), `notes/INCOMPATIBILITIES.md`.
