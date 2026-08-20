---
title: Qwen3-Coder-30B-A3B · DDTree vs DFlash vs autoregressive · single-stream (batch-1)
model: Qwen/Qwen3-Coder-30B-A3B-Instruct
company: Alibaba
family: Qwen
params: 30B / 3B (MoE, standard attention) + DFlash external drafter
engine: DDTree research harness (github.com/liranringel/ddtree, PyTorch + transformers, batch-1)
speculative: DDTree tree draft (budgets 64/256) vs single-line DFlash — z-lab/Qwen3-Coder-30B-A3B-DFlash, block_size 16
quant: BF16 (harness loads the unquantized target via AutoModelForCausalLM)
quant_rationale: EXPERIMENTS.md P0 #1/#3 — DDTree is the post's one un-measured method, and it isn't in any serving engine, so it only runs in the paper's PyTorch harness. Our own Qwen3.6 targets are hybrid GatedDeltaNet and the harness can't roll their recurrent state back for spec verification (see qwen3-6-35b-a3b-ddtree-blocked). Qwen/Qwen3-Coder-30B-A3B-Instruct is the harness's OWN validated target (qwen3_moe, standard attention) — same-size 30B-A3B MoE, so it is the faithful proxy for the tree-vs-single-line question on this box.
source_repo: Qwen/Qwen3-Coder-30B-A3B-Instruct
download_url: https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct
context: 4096
modalities: [text]
mm_served: false
concurrency: 1
tags: [qwen3-coder-30b-a3b, Alibaba, Qwen, BF16, 16-40B, Spark recipe, conc-1]
status: done
prefill_toks: n/a (harness reports single-stream decode + accept-len, not prefill tok/s)
decode_toks: 20.75
mem_gb: 68.02
mem_source: system MemAvailable delta (10s sampling) — bf16 30B-A3B target + bf16 DFlash drafter, batch-1, ctx short
spec_acceptance: mean accept-len 1.00 (base) / 2.25 (DFlash) / 3.22 (DDTree tb64) / 3.69 (DDTree tb256) — the tree lifts accept-len +43% over single-line DFlash at tb64, +64% at tb256
measured_on: 2026-07-01
completed_at: 2026-07-01 21:13 +0800
engine_image: lmsysorg/sglang:nightly-dev-cu13-20260623-ba9d5aed@sha256:ca580c17cf5f9d2e268f4153d977e3cd46528feb2c62a4de8683a05d08da3cf2
run_command: |
  # DDTree = the post's un-measured tree method. NOT in vLLM/SGLang -> paper's PyTorch harness (~/ddtree),
  # run inside the trusted SGLang cu130 torch env (has pip flash_attn + datasets, built for GB10 sm_121a).
  # One pass measures baseline (autoregressive) vs DFlash (single-line) vs DDTree (tree budgets) on the SAME
  # prompts. C++ tail-cache-compaction compiled+loaded (DDTree's fair path). See scripts/bench-ddtree.sh.
  scripts/bench-ddtree.sh Qwen/Qwen3-Coder-30B-A3B-Instruct z-lab/Qwen3-Coder-30B-A3B-DFlash \
    mt-bench 12 256 64,256 0.0 coder-mtbench
  # 12 mt-bench prompts (24 turns), 256-tok cap, temp 0.0, block_size 16.
---

**DDTree is what turns block-diffusion spec-decode from a single-stream LOSS into a single-stream WIN — and
there's a budget optimum.** Qwen3-Coder-30B-A3B (bf16, batch-1) on the paper's harness, mt-bench, 24 turns.

| method | decode tok/s | mean accept-len | vs autoregressive base |
|---|--:|--:|--:|
| baseline (autoregressive target) | 18.52 | 1.00 | — |
| DFlash (single-line, n=16 block) | 16.95 | 2.25 | **−8.4%** |
| **DDTree, tree-budget 64** | **20.75** | **3.22** | **+12.1%** |
| DDTree, tree-budget 256 | 17.32 | 3.69 | −6.5% |

- **The tree recovers the loss — the post's central "future" question, answered YES.** Single-line DFlash is a
  **net loss at batch-1** here (0.92×): a mean accept-len of 2.25-of-16 doesn't repay the drafter pass plus the
  block verify. Rebuilding the *same* block-diffusion draft as a **tree** (tb64) lifts accept-len to **3.22**
  and decode to **+12.1% over autoregressive** — a **+22% swing over single-line DFlash** (20.75 vs 16.95).
  So on this machine the block-diffusion draft only pays off *as a tree*.
- **Bigger tree ≠ faster — the budget has an optimum.** tb256 has the **highest** accept-len (3.69) yet is
  **slower** than tb64 (17.32 vs 20.75) and back under baseline (0.94×). Past ~tb64 the extra acceptance is
  bought with more nodes to verify per step, and on the (SDPA-forced, see below) target that verify cost
  outgrows the acceptance gain. **tb64 is the sweet spot; tb256 over-spends.** Any DDTree deployment must tune
  the budget — the CaDDTree cost-aware variant (EXPERIMENTS.md P2 #11) targets exactly this.
- **Why spec is a loss at batch-1 at all — and a caveat specific to the tree.** Two single-stream headwinds:
  (1) the target is **unquantized bf16** (memory-bandwidth-bound), so each verify is expensive; (2) DDTree's
  ancestor-only tree attention mask **forces the target verifier onto torch SDPA** — flash-attn can't express
  the tree mask — so the tree pays a slower verify kernel than a plain-causal flash-attn forward would. Both
  make the batch-1 bar high; the tree clears it, the single line doesn't.
- **Accept-len ladder (per-position value of the tree):** 1.00 → 2.25 → 3.22 → 3.69. The tree's win is entirely
  an **acceptance** win — it drafts multiple candidate continuations per block and verifies them together, so
  more of each block survives (fewer decode rounds: 2234 → 1536 for the same ~5k output tokens).

**METHODOLOGY — read before comparing to the serving rows:**
- **Batch-1 only.** This harness generates one request at a time; it does **not** batch concurrent requests, so
  there is **no conc-8/32 here**. The money-chart DDTree line at high concurrency cannot come from this tool.
- **bf16 target, not NVFP4.** Absolute tok/s is **not** comparable to the NVFP4 MTP/DFlash serving rows
  (`qwen3-6-35b-a3b-nvfp4-vllm-mtp`, `-ultimate-dflash`). The transferable numbers are the **DDTree-vs-DFlash
  accept-len ratio** and the **single-stream speedup-vs-autoregressive**, both measured on identical prompts.
- **Proxy target.** This is Qwen3-**Coder**-30B-A3B (standard-attention `qwen3_moe`), not our Qwen3.6-35B-A3B
  (hybrid GDN) — those are architecturally blocked in this harness (`qwen3-6-35b-a3b-ddtree-blocked`).
- **Workload:** mt-bench (chat prompts on a coding model). The coding-workload contrast (does acceptance climb
  toward the paper's code numbers?) is the HumanEval run — [`…-ddtree-humaneval`]({{ site.baseurl }}/configs/qwen3-coder-30b-a3b-ddtree-humaneval/).

Cross-ref: blocked hybrids [`35b-a3b`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-ddtree-blocked/) · [`27b`]({{ site.baseurl }}/configs/qwen3-6-27b-ddtree-blocked/) ·
`notes/INCOMPATIBILITIES.md` (DDTree harness section) · runner `scripts/bench-ddtree.sh`.
