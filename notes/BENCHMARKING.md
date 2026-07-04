# Benchmarking — methodology & policy

How to run and measure each config. Referenced from `CLAUDE.md`.
Engine/model-specific failures live in `INCOMPATIBILITIES.md`.

## Engine wrappers (all drive `bench-serving.py`)

`bench-serving.py` is engine-agnostic (any OpenAI `/v1/chat/completions` endpoint: llama-server, vLLM,
SGLang, TRT-LLM) and counts a streamed `{"error":...}` chunk as a failed request (not a 0-token
success).

- `scripts/bench-llamacpp-serving.sh` — launches llama.cpp `--server` + drives `bench-serving.py`
  against ShareGPT (current path). (`scripts/bench-llamacpp.sh` = synthetic `--bench`, superseded.)
- `scripts/bench-sglang-serving.sh` — `lmsysorg/sglang:spark`, port 30000.
- `scripts/bench-vllm-serving.sh` — vLLM, port 8000, `--gpu-memory-utilization 0.85
  --max-num-seqs=<conc>`. **Image policy (see below).**

vLLM and SGLang pre-reserve a static KV fraction, so their `mem_gb` is a *reservation*, not the model
footprint — dig the resident breakdown out of the engine logs for the Notes.

### vLLM image policy — try `nightly-aarch64` first, fall back to `cu130-nightly`

**Default to `vllm/vllm-openai:nightly-aarch64`** (the maintained successor: vLLM 0.23.1rc1+, GB10
jit-cache 0.6.12). The old pin `cu130-nightly` is **outdated** (abandoned ~2 months, no new pushes) —
use it only as a fallback. Override the wrapper's image with `VLLM_IMAGE=`.

