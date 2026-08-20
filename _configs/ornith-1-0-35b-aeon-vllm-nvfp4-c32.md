---
title: Ornith-1.0-35B AEON Uncensored · vLLM (aeon-ultimate) · NVFP4 · conc 32
model: AEON-7/Ornith-1.0-35B-AEON-Ultimate-Uncensored-NVFP4
company: Alibaba
family: Qwen
params: Qwen3.6-35B-A3B base (35B/3B MoE, hybrid GDN+full-attn) · AEON "Ornith 1.0" RL post-train, abliterated
engine: vLLM (aeon-vllm-ultimate custom container)
speculative: none (DFlash OFF — see the dflash-blocked page; DFlash trips hybrid+draft KV unification)
quant: NVFP4 (compressed-tensors, nvfp4-pack-quantized)
quant_rationale: Standard `Qwen3_5MoeForConditionalGeneration` NVFP4 compressed-tensors checkpoint — the SAME arch the main `nvidia/Qwen3.6-35B-A3B-NVFP4` engine runs on stock vLLM. AEON's QUICKSTART pushes their custom container, but the base model needs nothing special; this run uses the AEON image only because the model line is distributed with it. NVFP4 weights via Marlin (weight-only) — GB10 has no native FP4 compute, so Marlin is the correct kernel, not a fallback.
source_repo: AEON-7/Ornith-1.0-35B-AEON-Ultimate-Uncensored-NVFP4
download_url: https://huggingface.co/AEON-7/Ornith-1.0-35B-AEON-Ultimate-Uncensored-NVFP4
context: 32768
modalities: [text, image, video]
mm_served: false
concurrency: 32
tags: [ornith-1-0-35b-aeon, Alibaba, Qwen, NVFP4, 16-40B, conc-32]
status: done
prefill_toks: 436.0
decode_toks: 422.08
mem_gb: 110.0
mem_source: system `free -h` used after load at util 0.85 (KV pool 74.35 GiB; model 22.24 GiB). Not the resident-only footprint.
measured_on: 2026-06-28
completed_at: 2026-06-28 16:13 +0800
engine_image: ghcr.io/aeon-7/aeon-vllm-ultimate:latest@sha256:be9e05a11da6e72607ab6f3e960993b253b673af0727005122a3266129a518e3
run_command: |
  # UNTRUSTED third-party container — run with NO credentials (HF_TOKEN/API key withheld),
  # model mounted READ-ONLY, port bound to loopback (NOT --net=host as the AEON QUICKSTART uses).
  # DFlash OFF for this conc-32 run (DFlash hard-caps max-num-seqs at 16 per AEON's own docs, and
  # also fails to boot on this hybrid model — see the dflash-blocked page).
  docker run -d --name serving-ornith --gpus all --ipc=host \
    -e TORCH_CUDA_ARCH_LIST=12.1a -e CUTE_DSL_ARCH=sm_121a -e VLLM_USE_FLASHINFER_SAMPLER=1 \
    -v ~/ornith/model:/model:ro -p 127.0.0.1:8000:8000 \
    --entrypoint vllm ghcr.io/aeon-7/aeon-vllm-ultimate:latest \
    serve /model --served-model-name ornith --host 0.0.0.0 --port 8000 \
    --quantization compressed-tensors --trust-remote-code \
    --max-model-len 32768 --gpu-memory-utilization 0.85 \
    --max-num-seqs 32 --max-num-batched-tokens 16384 \
    --mamba-cache-dtype float32 --enable-prefix-caching --reasoning-parser qwen3
  python3 scripts/bench-serving.py --base-url http://127.0.0.1:8000 --model ornith \
    --dataset benchmark_data/ShareGPT_V3_unfiltered_cleaned_split.json \
    --num-prompts 1000 --max-seconds 900 --concurrency 32 --max-tokens 256
---

**DONE — strong batched throughput, exactly as expected for a 3B-active MoE on the vLLM/Marlin NVFP4 path.**
Ornith-1.0-35B (Qwen3.6-35B-A3B base) on the AEON vLLM container, NVFP4, ctx 32768, conc 32, **DFlash off**.

- **Result (conc 32):** prefill **436 tok/s**, decode **422.08 tok/s** aggregate; **1000/1000 completed,
  0 errors** in **604.5 s** (did NOT hit the 900 s cap). TTFT median 18.8 s (deep c=32 queue), req
  throughput 1.65 req/s.
- **KV pool @ util 0.85:** GPU KV cache **3,220,120 tokens** → **Maximum concurrency 98.27× @ 32K ctx**
  (KV memory 74.35 GiB). Model load 22.24 GiB, boot 315 s (full torch.compile — the AEON image has no
  persistent compile cache).
- **Kernel path:** `MarlinNvFp4LinearKernel` + **MARLIN** NvFp4 MoE backend, FLASH_ATTN, hybrid GDN
  (Triton/FLA prefill). `speculative_config=None`. Same weight-only NVFP4 path as the main engine — so
  these base numbers would be **identical on stock `vllm/vllm-openai`**; the AEON image is not load-bearing
  here (it only matters for DFlash, which doesn't boot — see below).
- **Reasoning:** returns thinking in a `reasoning` field (note: this fork uses `reasoning`, not
  `reasoning_content`), `content` clean. Recommended sampling temp 0.6 / top_p 0.95 / top_k 20.
- **TPOT median logged 0.0** is a client artifact (the bench's per-token timer doesn't see the fork's
  `reasoning` field as streamed content) — the aggregate decode tok/s is the reliable figure.

Pair with: the [conc-1 @ 256K page]({{ site.baseurl }}/configs/ornith-1-0-35b-aeon-vllm-nvfp4-c1-maxctx/) (single-stream + max
concurrency at full context) and the [DFlash-blocked page]({{ site.baseurl }}/configs/ornith-1-0-35b-aeon-vllm-nvfp4-dflash-blocked/).
