---
title: Qwen3.5-122B-A10B · vLLM · int4-AutoRound-EC + DFlash · conc 8
model: Qwen/Qwen3.5-122B-A10B
company: Alibaba
family: Qwen
params: 122B / 10B (MoE)
engine: vLLM
speculative: DFlash (z-lab drafter, rev 6c7242c pinned)
quant: int4-AutoRound-EC
quant_rationale: shieldstar's int4 AutoRound-EC (error-corrected AutoRound) base + z-lab's DFlash speculative drafter (z-lab/Qwen3.5-122B-A10B-DFlash), per a user-supplied DGX Spark recipe (builder eugr). Both are INDIVIDUAL-uploader repos (normally a BLOCK per the trusted-repo policy) — added at the user's explicit request. Revives the Qwen3.5 line that was archived as superseded by Qwen3.6; run as a standalone large-MoE spec-decode datapoint.
source_repo: shieldstar/Qwen3.5-122B-A10B-int4-AutoRound-EC
download_url: https://huggingface.co/shieldstar/Qwen3.5-122B-A10B-int4-AutoRound-EC
context: 262144
modalities: [text]
mm_served: false
concurrency: 8
tags: [qwen3.5-122b-a10b, Alibaba, Qwen, int4-AutoRound-EC, 41-130B, conc-8]
status: done
prefill_toks: 115.66
decode_toks: 107.43
mem_gb: 105.2
mem_source: system MemAvailable delta from idle baseline (10s sampling); vLLM 0.85 reservation, not the resident footprint
measured_on: 2026-06-24
completed_at: 2026-06-24 08:07 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:68e23ddd982ad5642e21354c2242a3a86d31a3ea83f5937e5c3867942dc6595b
run_command: |
  # UNBLOCKED 2026-06-24 by PINNING the DFlash draft to the known-good revision 6c7242c (num_kv_heads 4,
  # layers 4, sliding_window 2048). The prior block was the upstream draft bump to bce6f76 (kv_heads 8,
  # layers 6, sliding_window 4096), which doubled the draft's attention page size so it could not unify
  # with the base's mamba/GDN layers. With the old draft arch, vLLM pads cleanly:
  #   "Setting attention block size to 2144 tokens to ensure that attention page size is >= mamba page size"
  # nightly-aarch64 (vLLM 0.23.1, rewritten KV unifier). Pre-downloaded base + pinned draft rev to cache;
  # HF_HUB_OFFLINE=1. num_speculative_tokens:5 per the recipe. Dropped recipe extras irrelevant to a
  # throughput bench (custom .jinja, fastsafetensors, tool/reasoning parsers, override-gen-config).
  docker run -d --name vllm-qwen35-122b --gpus all --ipc=host -p 8000:8000 \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    --env HF_TOKEN=*** --env HF_HUB_OFFLINE=1 \
    --env VLLM_ENABLE_CUDAGRAPH_GC=1 --env FLASHINFER_DISABLE_VERSION_CHECK=1 \
    --env VLLM_USE_FLASHINFER_SAMPLER=1 --env VLLM_MARLIN_USE_ATOMIC_ADD=1 \
    vllm/vllm-openai:nightly-aarch64 shieldstar/Qwen3.5-122B-A10B-int4-AutoRound-EC \
    --served-model-name qwen --host 0.0.0.0 --port 8000 \
    --max-model-len 262144 --gpu-memory-utilization 0.85 \
    --max-num-batched-tokens 32768 --max-num-seqs 8 \
    --dtype bfloat16 --trust-remote-code \
    --speculative-config '{"method":"dflash","model":"z-lab/Qwen3.5-122B-A10B-DFlash","revision":"6c7242c934a9870d7c59c05240bdbb2467cc1394","num_speculative_tokens":5}' \
    --enable-prefix-caching --enable-chunked-prefill
  python3 scripts/bench-serving.py --base-url http://localhost:8000 --model qwen \
    --dataset benchmark_data/ShareGPT_V3_unfiltered_cleaned_split.json \
    --num-prompts 500 --max-seconds 900 --concurrency 8 --max-tokens 256
---

**DONE 2026-06-24 — UNBLOCKED by pinning the DFlash draft to the known-good revision.** Re-run from the
user's `…-v2-pinned-dflash.yaml` recipe, which pins `z-lab/Qwen3.5-122B-A10B-DFlash` to
`6c7242c934a9870d7c59c05240bdbb2467cc1394`. The 2026-06-23 block (below) was caused entirely by the
*upstream draft bump* (`bce6f76`: num_kv_heads 4→8, layers 4→6, sliding_window 2048→4096), which doubled
the draft's attention page size so vLLM could not unify it with the base's GDN/mamba layers. Pinning back
to the old draft arch (kv_heads 4, layers 4, sw 2048) makes the page sizes pad cleanly and it boots +
serves. **Standalone Qwen3.5 large-MoE spec-decode datapoint** (the line was [archived as superseded by
Qwen3.6]); kept at the user's explicit request.

