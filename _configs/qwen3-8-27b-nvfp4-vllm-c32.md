---
title: Qwen3.8-27B · vLLM · NVFP4
model: Qwen/Qwen3.8-27B
company: Alibaba
family: Qwen
params: 27B (dense, hybrid linear-attn)
engine: vLLM
quant: NVFP4
quant_rationale: Unsloth's NVFP4 quant of the day-one Qwen3.8-27B release (unsloth/Qwen3.8-27B-NVFP4) — mixed-precision compressed-tensors, NVFP4 (W4A4) on the MLP gate/up/down projections and FP8 (W8A8) on attention projections, linear-attn in/out projections, lm_head and the last 8 layers' MLPs; vision tower and the MTP head left unquantized. NVFP4 is the GB10 fast path (it beat official FP8 by ~21% on the Qwen3.6-27B sibling), and no nvidia/ NVFP4 exists for this model. Base (non-speculative) config; the in-repo MTP head is exercised in the -mtp sibling.
source_repo: unsloth/Qwen3.8-27B-NVFP4
download_url: https://huggingface.co/unsloth/Qwen3.8-27B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 32
tags: [qwen3.8-27b, Alibaba, Qwen, NVFP4, 16-40B, conc-32]
status: done
prefill_toks: 270.64
decode_toks: 209.97
mem_gb: 104.11
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85)
measured_on: 2026-08-15
completed_at: 2026-08-15 10:01 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:677afd5bf3b4bb9881f91e107af7098f8410726b4c05b25cb4a815900b398204
run_command: |
  # NVFP4 (compressed-tensors, nvfp4-pack-quantized auto-detected) on vLLM nightly-aarch64. Base, conc-32.
  scripts/bench-vllm-serving.sh unsloth/Qwen3.8-27B-NVFP4 65536 32 1000 900 256 \
    --trust-remote-code --dtype bfloat16
  # 814/1000 prompts, 0 errors, hit the 900 s time cap (cold load 571 s — 14 GB download + 38 s compile).
  # TTFT median 456.2 ms, TPOT median 144.1 ms, req throughput 0.876/s.
---

**Day-one Qwen3.8-27B on the Spark: 210 tok/s decode at conc-32, and it loads on stock vLLM nightly with
no flags beyond `--dtype bfloat16`.** The model landed 2026-08-14; `vllm/vllm-openai:nightly-aarch64`
(vLLM 0.27.2rc1.dev77, transformers 5.15.0) already registers `Qwen3_5ForConditionalGeneration` and
`Qwen3_5MTP`, so there was no arch wall to work around.

- **Result (conc 32):** prefill **270.6** / decode **210.0** tok/s aggregate; **814/1000, 0 errors**;
  TTFT median 456 ms, TPOT median 144 ms. Hit the 900 s cap (928.7 s wall) — the 571 s cold start
  (first-time 14 GB download + 38 s torch.compile) ate most of the budget, so the entry count is capped
  but the tok/s is steady-state. Flagged per the run-cap policy.
- **Memory breakdown (from the vLLM log, the useful number the 104.1 GB headline hides):** weights +
  non-torch **25.15 GiB**, peak activation **3.68 GiB**, CUDA-graph pool **0.40 GiB** (estimated 1.86, a
  362% over-estimate), KV cache **74.61 GiB** = **2,128,554 tokens** → max concurrency **32.5×** at
  65536 ctx. Free on device at startup 112.81/121.69 GiB. So the 104 GB headline is ~72% KV reservation;
  the model itself is a comfortable 25 GB and there is a lot of room to push context or concurrency.
- **This checkpoint silently gets an FP8 KV cache, and it doubles KV capacity.** unsloth's
  `quantization_config` carries a `kv_cache_scheme` (static per-tensor E4M3, `num_bits: 8`), so vLLM's
  `kv_cache_dtype=auto` resolves to FP8 KV — nothing on the command line says so. Against the official
  [`Qwen/Qwen3.8-27B-FP8`]({{ site.baseurl }}/configs/qwen3-8-27b-fp8-vllm-c32/) repo, which carries **no** `kv_cache_scheme` and
  therefore runs a BF16 KV cache, the same ~70 GiB reservation buys **2,128,554 vs 1,046,391 tokens —
  almost exactly 2×** (32.5× vs 16.0× max concurrency at 65536 ctx). Worth knowing before reading any
  NVFP4-vs-FP8 memory comparison on this model: they are not serving the same KV precision.
- **Architecture — same hybrid stack as Qwen3.5/3.6, not a new one.** `model_type: qwen3_5`, 64 layers
  interleaving **3× GatedDeltaNet linear-attention : 1× full attention** (`full_attention_interval: 4`,
  16 full-attn layers), hidden 5120, head_dim 256, 24 heads / 4 KV heads, `attn_output_gate`,
  partial RoPE (0.25) with interleaved mRoPE, 248320 vocab, 262144 max positions. That interleaving is
  why the KV reservation buys 2.1 M tokens on a 27B dense model — only a quarter of the layers hold a
  real KV cache. It is also why **DDTree stays blocked** (see below).
- **Quant is mixed, not uniform NVFP4.** unsloth splits it: `nvfp4-pack-quantized` W4A4 on
  `mlp.(gate|up|down)_proj`, `float-quantized` W8A8 on the attention projections, the linear-attn
  in/out projections, `lm_head` **and layers 56–63's MLPs** (the last 8 layers kept at FP8). The whole
  27-block vision tower, every `linear_attn` norm/conv path, and `re:^mtp.*` are in `ignore` —
  so the MTP head is BF16 and usable as a draft without a quant mismatch.
- **Served text-only** (`mm_served: false`) — the checkpoint is image+video capable (`vision_config`,
  `video_preprocessor_config.json`, patch 16, spatial merge 2) but the ShareGPT workload is text, and
  this keeps it comparable to the rest of the sweep.
- **Speculative options, checked at benchmark time (2026-08-15):**
  - **MTP — available in-repo.** `text_config.mtp_num_hidden_layers: 1`. Benchmarked in
    [`qwen3-8-27b-nvfp4-vllm-mtp-c32`]({{ site.baseurl }}/configs/qwen3-8-27b-nvfp4-vllm-mtp-c32/).
  - **DFlash — does not exist yet.** z-lab publishes DFlash drafters for Qwen3.5-27B, Qwen3.6-27B and
    Qwen3.6-35B-A3B, but their newest push is 2026-07-05 (Alpamayo) and there is **no Qwen3.8 drafter**
    on HF at all. Worth re-checking — this model is one day old.
  - **DDTree — blocked, same wall as [`qwen3-6-27b-ddtree-blocked`]({{ site.baseurl }}/configs/qwen3-6-27b-ddtree-blocked/).** It
    needs a DFlash drafter (none) *and* the harness verifies blocks via `past_key_values.crop(start)`,
    which the recurrent GatedDeltaNet state cannot support. Identical architecture, identical block.
- **Repo choice.** Trusted-repo policy: NVIDIA publishes no NVFP4 for this model (as with the 27B
  sibling); official `Qwen/Qwen3.8-27B-FP8` exists as the FP8 comparison point, and unsloth is the
  well-known quantizer used for the Qwen3.6-27B NVFP4 configs. The long tail of `*-oQ4e-mtp` / MLX /
  "Optimized-Speed" repos that appeared within a day of release are unvetted and were not used.
