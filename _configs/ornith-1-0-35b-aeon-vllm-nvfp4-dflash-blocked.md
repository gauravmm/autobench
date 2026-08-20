---
title: Ornith-1.0-35B AEON Uncensored · vLLM (aeon-ultimate) · NVFP4 + DFlash · conc 1 — BLOCKED
model: AEON-7/Ornith-1.0-35B-AEON-Ultimate-Uncensored-NVFP4
company: Alibaba
family: Qwen
params: Qwen3.6-35B-A3B base (35B/3B MoE, hybrid GDN+full-attn) · AEON "Ornith 1.0" RL post-train, abliterated
engine: vLLM (aeon-vllm-ultimate custom container, v0.23.0+aeon.sm121a.dflash)
speculative: DFlash (z-lab/Qwen3.6-35B-A3B-DFlash, num_speculative_tokens 6) — BLOCKED at KV unification
quant: NVFP4 (compressed-tensors, nvfp4-pack-quantized)
quant_rationale: AEON's headline config — NVFP4 base + DFlash drafter for a claimed ~1.9× single-stream speedup. The base runs fine (see the conc-32 / conc-1 pages); adding the DFlash draft is what blocks.
source_repo: AEON-7/Ornith-1.0-35B-AEON-Ultimate-Uncensored-NVFP4
download_url: https://huggingface.co/AEON-7/Ornith-1.0-35B-AEON-Ultimate-Uncensored-NVFP4
context: 262144
modalities: [text, image, video]
mm_served: false
concurrency: 1
tags: [ornith-1-0-35b-aeon, Alibaba, Qwen, NVFP4, 16-40B, conc-1]
status: blocked
prefill_toks:
decode_toks:
mem_gb:
mem_source:
measured_on: 2026-06-28
completed_at: 2026-06-28 16:13 +0800
engine_image: ghcr.io/aeon-7/aeon-vllm-ultimate:latest@sha256:be9e05a11da6e72607ab6f3e960993b253b673af0727005122a3266129a518e3
run_command: |
  # BLOCKED — boots through drafter load, then hard-asserts at KV-cache page-size unification.
  # Untrusted image — NO creds, model + drafter READ-ONLY, loopback port.
  docker run -d --name serving-ornith --gpus all --ipc=host \
    -e TORCH_CUDA_ARCH_LIST=12.1a -e CUTE_DSL_ARCH=sm_121a -e VLLM_USE_FLASHINFER_SAMPLER=1 \
    -v ~/ornith/model:/model:ro -v ~/ornith/drafter:/drafter:ro -p 127.0.0.1:8000:8000 \
    --entrypoint vllm ghcr.io/aeon-7/aeon-vllm-ultimate:latest \
    serve /model --served-model-name ornith --host 0.0.0.0 --port 8000 \
    --quantization compressed-tensors --trust-remote-code \
    --max-model-len 262144 --gpu-memory-utilization 0.6 \
    --max-num-seqs 16 --max-num-batched-tokens 16384 \
    --mamba-cache-dtype float32 --enable-prefix-caching --reasoning-parser qwen3 \
    --speculative-config '{"method":"dflash","model":"/drafter","num_speculative_tokens":6}'
  # PARTIAL UNBLOCK ONLY (dodges the page-size assert, not the real blocker): pin the drafter to its
  # pre-"Modal retrain" small-page revision (HF-API verified: num_key_value_heads 4, no sliding window):
  #   --speculative-config '{"method":"dflash","model":"z-lab/Qwen3.6-35B-A3B-DFlash",
  #     "revision":"31977fbe13a8...","num_speculative_tokens":6}'
  # ^ Expected to clear kv_cache_utils.py:1064 but then hit the GDN-rollback wall (vLLM #39273) and/or the
  #   prefix-cache IndexError on DGX Spark (#41884). External draft speculators don't work on a GDN target.
---

> **⚠️ CORRECTION (2026-06-28): the "blocked four ways" conclusion on this page is WRONG — refuted by direct
> measurement on the sibling 35B-A3B checkpoints.** Running the *same* AEON image with the **pre-retrain small-page
> drafter** (`z-lab/Qwen3.6-35B-A3B-DFlash @31977fbe`, 4 kv-heads / sw null), DFlash **boots AND serves cleanly,
> 0 errors across conc 1/8/32, with prefix-caching ON** — on both `AEON-7/Qwen3.6-35B-A3B-heretic-NVFP4` and the
> official `nvidia/Qwen3.6-35B-A3B-NVFP4`. None of the predicted walls fired (no #39273 GDN-rollback crash, no #41884
> prefix-cache IndexError, no NVFP4 acceptance collapse). The small-page pin is a **real end-to-end unblock**, not just
> an assert dodge. The Ornith config itself was not re-run, but it is the same image + target family, so the same lever
> applies. **The real reason to stay on MTP is throughput economics, not a block** — DFlash wins only conc-1 (+8.5% on
> the official model) and loses under load (MTP's ~66%/3-of-3 draft efficiency beats DFlash's ~25%/3.7-of-11). Measured
> pages: [`…official…dflash`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash/),
> [`…heretic…dflash`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-heretic-aeon-vllm-ultimate-dflash/). The original (now-corrected) analysis follows.

**BLOCKED with AEON's *required* (post-04-19, sw 4096 / 8 kv-heads) drafter — DFlash + this hybrid MoE trips the same
KV-cache page-size unification assert that blocked the
[Qwen3.5-122B-A10B DFlash run]({{ site.baseurl }}/configs/qwen3-5-122b-a10b-vllm-int4-autoround-dflash-c8/). The assert is real and reproduces;
what was wrong (see banner) is the claim that the small-page-drafter fix only dodges it — it actually serves.**