**Result (conc 8, ShareGPT, 15-min cap):** prefill **115.66 tok/s**, decode **107.43 tok/s**, 385
completed, **0 errors**, hit the time cap at 915 s. TTFT median 681 ms, TPOT median 67.5 ms.
- **DFlash speedup: ~1.26×** decode vs the non-spec base (85.5 → 107.43 tok/s at the same conc-8 —
  see [`qwen3-5-122b-a10b-vllm-int4-autoround`]({{ site.baseurl }}/configs/qwen3-5-122b-a10b-vllm-int4-autoround/)).
- **Spec acceptance:** mean acceptance length **~3.2–3.3** of `num_speculative_tokens=5`; **avg draft
  acceptance ~44%** (per-position 0.78 / 0.56 / 0.39 / 0.29 / 0.21 — healthy first-token accept, expected
  decay). That's in the **<50% band typical for a separate (non-MTP/EAGLE) draft on general ShareGPT
  chat** (BENCHMARKING.md rule of thumb) — well below a code workload, but enough for a real 1.26× win.
- **Memory:** `mem_gb 105.2` is the vLLM **0.85 unified-mem reservation**, not the resident footprint.
  Resident breakdown from logs: **model 63.71 GiB**, **KV cache 27.72 GiB** (GPU KV = 800,129 tokens →
  max concurrency 3.05× at 262K ctx), CUDA-graph pool 0.3 GiB. Load took 463 s (15 shards, ~67 GB).
- **Boot:** `Resolved architecture: DFlashDraftModel`; `Setting attention block size to 2144 tokens to
  ensure that attention page size is >= mamba page size` — the unification step that hard-asserted on the
  bad draft rev now succeeds. MarlinLinearKernel (linear) + MARLIN WNA16 MoE, FLASH_ATTN, cudagraphs on.

