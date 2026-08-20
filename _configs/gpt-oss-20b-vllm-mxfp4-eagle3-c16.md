---
title: gpt-oss-20b · vLLM · MXFP4 + EAGLE3 · conc 16
model: openai/gpt-oss-20b
company: OpenAI
family: gpt-oss
params: 21B / 3.6B (MoE)
engine: vLLM
speculative: EAGLE3
quant: MXFP4
quant_rationale: conc-16 point of the EAGLE3 fine-grained sweep (EXPERIMENTS.md #15). Intended to test whether the conc-32 "+28%" is a scheduling artifact — instead it uncovered a genuine concurrency-dependent acceptance jump (see Notes), so this is the pivotal point of the sweep. Same cu130-nightly + RedHatAI EAGLE3 recipe as the other rows; measured against the matched conc-16 base plus a controlled same-subset diagnostic.
source_repo: openai/gpt-oss-20b
download_url: https://huggingface.co/openai/gpt-oss-20b
context: 65536
modalities: [text]
mm_served: true
concurrency: 16
tags: [gpt-oss-20b, OpenAI, gpt-oss, MXFP4, 16-40B, Spark recipe, conc-16]
status: done
prefill_toks: 552.54
decode_toks: 431.75
mem_gb: 108.06
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85) + EAGLE3 head
spec_acceptance: mean acceptance length ~2.3 (stable 2.18–2.44) · avg draft acceptance ~44% (39.5–48.0%) · per-position ~0.63/0.42/0.27 — MUCH higher than conc-2/4 (~5%), and a controlled same-subset run proves it's concurrency-driven, not sampling (see Notes)
measured_on: 2026-07-01
completed_at: 2026-07-01 16:36 +0800
engine_image: vllm/vllm-openai:cu130-nightly@sha256:3dbe092ec5b2cef63b6104d33fa75d6ce53a7870962529ada69f78bbbc38e776
run_command: |
  # conc-16 EAGLE3, cu130-nightly + RedHatAI speculator. Harmony vocab via VOCAB_DIR override.
  VLLM_IMAGE=vllm/vllm-openai:cu130-nightly VOCAB_DIR=$HOME/tiktoken_encodings \
    scripts/bench-vllm-serving.sh openai/gpt-oss-20b 65536 16 1000 600 256 \
    --speculative-config '{"model":"RedHatAI/gpt-oss-20b-speculator.eagle3","method":"eagle3","num_speculative_tokens":3}'
  # 993/1000 prompts (did NOT hit cap; 551.7 s), 7 harmony errors. ready after 165 s.
  # Diagnostic (isolates concurrency vs prompt-subset): same recipe, conc 16, --num-prompts 150 (= the conc-2
  # subset) → 148/150, acceptance ~2.3/~44% (NOT ~5%). So acceptance is concurrency-driven here.
---

**conc-16 EAGLE3 — the sweep's pivot: spec FLIPS to a +26.7% win, and the reason is a real
concurrency-driven acceptance jump (not the scheduling artifact the post assumed).** gpt-oss-20b MXFP4 +
RedHatAI EAGLE3 speculator on vLLM, conc 16.

- **Result (conc 16):** prefill 552.54 / decode **431.75** tok/s aggregate; **993/1000 prompts, 7 errors**,
  finished in 551.7 s (did NOT hit the cap — a near-full clean sample); peak mem 108.1 GB.
- **EAGLE3 vs base at conc-16: +26.7%** (431.75 vs base [340.69]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-c16/)). Combined with
  the low-conc losses the sweep is **−29.3% (c2) → −32.9% (c4) → +26.7% (c16) → +28.2% (c32)** — the sign
  flip lives between c4 and c16.
- **Acceptance jumps to ~44% — and it's genuinely concurrency-driven.** Across 19/20 windows mean accept-len
  **~2.3** (2.18–2.44), avg draft acceptance **~44%** (per-position 0.63/0.42/0.27) — vs only **~5%** at
  conc-2/4. Because the low-conc runs hit the time cap on a *small* ShareGPT slice, this could have been a
  prompt-subset artifact, so I ran a **controlled diagnostic: conc-16 restricted to the same first ~150
  prompts as conc-2** → acceptance **~2.3 / ~44%**, i.e. identical to full conc-16 and **9× the conc-2 value
  on the very same prompts**. So the acceptance swing is **caused by concurrency, not by which prompts
  complete**.
- **This corrects the "+28%@c32 is a scheduling artifact" reading.** The high-conc win is **acceptance-backed**
  (~44% real acceptance / ~2.3 accepted tokens per step), not a mere prefill/scheduling effect. The genuine
  anomaly is the *opposite* of the CLAUDE.md rule: for this vLLM EAGLE3 path, **acceptance RISES with
  concurrency** (~5% at conc ≤8 → ~44% at conc ≥16), rather than staying flat. Likely a vLLM low-batch EAGLE3
  pathology (draft under-accepted at small batch — possibly a CUDA-graph/scheduler batch-size effect);
  mechanism unconfirmed, but the effect is reproducible and controlled for sampling.
- **Practical takeaway:** EAGLE3 on gpt-oss-20b ShareGPT is a **net loss below ~conc-8 and a real ~+27% win
  at conc ≥16** — so its value is genuinely concurrency-gated, but for the *high-batch serving* regime the
  win is real, not artifactual. Revisit the INCOMPATIBILITIES "acceptance ~5%, concurrency-degrading" note,
  which was measured only on the low-conc truncated runs.
- **TTFT/TPOT are buffered-reasoning artifacts** — aggregate decode tok/s is the valid metric.
- Sweep: [`-c1`]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-eagle3-c1/) · [`-c2`]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-eagle3-c2/) ·
  [`-c4`]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-eagle3-c4/) · [`-c8`]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-eagle3-c8/) ·
  [`c32` (main)]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-eagle3/). Base: [`-c16`]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-c16/).
