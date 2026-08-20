---
title: gpt-oss-120b · vLLM · MXFP4 + EAGLE3 (LMSYS draft) · conc 1
model: openai/gpt-oss-120b
company: OpenAI
family: gpt-oss
params: 116.8B (5.1B active, MoE)
engine: vLLM
speculative: EAGLE3 (lmsys/EAGLE3-gpt-oss-120b-bf16 — the SGLang/SpecForge draft, on vLLM)
quant: MXFP4
quant_rationale: EXPERIMENTS.md #5 — de-confound draft-vs-engine for the gpt-oss-120b spec-decode story. The published comparison was confounded (vLLM used nvidia's throughput draft = −45%@c32; SGLang used the LMSYS/SpecForge draft = +22%@c32 — both draft AND engine differed). This runs vLLM + the LMSYS draft to isolate the draft: does the workload-matched draft help on vLLM too, or is SGLang's win engine-specific? conc-1 first, to confirm vLLM even accepts the SpecForge-format draft.
source_repo: openai/gpt-oss-120b
download_url: https://huggingface.co/openai/gpt-oss-120b
context: 65536
modalities: [text]
mm_served: true
concurrency: 1
tags: [gpt-oss-120b, OpenAI, gpt-oss, MXFP4, 41-130B, Spark recipe, conc-1]
status: done
prefill_toks: 46.03
decode_toks: 25.53
mem_gb: 107.71
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85) + EAGLE3 head
spec_acceptance: mean acceptance length ~1.6 (1.36–2.19) · avg draft acceptance ~20% (12–40%) — much LOWER than the same LMSYS draft on SGLang (~55% at conc-1), consistent with the vLLM low-batch EAGLE3 pathology seen on the 20b
measured_on: 2026-07-01
completed_at: 2026-07-01 17:37 +0800
engine_image: vllm/vllm-openai:cu130-nightly@sha256:3dbe092ec5b2cef63b6104d33fa75d6ce53a7870962529ada69f78bbbc38e776
run_command: |
  # vLLM + LMSYS draft (isolates draft-vs-engine). cu130-nightly, harmony vocab via VOCAB_DIR override.
  VLLM_IMAGE=vllm/vllm-openai:cu130-nightly VOCAB_DIR=$HOME/tiktoken_encodings \
    scripts/bench-vllm-serving.sh openai/gpt-oss-120b 65536 1 500 600 256 \
    --speculative-config '{"model":"lmsys/EAGLE3-gpt-oss-120b-bf16","method":"eagle3","num_speculative_tokens":3}'
  # 62/500 prompts (hit 600 s cap; conc-1 + slow 120b), 16 harmony errors. ready after 585 s.
---

**conc-1 — vLLM DOES accept the LMSYS/SpecForge draft, and swapping it in beats vLLM's NVIDIA draft, but
still trails SGLang.** gpt-oss-120b MXFP4 + `lmsys/EAGLE3-gpt-oss-120b-bf16` on vLLM.

- **The draft loads on vLLM** (no format rejection) — so the draft-vs-engine comparison #5 wanted is possible.
- **Result (conc 1):** prefill 46.03 / decode **25.53** tok/s; 62/500 prompts (hit the 600 s cap), 16 harmony
  errors; peak mem 107.7 GB.
- **Draft-vs-engine at conc-1, three-way:**

  | conc-1 gpt-oss-120b | decode tok/s | draft accept |
  |---|--:|--:|
  | vLLM + NVIDIA throughput draft | 14.7 | ~9% |
  | **vLLM + LMSYS draft (this)** | **25.5** | ~20% |
  | SGLang + LMSYS draft | 40.6 | ~55% |

  **Swapping the draft (NVIDIA→LMSYS) on the same engine lifts decode +74% (14.7→25.5)** — the workload-matched
  draft helps on vLLM too, so the draft genuinely matters (not purely an SGLang effect). **But the engine also
  matters:** the *same* LMSYS draft yields 25.5 on vLLM vs 40.6 on SGLang. So the original −45%-vs-+22% gap was
  **both** — draft AND engine — not draft alone.
- **Why vLLM under-performs SGLang on the same draft — the low-batch EAGLE3 pathology.** Acceptance is only
  **~20%** here vs **~55%** for the identical draft on SGLang. This mirrors the gpt-oss-**20b** finding
  (vLLM EAGLE3 acceptance is depressed at low batch, ~5% at conc≤8 → ~44% at conc≥16). So the conc-1 vLLM
  number likely *understates* what the LMSYS draft can do on vLLM at high batch — **the conc-32 point is the
  decisive one** (see `-lmsys-c32`).
- **TTFT/TPOT are buffered-reasoning artifacts** — aggregate decode tok/s is the valid metric.
- Cross-ref: [`-lmsys-c32`]({{ site.baseurl }}/configs/gpt-oss-120b-vllm-mxfp4-eagle3-lmsys-c32/) · vLLM+NVIDIA
  [`eagle3`]({{ site.baseurl }}/configs/gpt-oss-120b-vllm-mxfp4-eagle3/) · SGLang+LMSYS
  [`sglang-eagle3-c1`]({{ site.baseurl }}/configs/gpt-oss-120b-sglang-mxfp4-eagle3-c1/) · base [`vllm-mxfp4`]({{ site.baseurl }}/configs/gpt-oss-120b-vllm-mxfp4/).