> **Replaced by → `Qwen/Qwen3.6-35B-A3B`** (sparse-MoE 3.6 counterpart; benchmarked base + native MTP —
> see `qwen3-6-35b-a3b-vllm-fp8`). Qwen's 3.6 line (27B dense + 35B-A3B MoE) outperforms the entire 3.5
> family at a fraction of the size — per [qwen.ai/blog](https://qwen.ai/blog?id=qwen3.6-27b) even the 27B
> dense beats the 397B 3.5 model — which is why this 122B/10B 3.5 MoE was archived. This page exists only
> to capture the user-requested int4-AutoRound-EC + DFlash datapoint; for current Qwen use the 3.6 configs.

- **Stack:** shieldstar `int4-AutoRound-EC` (error-corrected AutoRound 4-bit) base + z-lab **DFlash**
  speculative drafter (`z-lab/Qwen3.5-122B-A10B-DFlash`, `method: dflash`), at **262K context**, 32K
  prefill budget, `--max-num-seqs 8` (conc-8). Qwen general-thinking sampler (`temp 1.0 / top_p 0.95 /
  top_k 20`, `presence_penalty 1.5`), `reasoning-parser qwen3`, `tool-call-parser qwen3_coder`.
- **Image:** the recipe's `--tf5` build (vLLM 0.22 + transformers 5.x) → our **`autobench-vllm-022-tf`**
  (`VLLM_IMAGE=`). Env from the recipe: `VLLM_ENABLE_CUDAGRAPH_GC=1`, `FLASHINFER_DISABLE_VERSION_CHECK=1`,
  `VLLM_USE_FLASHINFER_SAMPLER=1`, `VLLM_MARLIN_USE_ATOMIC_ADD=1`.
- **Recipe metadata (from source):** quant_bits 4 (auto-round, int4), num_kv_heads 2, head_dim 256,
  num_layers 48, `solo_only: true`, `max_nodes: 1`, container `vllm-node-tf5`, mod
  `fix-qwen3.5-enhanced-chat-template`.

---

## Prior block (2026-06-23) — root cause, RESOLVED by the draft pin above. Kept for the record.

> **Resolved 2026-06-24:** the assert below was triggered by the *upstream* DFlash rev `bce6f76`, not by
> the base model. Pinning the draft to `6c7242c` (old arch) sidesteps it — see the DONE section at top.
> The analysis here remains valid as the explanation of *why* a draft-arch bump breaks unification.

**Every preliminary risk flag cleared — the block is a real engine limitation, found only after the model
loads.** Order of investigation:

- **Trust ✓** — `shieldstar` int4-AutoRound-EC base: **42,785 dl/30d**, has `config.json` +
  `quantization_config.json` + chat template in `tokenizer_config`; `z-lab` DFlash drafter: 1.55 GB,
  4502 dl, 17 likes. Both corroborated (same individual-uploader exception as cosmicproc, on the user's
  explicit recipe). Pre-downloaded both to cache (`HF_HUB_OFFLINE=1`, avoids the second-egress cap).
- **DFlash support ✓** — `method: dflash` is **natively in vLLM 0.22+** (`vllm/v1/spec_decode/dflash.py`;
  registered methods include `dflash`). Not a custom plugin. Needs explicit `num_speculative_tokens`
  (set 8, matching z-lab's block-size; the recipe omitted it → first failure, a `pydantic ValidationError`,
  fixed).
- **Truncated fields ✓** — pinned the DFlash `revision` to the repo's current sha
  `bce6f76cef2027552bed4a8a1bc9c449def48f05`; dropped the custom `qwen3.5-enhanced.jinja` (the base repo
  ships a chat template) and the tool/reasoning/override-gen-config flags (irrelevant to a throughput
  bench) — de-risked per ponytail.
- **Weights load ✓** — int4 AutoRound runs on GB10: `MarlinLinearKernel` (linear) + `MARLIN` WNA16 MoE
  backend selected, FLASH_ATTN, 15 shards (~67 GB) loaded. Fit is fine (~74 GB weights + small KV; only
  2 KV heads).

**The hard blocker — KV-cache page-size unification fails for `{GDN linear-attn + full-attn + DFlash draft}`:**
Qwen3.5-122B-A10B is a **hybrid** model — Gated-DeltaNet **linear-attention** layers (`qwen_gdn_linear_attn`,
mamba-style state cache) interleaved with **full-attention** layers — plus the DFlash draft's own KV spec.
vLLM must unify all these into one page size, and can't:
- **vLLM 0.22.0** (the recipe's `--tf5` build, `autobench-vllm-022-tf`): hard
  `assert new_spec.page_size_bytes == max_page_size` in `unify_kv_cache_spec_page_size` → fails immediately.
- **vLLM 0.23.1** (`nightly-aarch64`, the cu130-nightly successor — substituted because its KV unifier was
  rewritten to pad mismatched pages): gets **further** — logs `Setting attention block size to 2192 …`
  + `Padding mamba page size by 0.55% …` — but still trips a **residual**
  `assert page_size_bytes == max_page_size` (`kv_cache_utils.py:1077`) inside `get_kv_cache_groups`. It
  fails first in the cudagraph-memory-profiling path (`profile_cudagraph_memory →
  _init_minimal_kv_cache_for_profiling`); with **`--enforce-eager`** (cudagraph disabled, profiling
  skipped) it then fails at the **same assert in the real path** (`_initialize_kv_caches →
  get_kv_cache_configs`). So `--enforce-eager` does **not** bypass it — the padding doesn't reach exact
  page-size equality for this spec combination.

**Conclusion:** needs an upstream vLLM fix to `unify_kv_cache_spec_page_size` (handle hybrid
linear+full-attention **with** a spec-decode draft KV spec), or a source patch (declined — patching the
sanity assert risks a wrong KV layout / silent corruption, against the trusted-path policy). Same *family*
of "vLLM assertion on heterogeneous cache groups" that blocks Gemma-4 MTP, but a different exact assert
(KV page size vs attention-head grouping). Re-test when vLLM ships a hybrid+spec KV-unification fix.

**Note:** Qwen3.5 is superseded by Qwen3.6 (see the callout above); this was a user-requested standalone
datapoint, not part of the core list. **Follow-up done & hypothesis CONFIRMED:** the base model serves
fine **without** DFlash — see [`qwen3-5-122b-a10b-vllm-int4-autoround`]({{ site.baseurl }}/configs/qwen3-5-122b-a10b-vllm-int4-autoround/)
(decode 85.5 tok/s, conc-8, 0 errors). Dropping the `--speculative-config` removes the draft's KV spec and
the hybrid GDN+full-attn cache **unifies cleanly** — proving it is specifically the **third (DFlash draft)
KV spec** that vLLM can't reconcile, not the two-way hybrid base. **Follow-up (2026-06-24): the draft KV
spec only fails to unify with the *new* draft arch (`bce6f76`, sw 4096 / 8 kv-heads); pinning the draft to
the *old* arch (`6c7242c`, sw 2048 / 4 kv-heads) pads to an equal page size and serves — so this variant
is now DONE, not blocked.**