**Boot gets all the way through drafter load, then asserts during KV setup:**
- `Resolved architecture: DFlashDraftModel`; `speculative_config=SpeculativeConfig(method='dflash',
  num_spec_tokens=6)`; drafter loaded (EAGLE-style: shares target embed/lm_head, aux layers
  `(2,7,12,17,23,28,33,38)`).
- Then, in `determine_available_memory → profile_cudagraph_memory →
  _init_minimal_kv_cache_for_profiling → get_kv_cache_groups → unify_kv_cache_spec_page_size`:
  ```
  vllm/v1/core/kv_cache_utils.py:1064:  assert new_spec.page_size_bytes == max_page_size
  AssertionError  →  EngineCore init failed (exit 1)
  ```

**Why:** Ornith is a **hybrid** model (Gated-DeltaNet linear-attention + full-attention, plus a mamba/SSM
state cache). Without a draft, vLLM unifies the two KV specs by padding the attention page to the mamba
page (the base conc-32/conc-1 runs log `Setting attention block size to 1072 …` and serve fine). Adding
the **DFlash draft introduces a third KV spec**; on vLLM 0.23 (the AEON fork's base) it cannot reconcile
all three into one page size. This is the **identical failure family** documented in
`notes/INCOMPATIBILITIES.md` and confirmed by the base-vs-draft A/B here (base serves, +draft asserts) —
it is specifically the **draft's KV spec**, not the hybrid base.

**The page-size assert has a known lever — but it is NOT the real blocker here (correction, 2026-06-28).**
The current `z-lab/Qwen3.6-35B-A3B-DFlash` `main` config is `sliding_window: 4096`, `num_key_value_heads: 8`,
`num_hidden_layers: 6` — the *same* big-page shape (sw 4096 / 8 kv-heads) that broke the 122B on its
`bce6f76` rev. The 122B (a **dense** target) was genuinely **unblocked** by pinning the draft to an older
small-page rev (`6c7242c`: sw 2048 / 4 kv-heads), which pads to an equal page size. For this drafter the
**pre-"Modal retrain" revisions** (`31977fbe13a8` "Upload model", `f98dc5c2908b`) are HF-API-verified to have
`num_key_value_heads: 4` and **no sliding window** — the analogous small-page arch, so pinning to them should
clear the `kv_cache_utils.py:1064` assert.

**But Ornith's target is hybrid-GDN, and that's a different, deeper wall than the 122B's.** A web-verified
upstream review (2026-06-28) shows the page-size assert is only the *first* of four blockers for an external
DFlash draft on a Gated-DeltaNet model:
1. **GDN state rollback (vLLM #39273, the root cause):** a GatedDeltaNet layer's recurrent SSM state **cannot
   be rolled back when a speculative token is rejected**, which architecturally breaks *external* draft
   speculators (DFlash, EAGLE3, ngram) on any GDN model. MTP is safe because its head runs *after* the verified
   base step — no draft state to undo. **No drafter revision fixes this.**
2. **Hybrid DFlash path unmerged in vLLM** — base DFlash merged (#38300), but hybrid GDN+full-attn is an
   unchecked tracker item (#46105); the page-size assert is the open issue **#43626**.
3. **Open GB10-specific crash bug #41884** — DFlash + prefix caching → IndexError *specifically on DGX Spark*
   with this exact `z-lab/Qwen3.6-35B-A3B-DFlash` drafter. (Also #41190: TP MTP/DFlash on Qwen3.6 GDN.)
4. **NVFP4 acceptance nose-dive** (Vassallo, blog.davidvassallo.me 2026-05-15, tested this exact model): only
   ~4 of 15 speculative tokens accepted on a quantized target — so even where DFlash boots on NVFP4 the speedup
   evaporates. DFlash's published ~12–18%-over-MTP edge is **B200/bf16 only**.

So the revision pin would likely clear assert #1 and then hit #39273/#41884 — it is **not** the high-confidence
end-to-end unblock the 122B was. This config stays **blocked**.

**Bottom line (CORRECTED):** AEON's headline "~1.9× DFlash" still doesn't reproduce *with the drafter AEON's card
requires* (it asserts at boot) — but DFlash is **not** "blocked four ways." With the small-page drafter it boots and
serves cleanly; the measured truth is that it simply **loses to native MTP on a mixed workload** (wins only conc-1
+8.5%, loses −7%/−26% at conc-8/32) because MTP is far more draft-efficient (~66%/3-of-3 vs ~25%/3.7-of-11). The base
model is fast and stable either way. Trusted recommendation: **native MTP** — not because DFlash is impossible here,
but because it isn't worth an external drafter + a forbidden drafter revision + an untrusted image for a single-stream-only edge.

> **✓ MEASURED — the small-page pin DOES unblock (corrected from "✗ NOT A SIMPLE UNBLOCK"):** pinning the drafter to
> `z-lab/Qwen3.6-35B-A3B-DFlash @31977fbe13a8` (`sw None / 4 kv-heads`) cleared the page-size assert **and ran
> end-to-end with 0 errors** on the sibling 35B-A3B checkpoints (heretic + official). The web-verified upstream walls
> (#39273 GDN-rollback, #41884 DGX-Spark prefix-cache IndexError, Vassallo NVFP4 nose-dive) **did not materialize on the
> AEON fork** — evidently patched in their image. External draft speculators *do* work on this GDN target on this box;
> they're just not throughput-competitive with MTP on mixed prompts.

> Cross-ref: [`qwen3-5-122b-a10b-vllm-int4-autoround-dflash-c8`]({{ site.baseurl }}/configs/qwen3-5-122b-a10b-vllm-int4-autoround-dflash-c8/)
> (same assert, unblocked by a draft-revision pin) and `notes/INCOMPATIBILITIES.md` (hybrid+spec KV
> unification wall).
