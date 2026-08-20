---
title: Qwen3.6-35B-A3B · vLLM · NVFP4 + MTP · conc 8
model: Qwen/Qwen3.6-35B-A3B
company: Alibaba
family: Qwen
params: 35B / 3B (MoE)
engine: vLLM
speculative: MTP
quant: NVFP4
quant_rationale: Concurrency-8 point of the Qwen3.6-35B-A3B NVFP4 + native-MTP sweep — same stack as the conc-32 run (nvidia ModelOpt NVFP4 base on marlin + in-repo MTP head on triton), lower batch for the latency-characterization point. Acceptance should hold ~constant vs conc-32 (workload-driven); what changes is the per-stream TPOT.
source_repo: nvidia/Qwen3.6-35B-A3B-NVFP4
download_url: https://huggingface.co/nvidia/Qwen3.6-35B-A3B-NVFP4
context: 65536
modalities: [text, image, video]
mm_served: false
concurrency: 8
tags: [qwen3.6-35b-a3b, Alibaba, Qwen, NVFP4, 16-40B, Spark recipe, conc-8]
status: done
prefill_toks: 327.44
decode_toks: 289.14
mem_gb: 108.09
mem_source: system MemAvailable delta (10s sampling) — vLLM static KV (util 0.85) + MTP head
spec_acceptance: mean acceptance length ~3.0 (range 2.9–3.2) · avg draft acceptance ~67% · per-position 0.84/0.66/0.51
measured_on: 2026-06-23
completed_at: 2026-06-23 12:49 +08
engine_image: vllm/vllm-openai:nightly-aarch64@sha256:68e23ddd982ad5642e21354c2242a3a86d31a3ea83f5937e5c3867942dc6595b
run_command: |
  # conc-8 latency point (500 prompts / 300 s cap, matching the -c8 convention). Same NVIDIA Spark
  # MTP recipe as the conc-32 run.
  scripts/bench-vllm-serving.sh nvidia/Qwen3.6-35B-A3B-NVFP4 65536 8 500 300 256 \
    --quantization modelopt --trust-remote-code --reasoning-parser qwen3 --moe-backend marlin \
    --speculative-config '{"method":"mtp","num_speculative_tokens":3,"moe_backend":"triton"}'
  # 345/500 prompts (hit 300 s cap), 0 errors. ready after 437 s. TTFT median 6245 ms.
---

**conc-8 point of the Qwen3.6-35B-A3B NVFP4 + MTP sweep.** Lower-batch latency characterization
(cap 500 prompts / 300 s — reached 345, 0 errors). Pairs with the conc-32 done run (decode 541 tok/s
agg) and the conc-1 sibling.

- **Result (conc 8):** prefill 327.4 / decode **289.14** tok/s aggregate; peak mem 108.1 GB. Lower
  aggregate than conc-32 (541) purely because 8 streams push fewer total tokens — the meaningful low-conc
  signal is per-stream latency, but the `qwen3` reasoning-parser zeros the client TPOT median here (read
  the SpecDecoding throughput instead: ~225 tok/s accepted across the run).
- **Acceptance holds:** mean accept-len **~3.0** (2.9–3.2), avg draft acceptance **~67%**, per-position
  0.84 / 0.66 / 0.51 — essentially identical to the conc-32 run (~3.0 / 66–69%). **Acceptance is
  workload-driven, not concurrency-driven** — same conclusion as the 27B sweep.
- **600 s-cap recheck (2026-07-01):** this page's 289.14 was a 300 s / 500-prompt run; a matched **600 s-cap
  re-measurement gave decode 304.0 tok/s** (718/1000, 0 err) — the extra samples lift it slightly. Used the
  600 s value (**+25.7% over the matched base c8**) when drawing the base-vs-MTP curve, which removes the
  apparent c8 "dip"; see [`-vllm-c16`]({{ site.baseurl }}/configs/qwen3-6-35b-a3b-nvfp4-vllm-c16/) Notes.
