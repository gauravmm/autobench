---
title: Qwen3-Coder-30B-A3B · DDTree vs DFlash · HumanEval (coding workload) · single-stream
model: Qwen/Qwen3-Coder-30B-A3B-Instruct
company: Alibaba
family: Qwen
params: 30B / 3B (MoE, standard attention) + DFlash external drafter
engine: DDTree research harness (github.com/liranringel/ddtree, PyTorch + transformers, batch-1)
speculative: DDTree tree draft (budgets 64/256) vs single-line DFlash — z-lab/Qwen3-Coder-30B-A3B-DFlash, block_size 16
quant: BF16 (harness loads the unquantized target via AutoModelForCausalLM)
quant_rationale: EXPERIMENTS.md P0 #3 — the coding-workload contrast to the mt-bench (chat) run. The paper's 8.22× is coding-only and our serving runs are chat/ShareGPT; this run tests whether block-diffusion acceptance jumps toward the published band on code, with the TREE method specifically. Same model/drafter as qwen3-coder-30b-a3b-ddtree, only the dataset changes.
source_repo: Qwen/Qwen3-Coder-30B-A3B-Instruct
download_url: https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct
context: 4096
modalities: [text]
mm_served: false
concurrency: 1
tags: [qwen3-coder-30b-a3b, Alibaba, Qwen, BF16, 16-40B, Spark recipe, conc-1]
status: done
prefill_toks: n/a (harness reports single-stream decode + accept-len, not prefill tok/s)
decode_toks: 49.34
mem_gb: 113.27
mem_source: system MemAvailable delta (10s sampling) — inflated by tree/KV buffers on long full-256-tok code spans + fs page cache; batch-1 working set is ~68 GB (cf. the mt-bench run)
spec_acceptance: mean accept-len 1.00 (base) / 7.96 (DFlash) / 9.74 (DDTree tb64) / 10.50 (DDTree tb256) — code lifts every method ~3.5× over the mt-bench chat accept-lens
measured_on: 2026-07-01
completed_at: 2026-07-01 21:26 +0800
engine_image: lmsysorg/sglang:nightly-dev-cu13-20260623-ba9d5aed@sha256:ca580c17cf5f9d2e268f4153d977e3cd46528feb2c62a4de8683a05d08da3cf2
run_command: |
  # Same harness/model/drafter as the mt-bench run; dataset = humaneval (164 single-turn code problems).
  scripts/bench-ddtree.sh Qwen/Qwen3-Coder-30B-A3B-Instruct z-lab/Qwen3-Coder-30B-A3B-DFlash \
    humaneval 12 256 64,256 0.0 coder-humaneval
  # 12 HumanEval problems, 256-tok cap (all hit it: 3072 out toks), temp 0.0, block_size 16, cpp compaction ON.
---

**On code, block-diffusion spec-decode is a 2.7–2.8× single-stream WIN — and the tree's edge over the single
line nearly vanishes.** Same Qwen3-Coder-30B-A3B / DFlash drafter as [`…-ddtree`]({{ site.baseurl }}/configs/qwen3-coder-30b-a3b-ddtree/),
only the workload changes (chat → code). This is the workload thesis, measured.

| method | decode tok/s | accept-len (code) | vs base | accept-len (chat) |
|---|--:|--:|--:|--:|
| baseline (autoregressive) | 17.66 | 1.00 | — | 1.00 |
| DFlash (single-line) | 47.87 | **7.96** | **2.71×** | 2.25 |
| **DDTree, tree-budget 64** | **49.34** | **9.74** | **2.79×** | 3.22 |
| DDTree, tree-budget 256 | 41.30 | 10.50 | 2.34× | 3.69 |

- **Acceptance is overwhelmingly workload-driven — thesis confirmed.** Moving chat→code, single-line DFlash
  accept-len jumps **2.25 → 7.96** (×3.5) and DDTree-tb64 **3.22 → 9.74** (×3.0). Code is templated and
  low-entropy, so the block-diffusion draft nails long spans the target accepts wholesale. This is exactly the
  §1c/§3b "acceptance is workload- not concurrency-driven" claim, now shown for the *tree* method specifically.
- **Spec flips from a batch-1 loss (chat) to a huge win (code).** On chat both spec methods were ≤1.12× (DFlash
  a net *loss*, 0.92×). On code, DFlash is **2.71×** and DDTree-tb64 **2.79×** over autoregressive — even at
  batch-1, unquantized bf16, with the SDPA-forced tree verify. So whether single-stream spec-decode is worth it
  is dominated by the workload, not the method.
- **The tree's marginal value is inversely related to how good the single line already is.** DDTree-tb64 beats
  single-line DFlash by only **+3.1%** on code (49.34 vs 47.87) versus **+22%** on chat. When the single line
  already accepts ~8-of-16 (code), there is little headroom left for the tree to capture; when it accepts only
  ~2.25 (chat) the tree's extra candidate continuations matter a lot. **Takeaway: DDTree earns its keep on
  HARD/high-entropy workloads; on easy/templated ones plain DFlash already gets most of the win.**
- **Budget optimum holds, sharper here.** tb256 has the highest accept-len (10.50) yet is the *slowest* spec
  config (41.30, 0.84× of tb64) — with code rounds already few (324→299), the 256-node tree's per-step verify
  cost dominates. **tb64 is again the sweet spot.**
- **Memory 113 GB** is higher than the mt-bench 68 GB because every code completion runs the full 256 tokens
  (longer sequences, larger tree/KV buffers) and MemAvailable also absorbs fs page cache; the true batch-1
  working set is ~68 GB (per the chat run).

**METHODOLOGY:** batch-1 only (no conc 8/32); bf16 target (absolute tok/s not comparable to the NVFP4 serving
rows); harness-supported proxy target (our Qwen3.6 hybrids are blocked — [`35b-a3b`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-ddtree-blocked/)).
Chat companion: [`qwen3-coder-30b-a3b-ddtree`]({{ site.baseurl }}/configs/qwen3-coder-30b-a3b-ddtree/). See `notes/INCOMPATIBILITIES.md` +
`scripts/bench-ddtree.sh`.
