---
title: Gemma 4 26B-A4B · vLLM · NVFP4 + MTP · conc 256 (collapse — the ceiling)
model: google/gemma-4-26B-A4B-it
company: Google
family: Gemma
params: 26B / 4B (MoE)
engine: vLLM
speculative: MTP (Google assistant drafter)
quant: NVFP4
quant_rationale: NVIDIA NVFP4 base (modelopt) + Google's official MTP assistant drafter via vLLM's native gemma-4 MTP path. c256 point of the beyond-c32 ceiling-finding extension — this is the run that FOUND the ceiling (latency/scheduler collapse near the 121 GB memory wall).
source_repo: nvidia/Gemma-4-26B-A4B-NVFP4
download_url: https://huggingface.co/nvidia/Gemma-4-26B-A4B-NVFP4
context: 65536
modalities: [text, image]
mm_served: false
concurrency: 256
tags: [gemma-4-26b-a4b, Google, Gemma, NVFP4, 16-40B, conc-256]
status: done
prefill_toks: 1.55
decode_toks: 0.15
mem_gb: 118.29
mem_source: system MemAvailable delta (10s sampling) — near the 121 GB unified ceiling (util 0.85 KV reservation + larger-batch runtime buffers)
spec_acceptance: mean acceptance length 2.75 (2.73-2.79) · avg draft acceptance 58% · per-position ~0.77/0.57/0.41 (draft stayed healthy — the collapse is scheduler/latency, not draft quality)
measured_on: 2026-07-04
completed_at: 2026-07-04 11:04 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:e414712fdc04f61d98ccc58cb61232a0587a8c024544e9e6cf12f97b19b38172
run_command: |
  VLLM_IMAGE=vllm/vllm-openai:nightly-aarch64 scripts/bench-vllm-serving.sh nvidia/Gemma-4-26B-A4B-NVFP4 65536 256 1000 900 256 \
    --speculative-config '{"method":"mtp","model":"google/gemma-4-26B-A4B-it-assistant","num_speculative_tokens":3}'
  # COLLAPSE: 9/1000 completed, 512 errors (client TimeoutError), hit 900s cap (wall 1492.2s incl. in-flight timeouts).
  # TTFT median 13349.7 ms, TPOT median 252.1 ms, req thr 0.006/s. ready after 295s. Peak mem 118.29 GB (near 121 ceiling).
---

**This is the ceiling. At conc 256 the gemma-4 26B-A4B MTP line collapses** — the run that answers "where does the still-climbing curve stop." Context held at 65536, same recipe as c1–c128.

- **Collapse, not a throughput point:** only **9/1000 prompts completed, 512 errored** (client `TimeoutError`), TTFT median **13.3 s**, aggregate decode **0.15 tok/s**. This point is **excluded from the throughput curve** — c128 (1380 tok/s) is the last healthy gemma-mtp reading. Plotting 0.15 would be meaningless; the value here is the *finding*, not the number.
- **Two walls hit at once:**
  1. **Memory** — peak **118.29 GB** against the 121 GB unified ceiling (c64 110.6 → c128 114.4 → c256 118.3, ~4 GB/doubling). Almost no headroom left.
  2. **Scheduler/latency** — the MTP spec path pins `max_num_scheduled_tokens=2496` (vLLM warns: "Consider increasing max_num_batched_tokens"). With 256 concurrent seqs, each step advances only ~10 tokens/seq → TTFT explodes to 13 s → the client times requests out en masse. The engine itself kept drafting healthily (~58% acceptance, per-pos 0.77/0.57/0.41) and served ~290 tok/s in bursts, so **draft quality is NOT the cause** — it is queueing collapse under a fixed draft-token budget colliding with the memory wall.
- **The ceiling is memory-bound in the sense that matters:** by c256 there is no room to raise `--gpu-memory-utilization` or `--max-num-batched-tokens` enough to relieve the scheduler without blowing past 121 GB. **c128 is the practical top for this line on GB10 at 65536 ctx.**
- **Reproducibility note:** a future run *could* try to rescue c256 by raising `--max-num-batched-tokens` (relieves the 2496 cap) — but that costs KV memory the 118 GB peak doesn't have. Recorded here as the standard-recipe ceiling.
- **Image (pinned):** `vllm/vllm-openai:nightly-aarch64` @ `sha256:e414712fdc04…`. Ready after 295 s (loaded fine — the failure is at serving time, not load).
</content>
</invoke>
