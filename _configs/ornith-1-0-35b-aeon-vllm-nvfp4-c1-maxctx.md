---
title: Ornith-1.0-35B AEON Uncensored · vLLM (aeon-ultimate) · NVFP4 · conc 1 (256K ctx)
model: AEON-7/Ornith-1.0-35B-AEON-Ultimate-Uncensored-NVFP4
company: Alibaba
family: Qwen
params: Qwen3.6-35B-A3B base (35B/3B MoE, hybrid GDN+full-attn) · AEON "Ornith 1.0" RL post-train, abliterated
engine: vLLM (aeon-vllm-ultimate custom container)
speculative: none (DFlash OFF — DFlash trips hybrid+draft KV unification, see dflash-blocked page)
quant: NVFP4 (compressed-tensors, nvfp4-pack-quantized)
quant_rationale: Same NVFP4 compressed-tensors checkpoint as the conc-32 page, at full 256K context. Marlin weight-only NVFP4 (GB10 has no native FP4 compute). Run at util 0.85 to characterize the model's true KV-pool ceiling at max context.
source_repo: AEON-7/Ornith-1.0-35B-AEON-Ultimate-Uncensored-NVFP4
download_url: https://huggingface.co/AEON-7/Ornith-1.0-35B-AEON-Ultimate-Uncensored-NVFP4
context: 262144
modalities: [text, image, video]
mm_served: false
concurrency: 1
tags: [ornith-1-0-35b-aeon, Alibaba, Qwen, NVFP4, 16-40B, conc-1]
status: done
prefill_toks: 41.52
decode_toks: 37.7
mem_gb: 106.0
mem_source: system `free -h` used after load at util 0.85 (KV memory 74.04 GiB; model 22.24 GiB). Not resident-only.
measured_on: 2026-06-28
completed_at: 2026-06-28 16:13 +0800
engine_image: ghcr.io/aeon-7/aeon-vllm-ultimate:latest@sha256:be9e05a11da6e72607ab6f3e960993b253b673af0727005122a3266129a518e3
run_command: |
  # Untrusted image — NO creds, model READ-ONLY, loopback port. Single boot yields BOTH the conc-1
  # single-stream point AND the max-concurrency-at-max-context figure (KV-pool derived, at util 0.85).
  docker run -d --name serving-ornith --gpus all --ipc=host \
    -e TORCH_CUDA_ARCH_LIST=12.1a -e CUTE_DSL_ARCH=sm_121a -e VLLM_USE_FLASHINFER_SAMPLER=1 \
    -v ~/ornith/model:/model:ro -p 127.0.0.1:8000:8000 \
    --entrypoint vllm ghcr.io/aeon-7/aeon-vllm-ultimate:latest \
    serve /model --served-model-name ornith --host 0.0.0.0 --port 8000 \
    --quantization compressed-tensors --trust-remote-code \
    --max-model-len 262144 --gpu-memory-utilization 0.85 \
    --max-num-seqs 64 --max-num-batched-tokens 16384 \
    --mamba-cache-dtype float32 --enable-prefix-caching --reasoning-parser qwen3
  python3 scripts/bench-serving.py --base-url http://127.0.0.1:8000 --model ornith \
    --dataset benchmark_data/ShareGPT_V3_unfiltered_cleaned_split.json \
    --num-prompts 1000 --max-seconds 900 --concurrency 1 --max-tokens 256
---

**DONE — single-stream point and the max-concurrency ceiling at full 256K context.** Ornith-1.0-35B
(Qwen3.6-35B-A3B base) on the AEON vLLM container, NVFP4, ctx **262144**, conc 1, DFlash off, util 0.85.

- **Result (conc 1):** prefill **41.52 tok/s**, decode **37.7 tok/s** single-stream; **133 completed,
  0 errors** before the 900 s cap. TTFT median 6.7 s (256K-capable prefill setup), req throughput
  0.148 req/s. Boot 385 s.
- **★ Maximum concurrency @ 256K ctx (util 0.85): 14.43×** — GPU KV cache **3,781,766 tokens**, KV
  memory **74.04 GiB**, model 22.24 GiB, ~106 GiB used total. (At ctx 32K the same util gives 98.27× /
  3.22M-token pool — see the conc-32 page.) Scales down ~proportionally if you drop util toward the
  main engine's 0.69.
- **Kernel path:** identical to the conc-32 page — `MarlinNvFp4LinearKernel` + MARLIN MoE, FLASH_ATTN,
  hybrid GDN. Attention block size auto-set to 1072 to match the mamba/GDN page size (the unification
  that *succeeds* without a draft — and **fails with DFlash**, see the blocked page).
- **TPOT 0.0** is the same client artifact (fork's `reasoning` field); decode tok/s is the real number.

This is the trusted, DFlash-off baseline. DFlash (AEON's headline ~1.9× claim) does **not** boot on this
hybrid model — see [DFlash-blocked]({{ site.baseurl }}/configs/ornith-1-0-35b-aeon-vllm-nvfp4-dflash-blocked/) for the root cause and
the likely unblock (pin the draft to its pre-retrain small-page revision).
