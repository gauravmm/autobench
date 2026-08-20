---
title: Qwen3.8-27B · vLLM · NVFP4 + MTP · conc-128
model: Qwen/Qwen3.8-27B
company: Alibaba
family: Qwen
params: 27B (dense, hybrid linear-attn)
engine: vLLM
speculative: MTP
quant: NVFP4
quant_rationale: Same unsloth NVFP4 checkpoint plus its in-repo BF16 MTP head, at conc-128 — the batch where the speculative speedup finally reaches zero and the draft head starts costing memory.
source_repo: unsloth/Qwen3.8-27B-NVFP4
download_url: https://huggingface.co/unsloth/Qwen3.8-27B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 128
tags: [qwen3.8-27b, Alibaba, Qwen, NVFP4, 16-40B, conc-128]
status: done
prefill_toks: 448.96
decode_toks: 351.19
mem_gb: 114.67
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV reservation (util 0.85) + MTP head + 128-slot draft buffers
spec_acceptance: ~55% avg draft acceptance (last-20 samples 48.7–60.6%, median 54.1%) · mean acceptance length ~2.64 (of a possible 4.0) · per-position ~0.75 / 0.52 / 0.37 (num_speculative_tokens=3)
measured_on: 2026-08-21
completed_at: 2026-08-21 03:48 +0800
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:677afd5bf3b4bb9881f91e107af7098f8410726b4c05b25cb4a815900b398204
run_command: |
  # conc-128 point with the in-repo MTP head. Same recipe as conc-32 except --max-num-seqs.
  scripts/bench-vllm-serving.sh unsloth/Qwen3.8-27B-NVFP4 65536 128 1000 900 256 \
    --trust-remote-code --dtype bfloat16 \
    --speculative-config '{"method":"mtp","num_speculative_tokens":3}'
  # 1000/1000 prompts in 680.6 s — DRAINED the dataset, did NOT hit the 900 s cap. 0 errors.
  # ready after 305 s. TTFT median 14986.3 ms (!), TPOT median 282.8 ms.
---

**MTP reaches zero at conc-128: +1.4% throughput, 12× the TTFT, and 8.5 GB more memory.**

- **Result (conc 128):** decode **351.19** tok/s vs the
  [conc-128 base]({{ site.baseurl }}/configs/qwen3-8-27b-nvfp4-vllm-c128/)'s 346.23 — **+1.4%, inside
  the noise.** Both runs drained the identical 1000 prompts (305,551 prompt tokens): base **686.3 s**,
  MTP **680.6 s** — a **0.8% end-to-end difference**. Speculation buys nothing here. 0 errors.
- **The speculative curve, complete and terminated:**

  | conc | base decode | +MTP decode | speedup | base TTFT | +MTP TTFT |
  |------|-------------|-------------|---------|-----------|-----------|
  | 1    | 11.16  | 21.35  | **+91%** | 177 ms | 264 ms |
  | 2    | 20.11  | 38.95  | **+94%** | 301 ms | 408 ms |
  | 4    | 38.62  | 70.74  | **+83%** | 315 ms | 436 ms |
  | 8    | 75.04  | 126.68 | **+69%** | 345 ms | 476 ms |
  | 16   | 128.60 | 194.99 | **+52%** | 374 ms | 617 ms |
  | 32   | 209.97 | 274.74 | **+31%** | 456 ms | 857 ms |
  | 64   | 283.72 | 324.08 | **+14%** | 658 ms | 1445 ms |
  | 128  | 346.23 | 351.19 | **+1.4%** | 1251 ms | **14986 ms** |

  A flat ~90–95% plateau below c4, then a decay of roughly 15 points per doubling that hits zero at
  **c128**. The prediction made from the c64 point — zero somewhere in c128–c256 — lands at the near end.
- **TTFT blows up to 15 seconds.** 1251 → **14,986 ms**, a **12× regression**, where every batch up to
  c64 paid only a 36–120% premium. At 128 slots the draft forward for the whole batch sits in front of
  every incoming prefill, so new requests wait behind a full round of speculation that is no longer
  earning anything back.
- **This is the one point on the sweep where MTP costs real memory: 114.7 GB vs the base run's 106.2**
  (+8.5 GB), against a 121 GB unified ceiling — roughly **6 GB of headroom left**. Everywhere else on
  the sweep the two variants sat within the same 103–107 GB band, because the static reservation
  dominates. At 128 slots the per-slot draft buffers finally became a visible line item.
- **Acceptance ~55%** (last-20 samples 48.7–60.6%, median 54.1%), mean acceptance length **~2.64**,
  per-position **0.75 / 0.52 / 0.37** — unchanged. **Eight MTP runs now span ~52–58% with no trend in
  concurrency**, which settles it: acceptance is workload-driven, and the collapse in speedup is purely
  about how much idle compute the batch leaves behind, not about the draft head getting worse.
- **Recommendation from the completed curve:** enable MTP at **c1–c16** (+52% to +94%, TTFT premium
  under 65%); it is optional at c32 (+31% for +88% TTFT); **turn it off at c64 and above.**
