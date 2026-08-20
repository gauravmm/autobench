---
marp: true
theme: default
paginate: true
footer: "On Speculative Decoders — gauravmm.github.io/autobench/posts/2026-07-01-speculative-decoders-are-all-you-need/"
---

<style>
/* softaworks marp-slide structure, styled after Roast My Tech Stack's Metropolyst deck. */
:root {
  --paper: #fcfcfa;
  --ink: #333333;
  --blue: #1c58a1;
  --blue-soft: #ddeeff;
  --blue-muted: #acc1da;
  --line: #d8dde5;
  --red: #b33a3a;
}

section {
  background: var(--paper);
  color: var(--ink);
  font-family: Roboto, -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
  box-sizing: border-box;
  border-top: 12px solid var(--blue);
  font-size: 21px;
  line-height: 1.38;
  padding: 58px 64px 54px;
}

h1, h2, h3, h4, h5, h6 {
  color: var(--blue);
  font-weight: 700;
  margin: 0;
}

h1 { font-size: 54px; line-height: 1.12; }

h2 {
  font-size: 36px;
  line-height: 1.15;
  margin-bottom: 30px;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--blue-muted);
}

h3 {
  color: var(--ink);
  font-size: 25px;
  margin: 22px 0 8px;
}

ul, ol { padding-left: 30px; }
li { margin-bottom: 8px; }
li::marker { color: var(--blue); }

code {
  background: #eef2f7;
  color: var(--blue);
  padding: 2px 5px;
  border-radius: 4px;
  font-family: 'Roboto Mono', Consolas, monospace;
  font-size: 0.9em;
}

a { color: var(--blue); }
strong { color: var(--blue); font-weight: 700; }

footer {
  color: #667085;
  font-size: 12px;
  position: absolute;
  left: 64px;
  bottom: 21px;
}

section::after {
  color: var(--blue);
  font-size: 13px;
  right: 64px;
  bottom: 20px;
}

