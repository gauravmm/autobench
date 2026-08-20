---
title: Qwen3.6-27B (dense) · DDTree (Diffusion Draft Tree) · BLOCKED (hybrid GDN cache)
model: Qwen/Qwen3.6-27B
company: Alibaba
family: Qwen
params: 27B dense (hybrid GatedDeltaNet + full-attn)
engine: DDTree research harness (github.com/liranringel/ddtree, PyTorch + transformers, batch-1)
speculative: DDTree — tree draft over the z-lab/Qwen3.6-27B-DFlash block-diffusion drafter
quant: BF16 (harness loads the unquantized target via AutoModelForCausalLM)
quant_rationale: EXPERIMENTS.md P0 #2 — the dense-27B companion to the 35B-A3B DDTree run, so the tree result would exist for both the dense and the MoE headliner (parallels the MTP pair). Blocked for the same architectural reason as the 35B-A3B.
source_repo: Qwen/Qwen3.6-27B
download_url: https://huggingface.co/Qwen/Qwen3.6-27B
context: 4096
modalities: [text]
mm_served: false
concurrency: 1
tags: [qwen3.6-27b, Alibaba, Qwen, BF16, 16-40B, Spark recipe, conc-1]
status: blocked
measured_on: 2026-07-01
completed_at: 2026-07-01
run_command: |
  scripts/bench-ddtree.sh Qwen/Qwen3.6-27B z-lab/Qwen3.6-27B-DFlash mt-bench 20 512 64,256 0.0 q27b
  # Same GatedDeltaNet rollback wall as the 35B-A3B.
---

**BLOCKED — same hybrid GatedDeltaNet wall as [`qwen3-6-35b-a3b-ddtree-blocked`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-ddtree-blocked/).**
Qwen3.6-27B is `model_type: qwen3_5` (`Qwen3_5ForConditionalGeneration`) — the dense member of the same
Qwen3.5/3.6 family, with the **same interleaved GatedDeltaNet linear-attention + full-attention** stack. The
DDTree/DFlash harness verifies speculative blocks by `past_key_values.crop(start)` after each block, which a
recurrent linear-attention state cannot support (nothing to slice back to an arbitrary accepted position), so
the target forward fails identically. No serving engine implements DDTree, and the harness has no
hybrid-cache/state-checkpoint path.

The measurable DDTree datapoint on the Spark is on the harness-supported non-hybrid target — see
[`qwen3-coder-30b-a3b-ddtree`]({{ site.baseurl }}/configs/qwen3-coder-30b-a3b-ddtree/).
