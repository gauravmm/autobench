---
title: gpt-oss-20b · vLLM · MXFP4 · conc 2
model: openai/gpt-oss-20b
company: OpenAI
family: gpt-oss
params: 21B / 3.6B (MoE)
engine: vLLM
quant: MXFP4
quant_rationale: conc-2 base (non-spec) point of gpt-oss-20b — the matched no-spec baseline for the EAGLE3 conc-2 row (EXPERIMENTS.md #15). Same cu130-nightly recipe as the published conc-32 base; only --max-num-seqs differs. Needed to test whether the EAGLE3 conc-32 "+28%" is a real acceptance win or a scheduling artifact — the base line must exist at 2/4/16 to measure the spec speedup there.
source_repo: openai/gpt-oss-20b
download_url: https://huggingface.co/openai/gpt-oss-20b
context: 65536
modalities: [text]
mm_served: true
concurrency: 2
tags: [gpt-oss-20b, OpenAI, gpt-oss, MXFP4, 16-40B, Spark recipe, conc-2]
status: done
prefill_toks: 128.27
decode_toks: 83.37
mem_gb: 108.52
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85)
measured_on: 2026-07-01
completed_at: 2026-07-01 15:22 +0800
engine_image: vllm/vllm-openai:cu130-nightly@sha256:3dbe092ec5b2cef63b6104d33fa75d6ce53a7870962529ada69f78bbbc38e776
run_command: |
  # conc-2 base (no spec), cu130-nightly to match the gpt-oss-20b series. Harmony vocab via VOCAB_DIR override
  # (the historical ~/models/tiktoken_cache was empty+root-owned — see notes/INCOMPATIBILITIES.md).
  VLLM_IMAGE=vllm/vllm-openai:cu130-nightly VOCAB_DIR=$HOME/tiktoken_encodings \
    scripts/bench-vllm-serving.sh openai/gpt-oss-20b 65536 2 1000 600 256
  # 209/1000 prompts (hit 600 s cap), 5 harmony errors. TTFT/TPOT are buffered-reasoning artifacts.
---

**conc-2 base (no-spec) point of gpt-oss-20b MXFP4** — the matched baseline the EAGLE3 artifact test needs
(EXPERIMENTS.md #15). Same cu130-nightly recipe as the published conc-32 base; only `--max-num-seqs` changes.

- **Result (conc 2):** prefill 128.27 / decode **83.37** tok/s aggregate; 209/1000 prompts (hit the 600 s
  cap), **5 harmony errors** (mid-reasoning truncation at 256 tok — same class as the conc-32 base's 108
  errors, fewer at low batch); peak mem 108.5 GB.
- **Purpose:** anchors the base line so the EAGLE3 conc-2 point (pending) can be expressed as a real
  decode-speedup. The post's claim is that EAGLE3's conc-32 "+28%" is a scheduling/prefill effect, not
  acceptance — if so, EAGLE3-vs-base should be **flat or negative** at conc 2/4/16 and only spike at conc-32.
  This base row is half of that measurement at conc-2.
- **TTFT/TPOT are buffered-reasoning chat-path artifacts** (vLLM emits the harmony reasoning channel in one
  burst) — the aggregate decode tok/s is the valid metric.
- Base siblings: [`-c4`]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-c4/) · [`-c16`]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-c16/) ·
  [`c32` (main)]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4/). EAGLE3 counterpart: [`-eagle3-c2`]({{ site.baseurl }}/configs/gpt-oss-20b-vllm-mxfp4-eagle3-c2/).
