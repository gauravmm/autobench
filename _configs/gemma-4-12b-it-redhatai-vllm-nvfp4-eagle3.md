---
title: Gemma 4 12B · vLLM · NVFP4 + EAGLE3
model: google/gemma-4-12B-it
company: Google
family: Gemma
params: 12B (dense)
engine: vLLM
speculative: EAGLE3
quant: NVFP4
quant_rationale: Would stack RedHatAI/gemma-4-12B-it-NVFP4 (the done base/MTP quant) with a size-matched EAGLE3 head, mirroring the 26B-A4B/31B EAGLE3 rows — but no trusted, vLLM-compatible 12B EAGLE3 head exists (see below).
source_repo: RedHatAI/gemma-4-12B-it-NVFP4
download_url: https://huggingface.co/RedHatAI/gemma-4-12B-it-NVFP4
context: 65536
modalities: [text, image, audio, video]
mm_served: false
concurrency: 32
tags: [gemma-4-12b, Google, Gemma, NVFP4, 5-15B, conc-32]
status: blocked
prefill_toks:
decode_toks:
mem_gb:
mem_source:
measured_on: 2026-07-02
completed_at:
run_command: |
  # BLOCKED on draft availability, NOT the harness/image. The NVFP4 target loads + serves fine on
  # nightly-aarch64 (see the 12B NVFP4 base/MTP rows). The problem is the EAGLE3 head:
  #  1. RedHatAI ships gemma-4 EAGLE3 heads ONLY for 26B-A4B and 31B — the 12B name is 404.
  #  2. deepseek-ai/eagle3_gemma4_12b_ttt7 exists (trusted lab) but is packaged as a raw
  #     transformers/SpecForge model (architectures=["Gemma4Eagle3Model"]) that vLLM's spec-decode
  #     path does NOT support — it rejects at config validation (see Notes for the exact error).
  #  3. BCCard/MoAI-gemma-4-12B-it-speculator.eagle3 IS in the vLLM-compatible speculators format
  #     (architectures=["Eagle3DraftModel"] + speculators_config) and would load — but it is an
  #     untrusted 0-download / 0-like raw training dump, blocked per the trusted-repo policy.
  # Command that FAILED (deepseek head, nightly-aarch64):
  scripts/bench-vllm-serving.sh RedHatAI/gemma-4-12B-it-NVFP4 65536 32 1000 900 256 \
    --speculative-config '{"method":"eagle3","model":"deepseek-ai/eagle3_gemma4_12b_ttt7","num_speculative_tokens":3}'
---

## BLOCKED — no trusted, vLLM-compatible 12B EAGLE3 head exists (draft-availability block)

The 12B NVFP4 row already has **base (503.8)** and **+MTP (782.4)**; only the EAGLE3 cell is open. Filling
it needs an EAGLE3 speculator that is (a) size-matched to Gemma-4 12B, (b) packaged in vLLM's
speculators format, and (c) from a trusted source. **No head satisfies all three.**

- **RedHatAI ships no 12B head.** The convention `RedHatAI/gemma-4-12B-it-speculator.eagle3` is **404**
  (RedHatAI publishes gemma-4 EAGLE3 only for 26B-A4B and 31B, both benchmarked here).
- **`deepseek-ai/eagle3_gemma4_12b_ttt7` (trusted lab) is the WRONG PACKAGING for vLLM.** Its config
  declares `architectures: ["Gemma4Eagle3Model"]` (a raw transformers/SpecForge draft class), which vLLM's
  spec-decode path does not register. Attempting it dies at config validation before any weight load:

  ```
  ValidationError: 1 validation error for SpeculativeConfig
  Value error, Model architectures ['Gemma4Eagle3Model'] are not supported for now.
  ```

  vLLM only consumes the **`speculators`-library** packaging — `architectures: ["Eagle3DraftModel"]` +
  a `speculators_config` block (+ `auto_map` → `config.Eagle3SpeculatorConfig`), which is exactly what
  the working RedHatAI 26B-A4B/31B heads carry. The deepseek head has none of that. No vLLM flag adds a
  `Gemma4Eagle3Model` class; it's a repackaging/retrain job, not a harness fix. (The deepseek head is
  likely SGLang/SpecForge-native — runnable there, but that would break the same-engine 12B
  base/MTP/EAGLE3 comparison, so it was not pursued.)
- **`BCCard/MoAI-gemma-4-12B-it-speculator.eagle3` IS vLLM-compatible but untrusted.** It's in the correct
  speculators format (`Eagle3DraftModel` + `speculators_config`) and would load — but it's a **0-download,
  0-like** repo that ships raw training artifacts (`optimizer_state_dict.pt`, `training_state.json`,
  `val_metrics.json`), i.e. an unpolished training dump from a small org. Blocked per the trusted-repo
  policy (weaker provenance than even the cosmicproc NVFP4 base, which had 61k dl/mo when run on request).

**So this is blocked on sourcing a trusted, correctly-packaged draft, not on the harness or an image
wall** — the NVFP4 target itself serves fine (base/MTP rows). It unblocks if RedHatAI (or a trusted lab)
publishes a 12B EAGLE3 head in speculators format. Meanwhile **12B spec-decode is already covered by MTP**
(782.4 tok/s, +55% over base), and the "NVFP4 MTP beats NVFP4 EAGLE3 on the heavier models" story is
proven on the 26B-A4B and 31B rows regardless.

**RE-VERIFIED 2026-07-04 (HF API + raw configs, not just search) — unchanged, still blocked:**
- `deepseek-ai/eagle3_gemma4_12b_ttt7` `config.json` still `architectures: ["Gemma4Eagle3Model"]` with
  **no** `speculators_config`/`auto_map` → vLLM still rejects; vLLM has not added that class.
- `BCCard/MoAI-gemma-4-12B-it-speculator.eagle3` re-checked: **is** correct vLLM format
  (`Eagle3DraftModel` + `speculators_config` + `auto_map`, bf16 draft, targets a `gemma-4-12B`
  Gemma4Unified verifier — would pair with the NVFP4 target). But still **0 downloads / 0 likes**,
  created 2026-07-02, ships a raw training dump (`optimizer_state_dict.pt`, `training_state.json`,
  `val_metrics.json`) + a `config.py` executed via `auto_map`/trust-remote-code. **Untrusted — user
  declined to run it as an exception (2026-07-04); left blocked.**
- No RedHatAI 12B head (still only 26B-A4B + 31B). AEON-7 now ships a **31B** `eagle3-NVFP4` repackage
  and thoughtworks a **31B** head, but **no 12B** anywhere trusted. (Trusted-but-off-vLLM alternative:
  the deepseek SpecForge head on **SGLang** — not pursued, breaks the same-engine 12B comparison.)
