# CLAUDE.md — orientation for a future agent

**autobench**: a harness + results website for benchmarking open-weight LLMs on a single **NVIDIA
DGX Spark**. Live state = the `_configs/` pages + homepage listing; no separate journal.

- **The model list IS the `_configs/` collection** — one stub page per model × engine × quant is the
  source of truth for what to benchmark.
- **Companion docs:** `notes/BENCHMARKING.md` (how to run/measure: wrappers, dataset, run caps,
  spec-decode, image policy, digests) · `notes/INCOMPATIBILITIES.md` (engine/model walls + fixes —
  **check before debugging a failing launch**).

## Mission

- One model at a time: download → run across engine / quant / context configs → record
  **full run command · context window · tok/s (prefill + decode) · peak memory**. The notes ARE the
  deliverable — over-note.
- **Run by an Opus-class agent** — quant choice, sourcing trusted HF repos, and fixing imprecise
  model-list entries (wrong/renamed/gated repos, ambiguous sizes) need judgment; don't downgrade.

## The machine (`heruli`)

- DGX Spark, **GB10 Grace-Blackwell, ARM64**, Ubuntu 24.04, CUDA 13. 20 cores, ~3.5 TB free, internet.
- **121 GB unified memory** (CPU/GPU shared) — the hard ceiling that decides fit.
- Verify GPU: `nvidia-smi` → `GPU 0: NVIDIA GB10`.
- **sudo is password-gated** — can't run non-interactively; hand the user the exact command.
- **docker works without sudo** (user in `docker` group). Engines run as **NGC containers**
  (`--gpus all`). Pick **arm64/sbsa** tags — many wheels/images are x86-only.
- **Creds in `.env`** (gitignored): `NIM_KEY` (NGC, `nvcr.io` + NIM), `HF_TOKEN` (gated HF). Load with
  `set -a; source .env; set +a`. Never echo or commit them.
- **Measuring memory:** `nvidia-smi` reports N/A (unified) and cgroup/`docker stats` undercounts.
  Headline mem = **system `MemAvailable` delta** from idle baseline, 10 s sampling.
- **GPU driver recovery:** if `nvidia-smi` fails, check `uname -r` vs installed
  `linux-modules-nvidia-580-open-*` (kernel/module mismatch); fix with
  `sudo apt-get install -y linux-modules-nvidia-580-open-$(uname -r)` then `sudo modprobe nvidia`.

## Engines

- **llama.cpp · vLLM · TensorRT-LLM · SGLang · NIM**, all via NGC containers.
- Per model, sweep quant (GGUF Q4_K_M/Q8; FP8/AWQ/MXFP4/NVFP4/BF16) × context × concurrency.
- Verify exact HF repo IDs at download time — the model list has unverified 2026 names.
- Wrappers, per-model engine selection, spec-decode → `notes/BENCHMARKING.md`. Every known
  engine/model wall + fix → `notes/INCOMPATIBILITIES.md`.

## Website (Jekyll)

- **Ruby lives only in Docker — never install it on the host.** `./serve.sh` = live preview;
  `./build.sh` = static build into `_site` (run before pushing to catch Liquid errors).
- `_configs/` — the collection, one page per config. Front matter: `model/company/family/params/
  engine/speculative/quant/quant_rationale/source_repo/download_url/context/modalities/tags` + results
  (`prefill_toks/decode_toks/mem_gb/mem_source/run_command/completed_at/engine_image`) +
  `status: pending | blocked | done`. `engine_image` = pinned `repo:tag@sha256:<digest>` (map in
  `notes/BENCHMARKING.md`). Homepage sorts done (newest) → pending → blocked.
- `_archive/configs/` — `git mv` a page here to hide it without losing data (excluded in `_config.yml`).
- **Cross-config links must be `[text]({{ site.baseurl }}/configs/<slug>/)`** — a bare `[text](slug)`
  resolves against `/configs/<this-page>/` and 404s (permalink is `/configs/:name/`).
- **Tag taxonomy = 7 categories:** concurrency (`conc-N`) · model (per-model slug, FIRST in `tags:`,
  identical across a model's configs) · lab · family · quant · size-bucket
  (`≤4B`/`5-15B`/`16-40B`/`41-130B`/`130B+`) · `Spark recipe`. Engine is a field, NOT a tag.
- `scripts/new-config.sh` generates a page; `scripts/seed-stubs.sh` applies the taxonomy. Keep `tags*.md`
  pure-Liquid (Pages-safe).
- **Deploy:** push `main` → GitHub Actions → Pages (https://gauravmm.github.io/autobench). Remote is SSH
  via deploy key; `git push` just works. **Commit/push after every new benchmark.**

## Working style

- User moves fast; keep momentum, validate before pushing.
- **Read `date "+%Y-%m-%d %H:%M %z"` immediately before writing any `completed_at`** — never reuse an
  earlier timestamp (a run drifts it by minutes).
- Aggressive autocompact (`CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=40`) — rely on this file + `_configs/` pages
  as durable memory, not in-context history.
- No journal: results → per-config pages; decisions/methodology → here + the two `notes/` docs.
