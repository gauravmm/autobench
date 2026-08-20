---
title: Qwen3.6-35B-A3B · DDTree (Diffusion Draft Tree) · BLOCKED (hybrid GDN cache)
model: Qwen/Qwen3.6-35B-A3B
company: Alibaba
family: Qwen
params: 35B / 3B (MoE, hybrid GatedDeltaNet + full-attn)
engine: DDTree research harness (github.com/liranringel/ddtree, PyTorch + transformers, batch-1)
speculative: DDTree — tree draft over the z-lab/Qwen3.6-35B-A3B-DFlash block-diffusion drafter
quant: BF16 (harness loads the unquantized target via AutoModelForCausalLM)
quant_rationale: EXPERIMENTS.md P0 #1 — measure the post's one un-measured method (the block-diffusion draft TREE) on the Spark, head-to-head vs single-line DFlash and MTP. DDTree is not in any serving engine (only SGLang discussion #24605), so the only implementation is the paper's PyTorch harness. That harness cannot run this target — see below.
source_repo: Qwen/Qwen3.6-35B-A3B
download_url: https://huggingface.co/Qwen/Qwen3.6-35B-A3B
context: 4096
modalities: [text]
mm_served: false
concurrency: 1
tags: [qwen3.6-35b-a3b, Alibaba, Qwen, BF16, 16-40B, Spark recipe, conc-1]
status: blocked
measured_on: 2026-07-01
completed_at: 2026-07-01
engine_image: lmsysorg/sglang:nightly-dev-cu13-20260623-ba9d5aed (torch env only — harness never reached generation)
run_command: |
  # DDTree harness inside the trusted SGLang cu130 torch env (has flash_attn + datasets, built for GB10 sm_121a).
  # Target + drafter load fine; generation fails in the target forward.
  scripts/bench-ddtree.sh Qwen/Qwen3.6-35B-A3B z-lab/Qwen3.6-35B-A3B-DFlash mt-bench 20 512 64,256 0.0 q35b
  # -> ValueError: `has_previous_state` can only be called on LinearAttention layers,
  #    and the current Cache seem to only contain Attention layers.  (transformers qwen3_5_moe)
---

**BLOCKED — the open DDTree research harness cannot run Qwen3.6's hybrid GatedDeltaNet target.**
Qwen3.6-35B-A3B is `model_type: qwen3_5_moe` (`Qwen3_5MoeForConditionalGeneration`): a **hybrid** stack of
GatedDeltaNet **linear-attention** layers interleaved with full-attention layers. The DDTree/DFlash harness
(`dflash.py` / `ddtree.py`) verifies speculative blocks by rolling the target KV cache back to the accepted
prefix with `past_key_values.crop(start)` after every block. That rollback is the wall:

- **Vanilla cache mismatch.** The harness allocates a plain `transformers.DynamicCache`. On the first decode
  step the model's `_update_linear_attn_mask` calls `cache.has_previous_state()`, which raises because a
  `DynamicCache` holds only attention layers, not the LinearAttention state the hybrid model expects.
- **Deeper than a cache-class swap.** Even with the correct hybrid cache, `crop(start)` cannot rewind a
  GatedDeltaNet layer to an arbitrary token: linear-attention keeps a **recurrent state**, not per-token KV,
  so there is nothing to slice back to position `start`. Speculative decoding with rejection **requires**
  rewindable state; recurrent layers don't provide it without explicit per-step checkpointing.
- **This is the same GatedDeltaNet wall seen elsewhere.** The AEON vLLM fork only runs DFlash on this model by
  purpose-building a unified attention page (block size 1136) that reconciles the draft's small page with the
  mamba/GDN page (see [`…ultimate-dflash`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash/)). The research harness
  has no such integration, and **no serving engine implements DDTree at all**.

**Consequence for the money chart:** the DDTree line **cannot be measured for Qwen3.6-35B-A3B on the Spark
today.** DDTree here would require either (a) a hybrid-aware re-implementation of the tree verifier with
GatedDeltaNet state checkpointing, or (b) DDTree landing inside a purpose-built engine (e.g. AEON's DFlash
fork extended to trees). Neither exists.

**What we measured instead:** DDTree on the harness's own **non-hybrid** target
`Qwen/Qwen3-Coder-30B-A3B-Instruct` (`qwen3_moe`, standard attention) + `z-lab/Qwen3-Coder-30B-A3B-DFlash` —
a same-size MoE and a coding workload — giving the real tree-vs-single-line-DFlash accept-len + single-stream
speedup on this box. See [`qwen3-coder-30b-a3b-ddtree`]({{ site.baseurl }}/configs/qwen3-coder-30b-a3b-ddtree/). The dense Qwen3.6-27B
(`qwen3_5`, also hybrid) is blocked for the identical reason — [`…27b-ddtree-blocked`]({{ site.baseurl }}/configs/qwen3-6-27b-ddtree-blocked/).
