---
title: gpt-oss-120b · vLLM · MXFP4 + EAGLE3 (LMSYS draft) · conc 32
model: openai/gpt-oss-120b
company: OpenAI
family: gpt-oss
params: 116.8B (5.1B active, MoE)
engine: vLLM
speculative: EAGLE3 (lmsys/EAGLE3-gpt-oss-120b-bf16 — the SGLang/SpecForge draft, on vLLM)
quant: MXFP4
quant_rationale: EXPERIMENTS.md #5, the decisive point — de-confound draft-vs-engine for gpt-oss-120b spec-decode at conc-32, where the published comparison was vLLM+nvidia-draft (−45%) vs SGLang+LMSYS-draft (+22%). Running vLLM + the LMSYS draft isolates the draft: does swapping ONLY the draft (nvidia→LMSYS) on vLLM rescue the −45% collapse?
source_repo: openai/gpt-oss-120b
download_url: https://huggingface.co/openai/gpt-oss-120b
context: 65536
modalities: [text]
mm_served: true
concurrency: 32
tags: [gpt-oss-120b, OpenAI, gpt-oss, MXFP4, 41-130B, Spark recipe, conc-32]
status: done
prefill_toks: 279.82
decode_toks: 246.72
mem_gb: 106.86
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85) + EAGLE3 head
spec_acceptance: mean acceptance length ~1.9 (1.77–2.17) · avg draft acceptance ~29% (26–39%) — higher than conc-1 (~20%, low-batch pathology) but still below the same LMSYS draft on SGLang (~55%); part of that cross-engine gap may be a metric-definition difference (vLLM issue #42508)
measured_on: 2026-07-01
completed_at: 2026-07-01 19:21 +0800
engine_image: vllm/vllm-openai:cu130-nightly@sha256:3dbe092ec5b2cef63b6104d33fa75d6ce53a7870962529ada69f78bbbc38e776
run_command: |
  # vLLM + LMSYS draft, conc-32 (the decisive draft-vs-engine point). cu130-nightly, VOCAB_DIR override.
  VLLM_IMAGE=vllm/vllm-openai:cu130-nightly VOCAB_DIR=$HOME/tiktoken_encodings \
    scripts/bench-vllm-serving.sh openai/gpt-oss-120b 65536 32 1000 900 256 \
    --speculative-config '{"model":"lmsys/EAGLE3-gpt-oss-120b-bf16","method":"eagle3","num_speculative_tokens":3}'
  # 849/1000 prompts (no cap; 867 s), 151 harmony errors. ready after 549 s.
---

**conc-32 — the draft was ~the entire −45% disaster: swapping nvidia→LMSYS rescues vLLM from −45% to
essentially neutral.** gpt-oss-120b MXFP4 + `lmsys/EAGLE3-gpt-oss-120b-bf16` on vLLM.

- **Result (conc 32):** prefill 279.82 / decode **246.72** tok/s aggregate; 849/1000 prompts (no time cap,
  867 s), **151 harmony errors**; peak mem 106.9 GB.
- **Draft-vs-engine, isolated at conc-32:**

  | gpt-oss-120b @ conc-32 | decode tok/s | vs its base | draft accept |
  |---|--:|--:|--:|
  | vLLM base (no spec) | 252.8 | — | — |
  | vLLM + **NVIDIA** throughput draft | 138.5 | **−45%** | ~zero |
  | **vLLM + LMSYS draft (this)** | **246.72** | **−2.4%** | ~29% |
  | SGLang base (no spec) | 140.3 | — | — |
  | SGLang + LMSYS draft | 171.86 | **+22%** | ~55% |

- **Draft match dominates the sign — the post's central claim, confirmed.** Holding the engine fixed (vLLM)
  and swapping ONLY the draft, decode goes **138.5 → 246.72 (+78%)**: the catastrophic −45% was almost
  entirely the **off-distribution NVIDIA throughput draft**, not vLLM. With the workload-matched LMSYS draft,
  vLLM is back to ~breakeven with its own (fast) base.
- **But the engine still shapes the outcome — two ways.** (1) **Relative:** the same LMSYS draft yields a
  +22% *win* on SGLang but only ~neutral (−2.4%) on vLLM, because vLLM converts less of it — draft acceptance
  ~29% (vLLM) vs ~55% (SGLang). (2) **Absolute:** vLLM's base is far faster (252.8 vs SGLang's 140.3), so
  vLLM+LMSYS is the **highest absolute throughput** of the spec configs (**246.7** vs SGLang's 171.9) despite
  the smaller relative gain. So "which is better" depends on the axis: SGLang wins the *speedup ratio*, vLLM
  wins *tokens/s*.
- **Caveat on the acceptance gap (vLLM issue [#42508](https://github.com/vllm-project/vllm/issues/42508)):**
  vLLM and SpecForge/SGLang define acceptance differently and disagree by ~6–10 pts (direction varies by
  model), so part of the ~29%-vs-~55% gap may be measurement, not real conversion. The *within-vLLM* trend is
  informative though: acceptance is ~20% (c1) → ~48% (c8) → ~29% (c32) — a low-batch depression at c1 (the
  EAGLE3 pathology, cf. the gpt-oss-20b [`-eagle3-c16`]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-eagle3-c16/) diagnostic) then a
  high-batch decline by c32, peaking at c8 (~48%, near SGLang's ~55%; see [`-lmsys-c8`]({{ site.baseurl }}/configs/gpt-oss-120b-vllm-mxfp4-eagle3-lmsys-c8/)). Related open bug on the same
  model: [#38754](https://github.com/vllm-project/vllm/issues/38754) (EAGLE3 acceptance→0 under CUDA
  graphs+prefix-caching+chunked-prefill via router-GEMM NaNs) — a different signature (intermittent zero, not
  a stable low value), but worth ruling out with a prefix-caching-off control.
- **TTFT/TPOT are buffered-reasoning artifacts** — aggregate decode tok/s is the valid metric. 151 harmony
  errors are the usual 256-tok mid-reasoning truncation, worse at high batch.
- Cross-ref: [`-lmsys-c1`]({{ site.baseurl }}/configs/gpt-oss-120b-vllm-mxfp4-eagle3-lmsys-c1/) · vLLM+NVIDIA
  [`eagle3`]({{ site.baseurl }}/configs/gpt-oss-120b-vllm-mxfp4-eagle3/) · SGLang+LMSYS
  [`sglang-eagle3-c32`]({{ site.baseurl }}/configs/gpt-oss-120b-sglang-mxfp4-eagle3-c32/) · base [`vllm-mxfp4`]({{ site.baseurl }}/configs/gpt-oss-120b-vllm-mxfp4/).
