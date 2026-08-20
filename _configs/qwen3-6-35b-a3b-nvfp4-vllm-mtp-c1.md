---
title: Qwen3.6-35B-A3B · vLLM · NVFP4 + MTP · conc 1
model: Qwen/Qwen3.6-35B-A3B
company: Alibaba
family: Qwen
params: 35B / 3B (MoE)
engine: vLLM
speculative: MTP
quant: NVFP4
quant_rationale: Single-stream point of the Qwen3.6-35B-A3B NVFP4 + native-MTP sweep — same stack as the conc-32 run (nvidia ModelOpt NVFP4 base on marlin + in-repo MTP head on triton). Best-case MTP latency with no batch contention; the per-stream TPOT here is the headline number.
source_repo: nvidia/Qwen3.6-35B-A3B-NVFP4
download_url: https://huggingface.co/nvidia/Qwen3.6-35B-A3B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 1
tags: [qwen3.6-35b-a3b, Alibaba, Qwen, NVFP4, 16-40B, Spark recipe, conc-1]
status: done
prefill_toks: 116.8
decode_toks: 93.91
mem_gb: 108.57
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV (util 0.85) + MTP head
spec_acceptance: mean acceptance length ~3.0 (range 2.79–3.24, median 2.99) · accepted throughput ~70 tok/s single-stream · per-position ~0.84/0.66/0.51
measured_on: 2026-06-23
completed_at: 2026-06-23 13:02 +08
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:68e23ddd982ad5642e21354c2242a3a86d31a3ea83f5937e5c3867942dc6595b
run_command: |
  # conc-1 single-stream latency point (200 prompts / 300 s cap). Same NVIDIA Spark MTP recipe.
  scripts/bench-vllm-serving.sh nvidia/Qwen3.6-35B-A3B-NVFP4 65536 1 200 300 256 \
    --quantization modelopt --trust-remote-code --reasoning-parser qwen3 --moe-backend marlin \
    --speculative-config '{"method":"mtp","num_speculative_tokens":3,"moe_backend":"triton"}'
  # 111/200 prompts (hit 300 s cap), 0 errors. ready after 420 s. TTFT median 2394 ms.
---

**conc-1 (single-stream) point of the Qwen3.6-35B-A3B NVFP4 + MTP sweep.** Best-case MTP latency — no
batch contention. Pairs with the conc-32 done run (decode 541 tok/s agg) and the conc-8 sibling.

- **Result (conc 1):** prefill 116.8 / decode **93.91** tok/s single-stream aggregate; **111/200** prompts
  (hit 300 s cap), 0 errors; peak mem **108.57 GB**; TTFT median **2394 ms**. The single-stream decode is
  the headline low-conc number — no batch contention, so this is best-case MTP latency for this checkpoint.
- **Acceptance holds:** mean accept-len **~3.0** (range 2.79–3.24, median 2.99), avg draft acceptance
  ~66%, per-position ~0.84/0.66/0.51 — identical to conc-8 (~3.0) and conc-32 (~3.0). **Acceptance is
  workload-driven, not concurrency-driven** — same conclusion across the whole 35B-A3B and 27B sweeps.
- **Single-stream accepted throughput ~70 tok/s** (SpecDecoding log) vs ~93.9 tok/s client decode — the
  spec head sustains ~70 accepted tokens/s of useful generation per stream at acc-len 3.
- **600 s-cap recheck (2026-07-01):** this page's 93.91 was a 300 s / 200-prompt run; a matched **600 s-cap
  re-measurement gave decode 99.04 tok/s** (233/400, 0 err) — ~5% higher (the short cap over-weights warmup;
  same effect lifted MTP c8 289→304). **This is the money-chart-relevant MTP c1 baseline:** against it,
  DFlash's conc-1 lead is only **~+2.9%** (101.9 vs 99.04), not the +8.5% quoted against the 93.91 short-cap
  number — see [`…ultimate-dflash`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-ultimate-dflash/) and the base
  [`-vllm-c1`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-c1/).
- **TPOT caveat:** the `qwen3` reasoning-parser zeros the client TPOT median (reads 0.0) — corroborate with
  the in-engine SpecDecoding metrics above.
