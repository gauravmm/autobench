---
title: Qwen3.5-122B-A10B · vLLM · int4-AutoRound-EC · conc 8
model: Qwen/Qwen3.5-122B-A10B
company: Alibaba
family: Qwen
params: 122B / 10B (MoE)
engine: vLLM
quant: int4-AutoRound-EC
quant_rationale: shieldstar's int4 AutoRound-EC (error-corrected AutoRound) base, served WITHOUT the DFlash drafter — the non-speculative counterpart to qwen3-5-122b-a10b-vllm-int4-autoround-dflash-c8. The DFlash config is BLOCKED (vLLM can't unify the hybrid GDN+full-attn KV page sizes WITH a draft KV spec); the Notes there suspected the draft KV spec is what tips unification over, so a base-only run is the test of that hypothesis. Individual-uploader repo (normally a BLOCK), added at the user's explicit request alongside the DFlash recipe.
source_repo: shieldstar/Qwen3.5-122B-A10B-int4-AutoRound-EC
download_url: https://huggingface.co/shieldstar/Qwen3.5-122B-A10B-int4-AutoRound-EC
context: 262144
modalities: [text]
mm_served: false
concurrency: 8
tags: [qwen3.5-122b-a10b, Alibaba, Qwen, int4-AutoRound-EC, 41-130B, conc-8]
status: done
prefill_toks: 104.22
decode_toks: 85.5
mem_gb: 106.58
mem_source: system MemAvailable delta (10s sampling) — int4 weights 62.66 GiB + GDN/full-attn KV (262K ctx, conc-8)
completed_at: 2026-06-23 14:54 +08
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:68e23ddd982ad5642e21354c2242a3a86d31a3ea83f5937e5c3867942dc6595b
run_command: |
  # Same base as the DFlash config, with --speculative-config DROPPED. Served via the wrapper (durable
  # log + MemAvailable mem). Run cleanly — the hybrid GDN+full-attn KV UNIFIES once the draft spec is gone.
  scripts/bench-vllm-serving.sh shieldstar/Qwen3.5-122B-A10B-int4-AutoRound-EC 262144 8 500 900 256 \
    --trust-remote-code --dtype bfloat16 --max-num-batched-tokens 32768
  # = vllm/vllm-openai:nightly-aarch64, --gpu-memory-utilization 0.85 --max-num-seqs 8 (wrapper defaults).
  # 305/500 prompts (hit 900 s cap), 0 errors. ready after 762 s (62.66 GiB weights, ~8 min load from disk).
  # Arch Qwen3_5MoeForConditionalGeneration; int4 AutoRound served via AutoGPTQ MarlinLinearKernel +
  # int_wna16 MARLIN MoE backend; GDN on Triton/FLA. TTFT median 459 ms, TPOT median 88.0 ms.
---

**DONE — Qwen3.5-122B-A10B int4-AutoRound-EC WITHOUT DFlash serves cleanly.** The non-speculative
counterpart to the [blocked DFlash config]({{ site.baseurl }}/configs/qwen3-5-122b-a10b-vllm-int4-autoround-dflash-c8/) — and it
**resolves the open question that page left**: the draft's KV spec was indeed the trigger for the
unification failure.

> **KV unification — hypothesis CONFIRMED.** The DFlash run BLOCKED at vLLM's KV-cache page-size
> unification for `{GDN linear-attn + full-attn + DFlash draft}`; its Notes flagged the **draft's KV spec
> as the prime suspect**. Dropping `--speculative-config` removes that spec, and the model **loads and
> serves with no `unify_kv_cache_spec_page_size` assertion**. So the hybrid GDN + full-attn cache unifies
> fine **on its own** — it is specifically the **third (DFlash draft) KV spec** that vLLM can't reconcile
> with the two-way hybrid. The wall is the draft, not the base hybrid.

- **Result (conc 8):** prefill 104.2 / decode **85.5** tok/s aggregate; **305/500** prompts (hit the 900 s
  cap), **0 errors**; peak mem **106.58 GB**. TTFT median 459 ms, **TPOT median 88.0 ms**. Modest for a
  122B/10B MoE, but this is a large int4 model on a single GB10 — weights alone are 62.66 GiB.
- **Loads via:** arch `Qwen3_5MoeForConditionalGeneration`; int4 AutoRound served through AutoGPTQ
  `MarlinLinearKernel` + `int_wna16` MARLIN MoE backend; GDN layers on the Triton/FLA kernel. ~8 min to
  load 62.66 GiB from disk (ready after 762 s); the checkpoint (67 GiB) exceeds 90% of available RAM, so
  vLLM streams it shard-by-shard.
- **Repo:** [`shieldstar/Qwen3.5-122B-A10B-int4-AutoRound-EC`](https://huggingface.co/shieldstar/Qwen3.5-122B-A10B-int4-AutoRound-EC),
  individual-uploader, run per the user's explicit request (same exception as the DFlash sibling /
  cosmicproc). **Qwen3.5 is superseded by Qwen3.6** — a standalone large-MoE datapoint, not part of the
  core list. The DFlash-accelerated variant stays BLOCKED (see sibling + `notes/INCOMPATIBILITIES.md`).