table {
  border-collapse: collapse;
  width: 100%;
  font-size: 18px;
}
th {
  background: var(--blue);
  color: white;
  font-weight: 700;
}
th, td {
  border: 1px solid var(--line);
  padding: 7px 10px;
}
tr:nth-child(even) td { background: #f3f6fa; }

.callout {
  background: var(--blue-soft);
  border-left: 6px solid var(--blue);
  border-radius: 8px;
  padding: 15px 20px;
  margin-top: 22px;
}

.big {
  color: var(--blue);
  font-size: 44px;
  font-weight: 700;
  line-height: 1.1;
}

section.lead {
  background: var(--blue);
  border-top: 12px solid var(--blue-muted);
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding-right: 180px;
}
section.lead h1 { color: white; margin-bottom: 24px; }
section.lead p { color: #e8f0fa; font-size: 25px; }
section.lead strong { color: white; }
section.lead footer, section.lead::after { color: #dce8f7; }

section.focus {
  background: #dbdce5;
  border-top-color: var(--blue);
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-align: center;
}
section.focus h2 { border: 0; font-size: 48px; }

/* Deck tweaks */
img { max-width: 100%; }
</style>

<!-- _class: lead -->

# On Speculative Decoders

199 completed configs · one NVIDIA DGX Spark · measured, not marketed

<span style="font-size:16px; color:#dce8f7;">
Results: gauravmm.github.io/autobench · Spark provided by Ray Aun Fan
</span>

---

## Start here

- Use the model's **MTP path** when it has one
- Otherwise, test a **model-matched EAGLE3** draft
- Heavy external drafters are strongest at **low concurrency**
- Pick the fast **quant and engine first**

<div class="callout">Every number below is measured on one DGX Spark and linked to its run.</div>

---

## One machine changes the game

- Datacenter wins — giant batches, disaggregation, huge KV pools — do not transfer cleanly to one machine
- Speculative decoding trades a little local compute for fewer expensive target passes
- A **speculative decoder** (draft model, drafter, speculator) is a small, cheap model that *guesses the next few tokens*
- The big ("target") model verifies; accepted guesses are nearly free

---

## How it works

Draft → verify → accept prefix, stop at first disagreement:

<table>
<tr>
<td style="background:#eef2f7;"><code style="background:none;">I saw her duck</code></td>
<td style="background:#e5f4ea;"><span style="color:#287a44;">under the</span></td>
<td style="background:#f8e7e7;"><span style="color:#b33a3a;"><b>table</b></span></td>
<td style="background:#eef2f7;"><span style="color:#667085;">.</span></td>
</tr>
<tr>
<td style="background:#eef2f7;"><code style="background:none;">I saw her duck</code></td>
<td colspan="3" style="background:#ddeeff;"><span style="color:#1c58a1;">target: under the</span><b style="color:#1c58a1;"> branch</b></td>
</tr>
</table>

- Row 1 — <span style="color:#287a44;">**under the**</span> accepted; <span style="color:#b33a3a;">**table**</span> rejected; tail discarded
- Row 2 — in the same pass, the target generates <span style="color:#1c58a1;">**branch**</span>
- High-entropy forks are exactly where drafts die

---

## The economics

- Accepted tokens ≈ free; the drafter's run is a **fixed base cost**
- Payoff depends on acceptance, draft cost, scheduling, and spare compute
- One drafter pass proposes a whole continuation — 3 tokens for MTP, up to 16 for DFlash
- Everything in this talk is a case of this single tradeoff

---

## Four flavours

- **MTP** — prediction heads shipped in the model, or a matched assistant exposed through the engine's MTP path; usually lightest
- **EAGLE3** — a *separate* draft head grafted into the model; quality depends entirely on **which draft you load**
- **DFlash** — external diffusion-based drafter, up to 16 tokens per step; high fixed cost, chance of huge speedups
- **DDTree** *(emerging)* — DFlash's block draft rebuilt as a **tree** of continuations, verified in one pass
- Fast-moving field — new speculators are appearing continuously

---

## Five rules of speculation

1. **Drafters trade compute for speed** — heavy drafters spend spare compute; a saturated GPU has none
2. **Agreement is critical** — but accepted tokens still have to repay draft and verification cost
3. **Drafters are brittle** — engine, quant, workload, draft weights: change one and the win evaporates
4. **Slower target, bigger relative win** — speedup runs inversely to base speed
5. **Speculation can't rescue a bad config** — a multiplier, not a fix

---

## Rule 1 — compute buys speed

![w:84%](../assets/plots/mtp_vs_dflash_35b.svg)

- Qwen3.6-35B-A3B NVFP4: DFlash narrowly wins conc-1; **MTP leads from conc-2** and reaches [~750 tok/s at conc-128](https://gauravmm.github.io/autobench/configs/qwen3-6-35b-a3b-nvfp4-vllm-mtp-c128/)
- Heavy DFlash drafter beats the no-spec baseline **only at low batch**
- From conc-32 on, DFlash sits *below* the no-drafter baseline (407 vs 431 tok/s)
- The crossover curve belongs to the *drafter's cost*, not to speculation itself

---


## Rule 2 — agreement pays

Accept-length per verify pass (drafted tokens accepted + 1 free bonus token):

| Drafter | Accept-len |
|---|---|
| MTP | ~3.0 of 4 ([27B](https://gauravmm.github.io/autobench/tags/model/#qwen3-6-27b), [35B-A3B](https://gauravmm.github.io/autobench/tags/model/#qwen3-6-35b-a3b)) (~66%) |
| Qwen3.8 MTP | [~2.6–2.8 of 4 (~52–57%)](https://gauravmm.github.io/autobench/configs/qwen3-8-27b-nvfp4-vllm-mtp-c32/) |
| EAGLE3 | ~2.0–2.4 of 4 ([Gemma-4](https://gauravmm.github.io/autobench/tags/model/#gemma-4-31b); [gpt-oss](https://gauravmm.github.io/autobench/tags/model/#gpt-oss-120b) only with a workload-matched draft) |
| DFlash | [~3.2–4.4 of 11](https://gauravmm.github.io/autobench/tags/model/#qwen3-6-35b-a3b) (Qwen3.6-35B-A3B) |
| DDTree, code | **9.74 at b64; 10.50 at slower b256** ([Qwen3-Coder-30B-A3B](https://gauravmm.github.io/autobench/tags/model/#qwen3-coder-30b-a3b)) |
| DDTree, chat | 3.2 of 16 |

- In one target forward pass, the model checks all drafted tokens in parallel
- At the first disagreement the rest is discarded and normal decoding resumes
- More acceptance helps only when the extra draft and verification work is cheap enough

---

## Rule 3 — brittleness

Effectiveness depends on four things:

1. the **drafter model** (which draft weights)
2. the exact **training and quantization** of the target
3. the **workload**
4. the **serving software**

Change any one and the win can evaporate — or the launch can fail outright

- The drafter is judged by the target's token choices and fed by the target's own KV cache
- Two showcase cases ahead: an engine swap (43-point swing) and a draft swap (also 43 points)
- Before picking a drafter: test it in the *exact* configuration you'll run

---

## Rule 4 — slower target, bigger win

Four Qwen3.6 MTP runs (conc-32, vLLM), slowest base first:

| model · quant | base → MTP | Δ |
|---|---|--:|
| 27B · FP8 | [154.7](https://gauravmm.github.io/autobench/configs/qwen3-6-27b-vllm-fp8/) → [240.9](https://gauravmm.github.io/autobench/configs/qwen3-6-27b-vllm-fp8-mtp/) | **+56%** |
| 27B · NVFP4 | [187.7](https://gauravmm.github.io/autobench/configs/qwen3-6-27b-nvfp4-vllm/) → [274.1](https://gauravmm.github.io/autobench/configs/qwen3-6-27b-nvfp4-vllm-mtp/) | **+46%** |
| 35B-A3B · FP8 | [286.0](https://gauravmm.github.io/autobench/configs/qwen3-6-35b-a3b-vllm-fp8/) → [407.9](https://gauravmm.github.io/autobench/configs/qwen3-6-35b-a3b-vllm-fp8-mtp/) | **+43%** |
| 35B-A3B · NVFP4 | [430.8](https://gauravmm.github.io/autobench/configs/qwen3-6-35b-a3b-nvfp4-vllm/) → [541.3](https://gauravmm.github.io/autobench/configs/qwen3-6-35b-a3b-nvfp4-vllm-mtp/) | **+26%** |

- Two knobs move the target's cost: **quant** (slower FP8 gains more than fast NVFP4) and **architecture** (dense gains more than MoE)
- Flip side (Rule 5): NVFP4 *without* a speculator (430.8) still beats FP8 *with* MTP (407.9)
- **Pick the fast quant first, then add the drafter**

---

## Rule 5 — no rescue

A speculative decoder is a **multiplier, not a fix**. Three plain bases beat a fancier stack:

| Plain (no spec) | Fancy (best draft) |
|---|---|
| Qwen3.6-35B-A3B NVFP4 → [**430.8** tok/s](https://gauravmm.github.io/autobench/configs/qwen3-6-35b-a3b-nvfp4-vllm/) | FP8 + MTP → [407.9 tok/s](https://gauravmm.github.io/autobench/configs/qwen3-6-35b-a3b-vllm-fp8-mtp/) |
| Qwen3.8-27B NVFP4 → [**210.0** tok/s](https://gauravmm.github.io/autobench/configs/qwen3-8-27b-nvfp4-vllm-c32/) | FP8 + MTP → [203.0 tok/s](https://gauravmm.github.io/autobench/configs/qwen3-8-27b-fp8-vllm-mtp-c32/) |
| gpt-oss-120b MXFP4 on vLLM → [**252.8** tok/s](https://gauravmm.github.io/autobench/configs/gpt-oss-120b-vllm-mxfp4/) | SGLang + EAGLE3 → [171.9 tok/s](https://gauravmm.github.io/autobench/configs/gpt-oss-120b-sglang-mxfp4-eagle3-c32/) |

- Get the quant and engine right *first*
- Speculation compounds a good setup; it can't paper over a bad one

---

## MTP across three families

![w:92%](../assets/plots/base_vs_mtp.svg)

- Qwen3.6 + Qwen3.8 + Gemma-4, base vs +MTP at conc-32 on vLLM
- MTP adds **+26% to +94%** — peaking at Gemma-4-E4B FP8 ([1262 tok/s](https://gauravmm.github.io/autobench/configs/gemma-4-e4b-it-vllm-fp8-mtp/))
- Which method you even *get* is largely decided by the family: MTP only where the lab baked in a head

---

## Qwen3.6 — native MTP

The 35B-A3B MoE on NVFP4 + MTP hits [**541.3 tok/s**](https://gauravmm.github.io/autobench/configs/qwen3-6-35b-a3b-nvfp4-vllm-mtp/). The result matters because it lands on the right side of every rule:

- **R1** — after DFlash's narrow conc-1 win, MTP leads from conc-2 to conc-128
- **R2** — high acceptance: ~3.0 of 4 (~66%)
- **R3** — robust by construction: the MTP head ships with the model, draft and target are matched
- **R4** — light MoE pass on fast NVFP4 leaves little to amortize → "only" **+26%** (the small end of the curve)
- **R5** — that +26% compounds the fastest base we measured for this model

Engine details still bite: 27B NVFP4 + MTP gains [+46% on vLLM](https://gauravmm.github.io/autobench/configs/qwen3-6-27b-nvfp4-vllm-mtp/) but only [+10.5% on SGLang](https://gauravmm.github.io/autobench/configs/qwen3-6-27b-nvfp4-sglang-mtp/).

---

## Qwen3.8 — weaker draft, clear win

| concurrency | base → MTP | Δ | accept-len |
|---:|---|--:|--:|
| 1 | [11.16](https://gauravmm.github.io/autobench/configs/qwen3-8-27b-nvfp4-vllm-c1/) → [21.35](https://gauravmm.github.io/autobench/configs/qwen3-8-27b-nvfp4-vllm-mtp-c1/) | [**+91%**](https://gauravmm.github.io/autobench/configs/qwen3-8-27b-nvfp4-vllm-mtp-c1/) | ~2.8 / 4 |
| 8 | [75.04](https://gauravmm.github.io/autobench/configs/qwen3-8-27b-nvfp4-vllm-c8/) → [126.68](https://gauravmm.github.io/autobench/configs/qwen3-8-27b-nvfp4-vllm-mtp-c8/) | [**+69%**](https://gauravmm.github.io/autobench/configs/qwen3-8-27b-nvfp4-vllm-mtp-c8/) | ~2.6 / 4 |
| 32 | [209.97](https://gauravmm.github.io/autobench/configs/qwen3-8-27b-nvfp4-vllm-c32/) → [274.74](https://gauravmm.github.io/autobench/configs/qwen3-8-27b-nvfp4-vllm-mtp-c32/) | [**+31%**](https://gauravmm.github.io/autobench/configs/qwen3-8-27b-nvfp4-vllm-mtp-c32/) | ~2.6 / 4 |

<div class="callout"><strong><a href="https://gauravmm.github.io/autobench/configs/qwen3-8-27b-nvfp4-vllm-mtp-c32/">Acceptance stays ~52–57%.</a></strong> The gain shrinks because spare compute disappears—not because the workload changes.</div>

- Cost: higher TTFT at every point; [~22% less KV capacity](https://gauravmm.github.io/autobench/configs/qwen3-8-27b-nvfp4-vllm-mtp-c32/) at conc-32
- Rule 5 again: plain NVFP4 (210.0) still edges FP8 + MTP (203.0)

---

## Gemma-4 — MTP vs EAGLE3

![w:88%](../assets/plots/gemma_26b_crossover.svg)

- Gemma-4 is the only family with both Google's matched MTP assistant and grafted EAGLE3 — the cleanest head-to-head
- MTP leads EAGLE3 at every point and peaks at [**1380 tok/s**](https://gauravmm.github.io/autobench/configs/gemma-4-26b-a4b-it-vllm-nvfp4-mtp-c128/) (conc-128); both paths become non-viable at conc-256
- The drafter-free base is leaner and scales on to [1366 tok/s](https://gauravmm.github.io/autobench/configs/gemma-4-26b-a4b-it-vllm-nvfp4-c256/) at conc-256
- Native MTP wins the head-to-head: **+17%** on 26B-A4B, **+22%** on 31B

| model · quant | base | → MTP | Δ | → EAGLE3 | Δ |
|---|--:|--:|--:|--:|--:|
| 26B-A4B · NVFP4 | 421.1 | [**697.0**](https://gauravmm.github.io/autobench/configs/gemma-4-26b-a4b-it-vllm-nvfp4-mtp/) | +66% | [596.3](https://gauravmm.github.io/autobench/configs/gemma-4-26b-a4b-it-vllm-nvfp4-eagle3/) | +42% |
| 31B · NVFP4 | 167.0 | [**323.5**](https://gauravmm.github.io/autobench/configs/gemma-4-31b-it-vllm-nvfp4-mtp/) | +94% | [264.7](https://gauravmm.github.io/autobench/configs/gemma-4-31b-it-vllm-nvfp4-eagle3/) | +59% |

*(E4B FP8 and 12B NVFP4 have no usable EAGLE3 head; MTP alone still posts +45% / +55%.)*

---

## The whole serving stack matters

Three comparable Gemma-4-12B paths—not a controlled engine-only experiment:

| engine · quant | base → MTP | Δ | why |
|---|--:|--:|---|
| vLLM · NVFP4 | 503.8 → [**782.4**](https://gauravmm.github.io/autobench/configs/gemma-4-12b-it-redhatai-vllm-nvfp4-mtp/) | **+55%** | overlap scheduler on ✅ |
| SGLang · NVFP4 | 386.6 → [399.8](https://gauravmm.github.io/autobench/configs/gemma-4-12b-it-axionml-sglang-nvfp4-mtp/) | +3.4% | overlap scheduler off ❌ |
| llama.cpp · Q4 | 195.3 → [202.2](https://gauravmm.github.io/autobench/configs/gemma-4-12b-it-llamacpp-mtp/) | +3.5% | overlap scheduler off ❌ |

- Checkpoints differ between the NVFP4 rows; llama.cpp uses Q4_K_M
- Scheduler overlap is the leading explanation for vLLM's larger gain, not isolated proof
- Actionable: benchmark the exact engine + checkpoint + quant combination

---

## gpt-oss — the draft is everything

No native MTP head, so EAGLE3 is the only option — and where the draft-weights rule is sharpest:

| engine · draft | base → EAGLE3 | Δ |
|---|---|---|
| SGLang · LMSYS draft | [140.3](https://gauravmm.github.io/autobench/configs/gpt-oss-120b-sglang-mxfp4/) → [171.9](https://gauravmm.github.io/autobench/configs/gpt-oss-120b-sglang-mxfp4-eagle3-c32/) | **+22%** |
| vLLM · LMSYS draft | [252.8](https://gauravmm.github.io/autobench/configs/gpt-oss-120b-vllm-mxfp4/) → [246.7](https://gauravmm.github.io/autobench/configs/gpt-oss-120b-vllm-mxfp4-eagle3-lmsys-c32/) | −2.4% |
| vLLM · NVIDIA draft | [252.8](https://gauravmm.github.io/autobench/configs/gpt-oss-120b-vllm-mxfp4/) → [138.5](https://gauravmm.github.io/autobench/configs/gpt-oss-120b-vllm-mxfp4-eagle3/) | **−45%** |

- **R3**: on the same model and engine, swapping draft weights moves **43 points** (NVIDIA draft ~9% accept → LMSYS/SpecForge ~29%)
- **R5**: SGLang + EAGLE3 (171.9) is ~32% below vLLM with *no speculation* (252.8)
- Within vLLM, the LMSYS draft reaches 246.7: nearly neutral, still below base
- The fastest gpt-oss-120b we measured: **vLLM, no spec**

---

## Qwen3-Coder — DFlash & DDTree

DFlash on chat is dead weight: 2.25 of 16 accepted → **0.92×**. The *same* drafter on templated code (HumanEval): **[7.96 of 16](https://gauravmm.github.io/autobench/configs/qwen3-coder-30b-a3b-ddtree-humaneval/) → 2.7×**.

- **R2/R3** — the workload alone decides whether a high-cost drafter is waste or the fastest thing on the box
- Why: DFlash bets everything on *one* long continuation; its probability decays to nothing

**DDTree** (arXiv 2604.12989): rebuild the block draft as a tree of ~64 candidate paths, verify together — a hedge against that brittleness:

| batch-1 (research harness) | none | DFlash | DDTree b64 | DDTree b256 |
|---|--:|--:|--:|--:|
| chat: speedup | — | 0.92× | [**1.12×**](https://gauravmm.github.io/autobench/configs/qwen3-coder-30b-a3b-ddtree/) | 0.94× |
| code: speedup | — | 2.7× | [**2.8×**](https://gauravmm.github.io/autobench/configs/qwen3-coder-30b-a3b-ddtree-humaneval/) | 2.3× |

- DDTree *rescues* chat (0.92× → 1.12×); on code it does about the same as DFlash
- Paper claims 8.22× on HumanEval; we measure ~2.8× — speedup tracks spare compute
- Not in vLLM or SGLang yet — research-harness numbers at batch-1

---

## The future

- **Diffusion targets**
  - [DiffusionGemma](https://gauravmm.github.io/autobench/tags/model/#diffusiongemma-26b-a4b): 256-token blocks by diffusion, no drafter, no verify pass — [**116 tok/s at batch-1**](https://gauravmm.github.io/autobench/configs/diffusiongemma-26b-a4b-vllm-nvfp4-c1/), but throughput flat at ~200 and quality well below autoregressive Gemma-4
  - Nemotron-Labs-TwoTower: frozen AR model + trained denoiser — **×2.42** while keeping 98.7% of benchmark quality; the same architecture can both verify and speculate
- **Drafter-assisted prefill**
  - Small model skims the prompt and flags the tokens that matter → faster first token, up to **~7.7× TTFT** (SpecPrefill)
  - Natural next experiment for long-context, low-concurrency — exactly the Spark's niche
- **DDTree** isn't in vLLM or SGLang yet — watch closely

---

## So… what should I do?

The five rules, as a one-minute checklist:

1. Heavy drafters burn **spare compute** — biggest win at low concurrency
2. Check **acceptance rate** first — rejected tokens are wasted work
3. **Brittle**: engine, quant, workload, draft weights — nothing transfers without measuring
4. Slowest configs gain the most **relative** speedup
5. Pick the fast **quant and engine first** — a multiplier can't rescue a bad base

- None of this substitutes for benchmarking *your* model on *your* workload
- These numbers: one machine, a handful of engines, two datasets — Rule 3 is a standing warning
- Measure decode rate at **the concurrency you actually run**, on prompts that look like your traffic

---

## Keep watching

- Fast-moving on both sides: new speculators (trees, diffusion drafters, drafter-assisted prefill) and target models that fold speculation into their architecture
- The right answer six months from now isn't on this page yet

<span style="font-size:16px; color:#8b949e;">
All results: gauravmm.github.io/autobench · post: "On Speculative Decoders" · DGX Spark by Ray Aun Fan, benchmarked autonomously by Opus 4.8
</span>
