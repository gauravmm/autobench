---
title: MiniMax-M2.7-REAP 172B · vLLM · NVFP4 (W4A4) · conc 1 · 160K
model: saricles/MiniMax-M2.7-REAP-172B-A10B-NVFP4-GB10
company: MiniMax (base) · saricles (REAP + NVFP4)
family: MiniMax
params: 172B / ~10B (MoE, REAP-pruned from 230B/10B — 256→192 experts, 62 layers)
engine: vLLM
quant: NVFP4 (W4A4)
quant_rationale: Same community modelopt NVFP4 (W4A4) checkpoint as the conc-32 sibling (see [base config]). This page is the single-stream serving operating point — maximum usable context (160K), conc-1, util 0.95, with tool-call + reasoning parsers enabled — i.e. how the model is actually deployed as the interactive gateway on :4000, not the throughput benchmark.
source_repo: saricles/MiniMax-M2.7-REAP-172B-A10B-BF16
download_url: https://huggingface.co/saricles/MiniMax-M2.7-REAP-172B-A10B-NVFP4-GB10
hf_repo: saricles/MiniMax-M2.7-REAP-172B-A10B-NVFP4-GB10
hf_url: https://huggingface.co/saricles/MiniMax-M2.7-REAP-172B-A10B-NVFP4-GB10
context: 163840
modalities: [text]
mm_served: true
concurrency: 1
tags: [minimax-m27-reap-172b, MiniMax, MiniMax-M2, NVFP4, 130B+, Spark recipe, REAP, conc-1]
status: done
prefill_toks: 26.76
decode_toks: 25.44
mem_gb: 121
mem_source: system MemAvailable peak while serving — used ~121/127.6 GB (1.2 GB free) at util 0.95, 160K-ctx KV reservation
measured_on: 2026-06-27
completed_at: 2026-06-27 19:22 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:68e23ddd982ad5642e21354c2242a3a86d31a3ea83f5937e5c3867942dc6595b
run_command: |
  # Interactive single-stream serving point (the live :4000 gateway), NOT the throughput run.
  # Differs from the conc-32 benchmark: max-model-len 163840 (max usable ctx, see Notes),
  # max-num-seqs 1, gpu-memory-utilization 0.95, + minimax_m2 reasoning/tool-call parsers.
  docker run -d --gpus all --ipc=host -p 4000:8000 --name serving-minimax-m27-reap \
    -v ~/Desktop/reap-nvfp8/models/MiniMax-M2.7-REAP-172B-A10B-NVFP4-GB10:/model:ro \
    vllm/vllm-openai:nightly-aarch64 \
    /model \
    --host 0.0.0.0 --port 8000 --max-model-len 163840 \
    --gpu-memory-utilization 0.95 --max-num-seqs 1 \
    --kv-cache-dtype fp8 \
    --trust-remote-code \
    --reasoning-parser minimax_m2 --enable-auto-tool-choice --tool-call-parser minimax_m2 \
    --served-model-name minimax-m27-reap-nvfp4
  python3 scripts/bench-serving.py --base-url http://localhost:4000 \
    --model minimax-m27-reap-nvfp4 \
    --dataset benchmark_data/ShareGPT_V3_unfiltered_cleaned_split.json \
    --num-prompts 500 --max-seconds 300 --concurrency 1 --max-tokens 256
---

**The live interactive gateway point — maximum usable context, single stream.** Same community NVFP4
(W4A4) checkpoint as the conc-32 throughput run ([base config]), but measured as it is actually
*deployed*: one sequence at a time, the largest context that fits, `--gpu-memory-utilization 0.95`, and
the `minimax_m2` reasoning + tool-call parsers wired up for agentic use. This is the container that stays
up on `:4000`.

**Result (conc-1 ShareGPT, 160K ctx):** prefill **26.76 tok/s**, decode **25.44 tok/s**, **30/500
prompts** in the 300 s cap (`hit_time_cap=true`), **0 errors**. ttft_median 9.71 s and tpot_median 0.0
are buffered-reasoning artifacts of the `minimax_m2` parser (the whole reasoning trace is held then
flushed), so the aggregate tok/s are the valid headline, not the per-token medians. Single-stream decode
(25 tok/s) is roughly a quarter of the conc-32 aggregate (112 tok/s) — expected: at conc-1 there is no
batching to amortise the 92 GiB weight read per decoded token, and MiniMax emits long reasoning traces
before answering. Streaming works end-to-end (reasoning deltas then the answer + `finish_reason: stop`).

**Maximum usable context = 160K, NOT the architectural 192K.** The model's `max_position_embeddings` is
196,608, but the KV cache doesn't fit at conc-1 on this box: at util 0.95 only **~20.3 GiB KV** is left
after the 92.2 GiB weights, and full 196,608 tokens needs **23.25 GiB** (vLLM's own estimate: max
~171,800 tokens). Pushing util past 0.95 to claw back the difference would leave <3 GB system headroom
and risk OOM during generation. So this serves at **163,840 (160K)** — a clean value just under the
profiling estimate, with margin against run-to-run profiling variance (it gave 180,176 KV tokens / 1.10×
concurrency headroom).

**Memory: ~121 GB used (1.2 GB free of 127.6 GB).** This is the practical ceiling for this checkpoint on
the 121 GB-usable box — weights alone are 92 GiB, and the 160K KV reservation consumes most of the rest.

**Pair:** throughput sibling at [base config]({{ '/configs/minimax-m27-reap-172b-vllm-nvfp4/' | relative_url }})
(conc-32, 65536 ctx). Same `engine_image`, same checkpoint, same cutlass serve recipe — only the operating
point (context / concurrency / util / parsers) differs.