Known fallback case: `nightly-aarch64` **regresses loading of the E4B *elastic* Gemma-4 NVFP4 checkpoint**
(`gemma4.py tie_weights → NotImplementedError`, fires on E4B's tied+quantized `lm_head`) — drop back to
`cu130-nightly` for *that* checkpoint. This is **not** a blanket Gemma-4 NVFP4 regression: non-elastic
Gemma-4 NVFP4 (12B dense confirmed; 26B-A4B/31B) loads fine on `nightly-aarch64` (see
`notes/INCOMPATIBILITIES.md` → Gemma-4 MTP). If a model fails to load on `nightly-aarch64`, try
`cu130-nightly` before declaring it blocked, and note which image worked on the config page (record the
actual one in `engine_image`).

## Model downloads — let the container pull, don't host-`hf download`

The HF cache `~/.cache/huggingface/hub` is **root-owned** (every model was pulled *inside* a serving
container running as root with the cache bind-mounted). So a **host-side `hf download` fails with
`PermissionError: [Errno 13]`** on the root-owned `hub/` — and `huggingface-cli` is now a deprecated no-op
besides. **Don't pre-download on the host.** Just launch the benchmark: the wrappers pass `HF_TOKEN` and
mount `~/.cache/huggingface`, so **vLLM/SGLang self-download the model (and any `--speculative-config`
drafter) on first boot**, as root, into the cache — the health-wait loop covers the pull. Gated repos work
too (the token is in the container env). First run of a new model is slower (download + load); reruns hit
the cache. MemAvailable isn't corrupted by the pull — it counts reclaimable page cache as available, and the
download completes before the mem sampler starts (sampler runs only after `/health` is ready).

## Workload dataset

Benchmark against the real dataset in **`./benchmark_data/`** —
`ShareGPT_V3_unfiltered_cleaned_split.json` (ShareGPT V3, 94k conversations, ~642 MB, **gitignored —
never commit it**), not synthetic fixed-length tokens. Feed it to each engine's serving benchmark: vLLM
`benchmark_serving.py --dataset-path …`, SGLang `bench_serving --dataset-name sharegpt --dataset-path
…`, TRT-LLM `trtllm-bench --dataset …`. llama.cpp's `llama-bench` takes no dataset, so for llama.cpp run
`llama-server` + a serving benchmark against it (or derive representative input/output lengths from
ShareGPT). Always record concurrency.

## Per-run runtime cap

Target **~1000 entries or 15 minutes of wall-clock, whichever is shorter**, for each config's serving
benchmark. Cap the ShareGPT prompt count (`--num-prompts` / equivalent) at ~1000 and stop a run that
crosses 15 min. Note in the config if a run hit the time cap before the entry cap (signals a slow path
worth flagging).

## Unified-memory ceiling & the mem-watchdog (GB10) — READ before high-concurrency sweeps

**CPU and GPU share ONE 121 GB pool, and a vLLM run can HARD-CRASH/reboot the whole box.** vLLM
reserves ~`gpu-memory-utilization`·121 GB of KV up front; then **CUDA-graph capture + activation
buffers pile on TOP of that reservation as `--max-num-seqs` grows**. Past ~conc-64 at ctx 65536 the
free headroom collapses to a few GB and a GPU unified alloc that can't be satisfied takes the kernel
down — **no graceful OOM-kill, the machine reboots.**

- **`mem_gb` is a DELTA from the ~118 GB idle baseline, so read it as "used", and 121 − 118 ≈ 3 GB is
  all the slack.** Observed 2026-07-04 (gemma-4 26B-A4B NVFP4+MTP, util 0.85, ctx 65536):
  c64 `mem_gb` 110.6 → **~8 GB free**; c128 114.4 → **~4 GB free** (already marginal); c256 118.3 →
  **~0.2 GB free** (survived only because the run collapsed to ~9 active seqs). Launching qwen-mtp
  (35B, heavier) at c64 right after the c256 collapse **rebooted the box.**
- **Always run high-concurrency (≥ c64) sweeps under `scripts/mem-watchdog.sh`.** It polls
  `MemAvailable` every 0.25 s and `docker kill`s the `vllm-*` container the instant free memory drops
  below a floor (default **6 GB**), converting a machine crash into a killed container + a recorded
  "memory ceiling". Arm it in the **background before** launching the container (graph capture spikes
  memory during load/warmup, not just serving):
  `scripts/mem-watchdog.sh 6 vllm- 0.25 & ` → run the wrapper → `kill %1`. It writes
  `$WATCHDOG_TRIPFILE` (default `/tmp/mem-watchdog.trip`) on a trip; a tripped run = the memory ceiling.
- **A watchdog trip IS a valid result** — record the config page as the ceiling point (note it tripped,
  at what free-mem, and that it is memory-bound). Don't retry the identical config expecting success.
- **Between runs, let `MemAvailable` recover to ~118 GB before launching the next** (the c256→qwen
  cascade crash came from launching while the box was still near-zero). `docker ps` empty ≠ memory
  reclaimed; check `/proc/meminfo`.
- **To push a line PAST its 0.85-util memory ceiling** (get a real compute-scaling point instead of an
  OOM), drop `--gpu-memory-utilization` (e.g. 0.78) to shrink the reservation and free headroom for
  graphs — but **label it a separate util-adjusted regime** (it no longer splices onto the 0.85 curve).

## Policy

- **Run order:** generally do the **headliners first** (the `Spark recipe` / best-documented
  showcases — gpt-oss, the Nemotron NVFP4 models), then work through the rest **small → big**, so
  cheap fast runs validate each engine/path before the heavy giants.
- **Record anything interesting in the per-config Notes** (the markdown body of the `_configs/*.md`
  page, rendered as the "Notes" section). When a run surprises you — a context length that fits or
  OOMs, the memory cliff where it stops fitting, an unusually good/bad quant, throughput that defies
  the bandwidth estimate, a format/dispatcher gotcha, multimodal quirks — write it there. The user
  reviews these manually, so prefer over-noting to losing the observation.
- **Extra quants welcome.** Beyond the one stub config per model, add more quants whenever useful —
  but only from a **trusted HF repo** (the model's own org, or a well-known quantizer like
  ggml-org / unsloth / the lab's official quant). For every config record **`quant_rationale`**
  (why this quant) and **`download_url`** + `source_repo` (its HF page).
- **When unsure, BLOCK — don't guess.** If you're not confident a quant is safe/legit to run
  (sketchy/unofficial repo, unclear license, can't confirm the format fits), set
  **`status: blocked`** instead of running it; the user reviews blocked items later.
- **Status values:** `pending` → `blocked` (needs human review) / `done`. Listing sorts
  done (newest first) → pending → blocked (last).
- **Compound dimensions — that's the point.** Wherever a model supports it, benchmark the
  cross-product as separate configs: engine × quant × speculative-decoding (e.g. gpt-oss-20b →
  vLLM, SGLang, SGLang+EAGLE3, TRT-LLM). More comparable data points is the goal, not one config
  per model.
- **Engine selection per model.** When loading a new model to benchmark, first check current
  sources (NVIDIA Dev Forums, `build.nvidia.com/spark`, the engine repos/discussions) for which
  serving stack is claimed **highest-performance for THAT model on GB10/Spark**. If one is the
  obvious winner, use it; if it's close, **benchmark the top two**. Briefly note the decision + why
  (with a source) on the config page. The stub's engine/quant is only a starting guess — override it
  per this check.
- **TensorRT-LLM build time.** TRT-LLM compiles a per-model engine before it can serve — **record
  that compilation / engine-build time on the model page.** It's a real cost of the path (often the
  reason to prefer SGLang/vLLM) and belongs in the comparison.
- **NIM is available.** An NGC key is in `.env` as `NIM_KEY`. NIM configs may be **run** (not
  auto-blocked) — pull `nvcr.io/nim/...` images and pass the key as `NGC_API_KEY`. Only block a
  specific NIM config if that model isn't in the NIM catalog / can't be served.
- **Benchmark measures throughput, not accuracy** (tok/s + concurrency), per the speed-only scope.

## Speculative decoding

Where a model ships an **MTP** module (e.g. DeepSeek) or an **EAGLE/EAGLE3/Medusa** draft is available
for the engine, benchmark a **separate config with speculation enabled IN ADDITION to the base
(non-spec) config** — never replace it. Record the method in a `speculative:` field (e.g. `EAGLE3`,
`MTP`) and the decode-tok/s speedup vs the base run in Notes. SGLang (EAGLE3) and vLLM/TRT-LLM (MTP) are
the usual paths. The `speculative:` value is **folded into the Engine display** (e.g. `SGLang + EAGLE3`)
on the page and listing — it is NOT a separate table column.

- **ALWAYS capture the draft acceptance rate for spec runs.** The serving wrappers print a
  `==> SPEC-METRICS (acceptance):` block (grepped from the engine container's log **before** teardown)
  whenever a speculative flag is present — vLLM logs mean acceptance length / per-position acceptance,
  llama.cpp logs `n_draft`/`n_accept`, SGLang logs accept length. **Record the acceptance rate (and
  mean accepted tokens/step) on the config page** alongside the speedup — it's what explains *why* a
  spec run helped or hurt. If the grep catches nothing, note the metric wasn't emitted rather than
  omitting it silently.
- **Cross-check the acceptance rate against the published/expected value, and flag any gap.** Before
  accepting a spec result, look up what the model's drafter is *supposed* to achieve (the lab/unsloth
  blog, vLLM recipe, the EAGLE3/MTP paper) and compare. Rules of thumb: well-matched **MTP/EAGLE3
  drafts land ~70–85% draft acceptance** (often >80% on *coding* workloads; **ShareGPT general chat
  runs lower**, e.g. Qwen3.6-27B MTP measured **67%** here vs ~80%+ reported on code), **mean
  acceptance length ≈ 3.0** for `num_speculative_tokens=3`; off-the-shelf separate draft models
  usually <50%. **Acceptance is workload-driven, NOT strongly concurrency-driven** — it should stay
  roughly constant across conc 1/8/32; what changes with concurrency is whether the *speedup*
  materializes (bigger at low batch). So if a measured acceptance is **far from expectation**
  (e.g. an MTP head at 30%, or acceptance that swings wildly with concurrency), that's a **red flag**
  — likely a misconfigured method name, a base/draft mismatch, or a quant/format problem — and should
  be investigated and noted on the config page, not silently recorded.
- For the measured gpt-oss EAGLE3 result (poor & concurrency-degrading on ShareGPT), see
  `INCOMPATIBILITIES.md`.

## `engine_image` digest map

`engine_image` records the **fully pinned base image** the run used: `repo:tag@sha256:<digest>`. Engine
tags (cu130-nightly, llama.cpp:full-cuda, …) are rolling, so the `@sha256` digest is the only durable
record of what actually ran. Populate it for every `done` run (capture with
`docker inspect --format '{{index .RepoDigests 0}}' <tag>` right after the run). Derive the short tag in
Liquid with `{{ c.engine_image | split: '@' | first }}`.

Digest map as of 2026-06-23:
- `vllm/vllm-openai:nightly-aarch64@sha256:68e23ddd982ad5642e21354c2242a3a86d31a3ea83f5937e5c3867942dc6595b`
  — **the current default** (vLLM 0.23.1rc1, GB10 jit-cache 0.6.12). `nightly-aarch64` is a rolling
  tag, so this digest will drift — recapture it per run.
- `vllm/vllm-openai:cu130-nightly@sha256:3dbe092ec5b2cef63b6104d33fa75d6ce53a7870962529ada69f78bbbc38e776`
  — **outdated fallback** (abandoned ~2 months, no push, so its digest is stable). Use only where
  `nightly-aarch64` regresses (e.g. Gemma-4 NVFP4 loading).
- `ghcr.io/ggml-org/llama.cpp:full-cuda@sha256:12b288d6271e8de14412d61f641ca3ecd83bd73e1c4f4f22d86b2536f2b2f8e2`
- `lmsysorg/sglang:spark@sha256:16dec654b13e4d10a2d9eefa0560e85fed0d1fc9536986e1dfb1bcb0077cbc7a`
- `lmsysorg/sglang:nightly-dev-cu13-20260623-ba9d5aed@sha256:ca580c17cf5f9d2e268f4153d977e3cd46528feb2c62a4de8683a05d08da3cf2`
  — newer nightly (transformers 5.8.1); needed for Qwen3.6 arch **and** for gpt-oss-120b EAGLE3 at
  conc-32 (the `spark` image drops ~70% of streams with eagle3 — see `INCOMPATIBILITIES.md`).
