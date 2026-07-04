# On Speculative Decoders

---

**TL;DR:** run native MTP where the model has it; test EAGLE3 where it doesn't. On one DGX Spark the fastest config we measured at 32 concurrent threads is [Gemma-4-26B-A4B NVFP4 + MTP](https://gauravmm.github.io/autobench/tags/model/#gemma-4-26b-a4b) at **697.0 tok/s**, with [Qwen3.6-35B-A3B NVFP4 + MTP](https://gauravmm.github.io/autobench/tags/model/#qwen3-6-35b-a3b) close behind at **541.3 tok/s**.

---

A lot of ink and bits get spilled speeding up *datacenter-scale* inference (batching, disaggregation, giant KV pools). Speculative decoding is the rare trick that is particularly effective at speeding up the *small, local, low-concurrency* case — the single RTX or Apple Silicon chip on your lap.

A **speculative decoder** (a.k.a. draft model, drafter, or speculator) is a small, cheap predictor that *guesses the next few tokens* the big model is about to produce. The big ("target") model then performs its decode pass, accepting guesses that match; the first disagreement is where normal decoding resumes. When the guesses are good, you get several tokens for the price of one.

This means that tokens where the speculative decoder agrees with the target model are nearly free, but there's a base cost to run the speculative decoder. In the rest of this article we'll explore this tradeoff and ground this in real data.

Speculative decoders work well when the next token is easy to guess. Something like this, with one obvious continuation, works well:

<link rel="stylesheet" href="assets/token-stream.css">

<p class="token-stream fork">
<span class="ctx"><span class="tok c0">The</span><span class="tok c1">quick</span><span class="tok c2">brown</span><span class="tok c3">fox</span></span>
<span class="guess"><span class="ell">…</span></span>
<span class="guess"><span class="ell">…</span> <span class="tok c4">jumps</span><span class="tok c5">over</span><span class="tok c0">the</span><span class="tok c1">lazy</span><span class="tok c2">dog</span><span class="tok c3">.</span></span>
</p>

Something like this does not. The drafter bets on one continuation, and the target's single verify pass **accepts** the tokens it agrees with, **rejects** the first disagreement, and discards everything after it:

<p class="token-stream fork">
<span class="ctx"><span class="tok c0">I</span><span class="tok c1">saw</span><span class="tok c2">her</span><span class="tok c3">duck</span></span>
<span class="guess"><span class="ell">…</span></span>
<span class="guess"><span class="ell">…</span> <span class="tok acc">under</span><span class="tok acc">the</span><span class="tok rej">table</span><span class="tok dis">.</span></span>
<span class="guess"><span class="ell">…</span> <span class="tok c4">under</span><span class="tok c5">the</span><span class="tok c2">branch</span></span>
</p>

Top row: the draft as verified — **under the** is accepted (green) and now costs nearly nothing, **table** is rejected (red), and the tail is thrown away (grey). Bottom row: the target generates *branch* in the same pass and decoding resumes from there.

## The Options

Speculative decoding is a fast-moving field, so keep an eye out for new versions.

As of right now, there are three flavours that are common (and one emerging).

- **[MTP (multi-token prediction)](https://arxiv.org/abs/2404.19737):** extra prediction heads baked into the model. (DeepSeek, Qwen3.6, Gemma-4, etc.) The lightest-weight alternative.
- **[EAGLE3](https://arxiv.org/abs/2503.01840):** a *separate*, small draft head grafted into the model, reads activations at multiple levels to make its predictions. Quality depends entirely on *which* draft you load.
- **[DFlash](https://github.com/z-lab/dflash):** an external diffusion-based drafter that speculates many (up to 16) tokens per step. High fixed cost, with the chance for huge speedups.
- **[DDTree](https://liranringel.github.io/ddtree/) (emerging):** DFlash with a tree instead of a single draft line. Amazingly quick when it works.

The numbers below come from 149 benchmark configs run on an NVIDIA DGX Spark, generously provided by [Ray Aun Fan](https://www.linkedin.com/in/rayaunfan) — thank you, Ray! These benchmarks were run semi-autonomously by an Opus 4.8 agent over about a week. Full results are [on the autobench website](https://gauravmm.github.io/autobench/).

## Five rules of speculation

The drafter runs first and proposes a short continuation — 3 tokens for MTP, 5-16 for DFlash depending on the config. This imposes a **fixed cost**, and buys a **variable speedup** depending on how many tokens are accepted. This only pays off when our spare compute and acceptance rates are both good enough.

### Rule 1 — Drafters trade compute for speed {#drafters-trade-compute-for-speed}

Once the GPU is saturated, the drafter must compete with real requests for compute. Native MTP drafters are almost free and provide a fantastic tradeoff. It's the heavy external DFlash drafters that *spend spare compute to buy low-concurrency throughput* — and a busy server has none to spend.

![Decode throughput vs concurrency for Qwen3.6-35B-A3B NVFP4 on vLLM, log-log, three lines: no-spec base, MTP, and DFlash. At conc-1 the three cluster (base 75, MTP 94, DFlash 100); MTP then leads at every concurrency (541 tok/s at conc-32); DFlash beats base only at low batch and dips below the no-spec baseline by conc-32 (407 vs base 431).](assets/plots/mtp_vs_dflash_35b.svg)
{: #fig-concurrency-crossover}

**Figure 1 — The concurrency crossover.** Decode tok/s vs concurrency for Qwen3.6-35B-A3B NVFP4 on vLLM: MTP leads at every batch size, while the heavy DFlash drafter beats the no-spec baseline only at low concurrency and slips below it by conc-32.
{: .figcaption}

Even with spare compute, the heavy DFlash drafter barely beats the built-in MTP; once the batch saturates the GPU it loses badly, even slipping below the no-drafter baseline at conc-32 (407 vs 431). The trade-off curve belongs to the *drafter's cost*, not to speculation itself.

As with everything in LLMs, the exact tradeoff curve is a fingerprint of the method, not a universal law. Later on we'll discuss other trends that confound this simple rule.

### Rule 2 — Agreement is critical to performance {#agreement-is-critical-to-performance}

In one target forward pass, the model computes the probability of each speculated token in parallel. Where the target agrees, we **pretend the token was there all along**; at the first disagreement we discard the rest and let the target generate that token normally, then re-speculate.

- **MTP** ≈ 3.0 of 4 ([Qwen3.6-27B](https://gauravmm.github.io/autobench/tags/model/#qwen3-6-27b), [35B-A3B](https://gauravmm.github.io/autobench/tags/model/#qwen3-6-35b-a3b)) — that's ~2 of 3 drafted tokens accepted plus the one free "bonus" token from the verify pass. Very efficient.
- **EAGLE3** ≈ 2.0-2.4 of 4 ([Gemma-4](https://gauravmm.github.io/autobench/tags/model/#gemma-4-31b); [gpt-oss](https://gauravmm.github.io/autobench/tags/model/#gpt-oss-120b) only with a workload-matched draft).
- **DFlash** ≈ 3.2-4.4 of 11 serving [Qwen3.6-35B-A3B](https://gauravmm.github.io/autobench/tags/model/#qwen3-6-35b-a3b) — collapses after a few positions, leading to much waste.
- **DDTree** ≈ **9.7 of 16 on code**, as low as 3.2 of 16 on chat ([Qwen3-Coder-30B-A3B](https://gauravmm.github.io/autobench/tags/model/#qwen3-coder-30b-a3b), research harness) — DFlash's block draft rebuilt as a *tree* of candidate continuations, verified together so more of each block survives. Full numbers in the Qwen3-Coder section below.

### Rule 3 — Drafters are brittle {#drafters-are-brittle}

Drafters are being judged by the target model's token choices, and are fed by the target model's own KV cache. That's what makes the draft cheap, but also fragile. Even if the drafter produces a plausible next token, it is only accepted if it is the *same next token that the target model would have made*.

This means that the effectiveness depends on:

1. the drafter model,
2. the exact training and quantization of the target model,
3. the workload, and
4. the serving software.

Change any one and the win can evaporate or the launch can fail outright.

The starkest case: **gpt-oss-120b on vLLM, one ShareGPT workload — swap only the EAGLE3 draft**, and decode moves 43 points, from −45% to roughly neutral (Table 4, in the gpt-oss section below). Before picking a drafter, test it in the exact configuration you will be using.

### Rule 4 — Slower target, bigger relative win {#slower-target-bigger-relative-win}

The costlier the target's forward pass, the more idle bandwidth the drafter hides behind — so the *relative* speedup runs inversely to base speed. Two knobs move that cost: **quant** (a slower FP8 base gains more than the same model on faster NVFP4) and **architecture** (a dense model gains more than a comparable MoE, whose lighter per-token pass leaves less to amortize). Sort the four Qwen3.6 MTP runs from slowest base to fastest and the relative win falls straight down the table:

| model · quant | base → MTP | Δ |
|---|---|--:|
| Qwen3.6-27B · FP8 | 154.7 → 240.9 | **+56%** |
| Qwen3.6-27B · NVFP4 | 187.7 → 274.1 | **+46%** |
| Qwen3.6-35B-A3B · FP8 | 286.0 → 407.9 | **+43%** |
| Qwen3.6-35B-A3B · NVFP4 | 430.8 → 541.3 | **+26%** |

**Table 1 — Slower base, bigger relative win.** Four Qwen3.6 MTP runs at conc-32 on vLLM, sorted slowest base to fastest; the MTP speedup falls monotonically from +56% to +26%.
{: .figcaption}

Each model gains more on its slower FP8 quant than its faster NVFP4 quant, and the 27B dense architecture gains more than the 35B-A3B MoE architecture.

The flip side ([Rule 5](#speculation-cant-rescue-a-bad-config)): NVFP4 *without* a speculator (430.8) still out-decodes FP8 *with* MTP (407.9) — pick the fast quant first, then add the drafter.

### Rule 5 — Speculation can't rescue a bad config {#speculation-cant-rescue-a-bad-config}

A speculative decoder is a multiplier, not a fix. Twice in our data, the plainer setup with **no speculation at all** out-decodes a fancier one running its best available draft: Qwen3.6-35B-A3B on NVFP4 with no drafter ([430.8](https://gauravmm.github.io/autobench/configs/qwen3-6-35b-a3b-nvfp4-vllm/)) beats FP8 + MTP ([407.9](https://gauravmm.github.io/autobench/configs/qwen3-6-35b-a3b-vllm-fp8-mtp/)), and gpt-oss-120b MXFP4 on vLLM with no drafter ([252.8](https://gauravmm.github.io/autobench/configs/gpt-oss-120b-vllm-mxfp4/)) beats SGLang running the best EAGLE3 draft ([171.9](https://gauravmm.github.io/autobench/configs/gpt-oss-120b-sglang-mxfp4-eagle3-c32/)).

Get the quant and engine right *first*; speculation compounds a good setup, it can't paper over a bad one.

## The Models

Which method you even *get* is largely decided by the family — MTP only exists where the lab baked in a head, EAGLE3 only where someone has trained a draft for that exact model. So the walk below goes family by family: Qwen3.6 and Gemma-4 with native MTP, gpt-oss with EAGLE3 only, then Qwen3-Coder with DFlash and DDTree.

![Grouped bar chart of decode tok/s, base vs +MTP at conc-32 on vLLM, for eight Qwen3.6 and Gemma-4 configs; MTP adds +26% to +94%, peaking at Gemma-4-E4B FP8 at 1262 tok/s.](assets/plots/base_vs_mtp.svg)
{: #fig-base-vs-mtp}

**Figure 2 — Native MTP across the family.** Decode tok/s, base vs +MTP at conc-32 on vLLM, across eight Qwen3.6 and Gemma-4 configs; MTP adds +26% to +94%.
{: .figcaption}

### Qwen3.6 — native MTP {#qwen36-native-mtp}

This family runs a close second on the board: the **[35B-A3B MoE on NVFP4 + MTP hits 541.3 tok/s](https://gauravmm.github.io/autobench/configs/qwen3-6-35b-a3b-nvfp4-vllm-mtp/)** — bettered only by Gemma-4-26B-A4B's native MTP (below). The decode is so quick because it lands on the right side of each of our five rules.

**[Rule 1 — Drafters trade compute for speed](#drafters-trade-compute-for-speed).** Native MTP is nearly free — it wins at *every* concurrency (the MTP line in [Figure 1](#fig-concurrency-crossover)), with none of the spare-compute tax that makes heavy DFlash fade under load.

**[Rule 2 — Agreement](#agreement-is-critical-to-performance).** High acceptance — ~66%, ~3.0 of 4 including the free bonus token.

**[Rule 3 — Drafters are brittle](#drafters-are-brittle).** Robust here by construction: the MTP head ships with the model, so draft and target are matched.

**[Rule 4 — Slower target, bigger relative win](#slower-target-bigger-relative-win).** A light MoE pass on fast NVFP4 leaves little to amortize, so MTP adds "only" **[+26%](https://gauravmm.github.io/autobench/configs/qwen3-6-35b-a3b-nvfp4-vllm-mtp/)** — the small end of the curve.

**[Rule 5 — Speculation can't rescue a bad config](#speculation-cant-rescue-a-bad-config).** That +26% rides on the fastest quant-and-engine we measured, so the absolute number lands near the very top of the board — second only to Gemma-4-26B-A4B + MTP. Speculation compounds a good config; here it compounds one of the best.

One interesting discovery we made is that minor engine details can greatly affect performance ([Rule 3](#drafters-are-brittle)). On the dense 27B NVFP4 + MTP, the **[+46% gain on vLLM](https://gauravmm.github.io/autobench/configs/qwen3-6-27b-nvfp4-vllm-mtp/)** is only **[+10.5% on SGLang](https://gauravmm.github.io/autobench/configs/qwen3-6-27b-nvfp4-sglang-mtp/)**. This seems to be due to scheduling decisions in the engine.

### Gemma-4 — MTP vs EAGLE3, head to head

**Gemma-4 26B-A4B NVFP4 + MTP [tops the board at 697.0 tok/s](https://gauravmm.github.io/autobench/configs/gemma-4-26b-a4b-it-vllm-nvfp4-mtp/)**, ahead of Qwen.

Gemma-4 is the only family here with *both* a native assistant-MTP path and grafted EAGLE3 heads, so it exercises the widest spread of the rules. Because the same model also carries a grafted **[EAGLE3 head (596.3)](https://gauravmm.github.io/autobench/configs/gemma-4-26b-a4b-it-vllm-nvfp4-eagle3/)**, this is the one place we can put the two drafters head-to-head — and native MTP wins.

![Decode throughput vs concurrency for the Gemma-4 26B-A4B family on vLLM NVFP4, log-log, four lines: no-spec base, MTP, EAGLE3, and DiffusionGemma. DiffusionGemma is fastest at batch-1 (116 tok/s) but saturates near 200 tok/s and stays flat; the three autoregressive lines climb with concurrency and overtake it — MTP leads past conc-4 and is still rising at 697 tok/s at conc-32 (the sweep's cap, memory-bound not saturated), EAGLE3 at 596, no-spec base at 421.](assets/plots/gemma_26b_crossover.svg)
{: #fig-gemma-26b-crossover}

**Figure 3 — Gemma-4 26B-A4B, the whole family across concurrency.** Decode tok/s vs concurrency on vLLM NVFP4. Native MTP leads at every batch past conc-4; grafted EAGLE3 trails it; the [DiffusionGemma](#diffusion-based-models) target wins at batch-1 but saturates near 200 tok/s while the autoregressive lines keep scaling.
{: .figcaption}

We compare MTP and EAGLE3 drafters, and find that MTP wins the two head-to-head rows outright:

| model · quant | base | → MTP | Δ | → EAGLE3 | Δ |
|---|--:|--:|--:|--:|--:|
| E4B · FP8 | 869.7 | **[1261.5](https://gauravmm.github.io/autobench/configs/gemma-4-e4b-it-vllm-fp8-mtp/)** | +45% | [—](https://gauravmm.github.io/autobench/configs/gemma-4-e4b-it-vllm-fp8-eagle3/) | — |
| 12B · NVFP4 | 503.8 | **[782.4](https://gauravmm.github.io/autobench/configs/gemma-4-12b-it-redhatai-vllm-nvfp4-mtp/)** | +55% | [—](https://gauravmm.github.io/autobench/configs/gemma-4-12b-it-redhatai-vllm-nvfp4-eagle3/) | — |
| 26B-A4B · NVFP4 | 421.1 | **[697.0](https://gauravmm.github.io/autobench/configs/gemma-4-26b-a4b-it-vllm-nvfp4-mtp/)** | +66% | [596.3](https://gauravmm.github.io/autobench/configs/gemma-4-26b-a4b-it-vllm-nvfp4-eagle3/) | +42% |
| 31B · NVFP4 | 167.0 | **[323.5](https://gauravmm.github.io/autobench/configs/gemma-4-31b-it-vllm-nvfp4-mtp/)** | +94% | [264.7](https://gauravmm.github.io/autobench/configs/gemma-4-31b-it-vllm-nvfp4-eagle3/) | +59% |

**Table 2 — MTP vs EAGLE3 across Gemma-4.** Decode tok/s at conc-32 on vLLM, base vs each drafter. MTP wins both head-to-head rows; the two small models have no usable EAGLE3 head (dashes link to why).
{: .figcaption}

Because it hands us both drafters across four sizes, Gemma-4 is the cleanest illustration of three of our rules.

**[Rule 2 — Agreement](#agreement-is-critical-to-performance).** Native MTP posts a higher accept-len (~2.7-2.8 of 4, ~55-65% draft acceptance) than EAGLE3 (~2.0-2.4 of 4), and that decides the head-to-head: MTP beats EAGLE3 by **[+17%](https://gauravmm.github.io/autobench/configs/gemma-4-26b-a4b-it-vllm-nvfp4-mtp/)** on 26B-A4B (697.0 vs 596.3) and **[+22%](https://gauravmm.github.io/autobench/configs/gemma-4-31b-it-vllm-nvfp4-mtp/)** on 31B (323.5 vs 264.7).

**[Rule 3 — Drafters are brittle](#drafters-are-brittle),** and the engine bites hardest. Hold the model, quant, and MTP drafter fixed at Gemma-4-12B, swap only the engine, and the win swings from huge to nil:

| engine · quant | base → MTP | Δ | why |
|---|--:|--:|---|
| vLLM · NVFP4 | 503.8 → **[782.4](https://gauravmm.github.io/autobench/configs/gemma-4-12b-it-redhatai-vllm-nvfp4-mtp/)** | **+55%** | overlap scheduler on ✅ |
| SGLang · NVFP4 | 386.6 → **[399.8](https://gauravmm.github.io/autobench/configs/gemma-4-12b-it-axionml-sglang-nvfp4-mtp/)** | +3.4% | overlap scheduler off ❌ |
| llama.cpp · Q4 | 195.3 → **[202.2](https://gauravmm.github.io/autobench/configs/gemma-4-12b-it-llamacpp-mtp/)** | +3.5% | overlap scheduler off ❌ |

**Table 3 — Same drafter, three engines.** Gemma-4-12B NVFP4 + MTP held fixed, only the engine changes; vLLM's overlap scheduler turns a +55% win into +3–4% on SGLang and llama.cpp.
{: .figcaption}

The overlap scheduler runs work concurrently instead of sequentially, allowing the drafter (and CPU) overhead to be hidden. This is not available on llama.cpp, and disabled for this model under the current SGLang, hence the poor performance gain.

**[Rule 4 — Slower target, bigger relative win](#slower-target-bigger-relative-win).** Read Table 2 down its base&rarr;spec columns: the slower dense **31B** out-gains the faster MoE **26B-A4B** on both drafters — **+94% vs +66%** with MTP, **+59% vs +42%** with EAGLE3.

### gpt-oss — EAGLE3 only, the draft is everything

No native MTP head, so EAGLE3 is the only option — and gpt-oss is where the *draft-is-everything* rule is sharpest:

| engine · draft | base → EAGLE3 | Δ | note |
|---|---|---|---|
| SGLang · LMSYS draft | 140.3 → 171.9 | **+22%** | mixed engine images |
| vLLM · LMSYS draft | 252.8 → 246.7 | **−2.4%** | neutral |
| vLLM · NVIDIA draft | 252.8 → 138.5 | **−45%** | wrong draft, saturated model |

**Table 4 — gpt-oss-120b EAGLE3, engine × draft.** The draft dominates: on vLLM the same model swings from −45% (NVIDIA draft) to −2.4% (LMSYS), and no spec config beats vLLM's no-spec baseline (252.8).
{: .figcaption}

**[Rule 3 — Drafters are brittle](#drafters-are-brittle).** The draft alone moves 43 points. Same model, workload, and engine (vLLM): swapping NVIDIA's throughput-tuned draft (~9% accept) for LMSYS/SpecForge (~29% accept) rescues −45% to roughly neutral.

**[Rule 5 — Speculation can't rescue a bad config](#speculation-cant-rescue-a-bad-config).** SGLang *with* the best draft (171.9) is still ~32% below vLLM with **no speculation at all** (252.8). The fastest gpt-oss-120b we measured is vLLM, no spec.

### Qwen3-Coder-30B-A3B — DFlash and DDTree

So far, we have seen DFlash lag behind MTP and EAGLE3, due to its weight and low acceptance. Qwen3-Coder-30B-A3B, for example, only accepts 2.25 of 16 tokens on chat datasets, which is disappointingly low for a high-cost drafter like DFlash.

**[Rule 2 — Agreement](#agreement-is-critical-to-performance).** DFlash is redeemed by the *workload*: on templated, low-entropy code (HumanEval), the same Qwen3-Coder-30B-A3B drafter nails long spans: **[7.96 of 16](https://gauravmm.github.io/autobench/configs/qwen3-coder-30b-a3b-ddtree-humaneval/)**, a 2.7× decode win — a bigger *relative* multiplier than any autoregressive drafter here posts, albeit at batch-1 throughput in a research harness.

**[Rule 3 — Drafters are brittle](#drafters-are-brittle).** The workload alone decides whether DFlash is dead weight or the fastest thing on the box. This brittleness is because DFlash bets everything on *one* long draft continuation, the probability of which quickly decays to nothing.

A brand-new technique called [DDTree](https://liranringel.github.io/ddtree/) (arXiv [2604.12989](https://arxiv.org/abs/2604.12989)) is designed to wring more accepted tokens out of the same drafter by building a tree of likely continuations and verifying it in a single pass. They construct a prefix tree like this of (typically) about 64 paths and verify the most likely outcome:

<p class="token-stream fork tree">
<span class="ctx"><span class="tok c0">I</span><span class="tok c1">saw</span><span class="tok c2">her</span><span class="tok c3">duck</span></span>
<span class="guess"><span class="ell">…</span></span>
<span class="guess"><span class="ell">…</span> <span class="tok c4">under</span><span class="tok c5">the</span></span>
<span class="sub"><span class="ell">…</span></span>
<span class="sub"><span class="ell">…</span> <span class="tok c0">branch</span><span class="tok c1">.</span></span>
<span class="sub"><span class="ell">…</span> <span class="tok c0">table</span><span class="tok c1">.</span></span>
<span class="guess"><span class="ell">…</span> <span class="tok c4">waddle</span></span>
<span class="sub"><span class="ell">…</span></span>
<span class="sub"><span class="ell">…</span> <span class="tok c5">away</span><span class="tok c0">.</span></span>
<span class="sub"><span class="ell">…</span> <span class="tok c5">across</span><span class="tok c0">the</span><span class="tok c1">pond</span><span class="tok c2">.</span></span>
</p>

This allows them to effectively hedge the continuation, reducing its brittleness. We measured the performance of this setup using the research-grade code on our single DGX Spark and obtained an approximately 2.8× speedup.

| workload | method | accept-len | decode tok/s | our speedup | paper speedup |
|---|---|--:|--:|--:|--:|
| chat (mt-bench) | none | 1.00 | 18.52 | — | — |
| | DFlash (single line) | 2.25 | 16.95 | **0.92×** | 2.04× |
| | **DDTree (budget 64)** | 3.22 | **20.75** | **1.12×** | 3.27× |
| | DDTree (budget 256) | 3.69 | 17.32 | 0.94× | |
| code (HumanEval) | none | 1.00 | 17.66 | — | — |
| | DFlash (single line) | 7.96 | 47.87 | **2.7×** | 6.09× |
| | **DDTree (budget 64)** | 9.74 | **49.34** | **2.8×** | 8.22× |
| | DDTree (budget 256) | 10.50 | 41.30 | 2.3× | |

**Table 5 — DDTree recovers DFlash's loss.** Qwen3-Coder-30B-A3B at batch-1 in the paper's PyTorch harness; the paper reports 8.22× lossless on HumanEval; we measure ~2.8×. Paper columns: [DDTree paper](https://arxiv.org/abs/2604.12989) Table 1, Qwen3-Coder-30B, temp 0.
{: .figcaption}

Where the workload already suits DFlash (code), DDTree performs about the same. On the chat workload, where DFlash fails, DDTree rescues its performance.

**[Rule 1 — Drafters trade compute for speed](#drafters-trade-compute-for-speed).** Even with the tree, there's a tradeoff between the tree budget and time. Even though the larger 256 budget has a higher acceptance, it is *slower* than budget 64 both times. The extra acceptance costs more to verify than it saves.

This is new technology, hot off the presses, so it isn't in vLLM or [SGLang](https://github.com/sgl-project/sglang/discussions/24605). Watch this closely; it's likely going to be a huge part of the future.

## The future

### Diffusion-based Models

DFlash (and DDTree) use a diffusion-based drafter that fills in a whole block of future positions at once, rather than token-by-token. This gives them tremendous speed, but lower accuracy.

Google is taking diffusion all the way into the *target* model with [DiffusionGemma](https://gauravmm.github.io/autobench/tags/model/#diffusiongemma-26b-a4b) — no drafter, no verify pass, the whole model generates 256-token blocks by diffusion and self-corrects as it goes. On the Spark we measured it at **[116.0 tok/s at batch-1](https://gauravmm.github.io/autobench/configs/diffusiongemma-26b-a4b-vllm-nvfp4-c1/)** and **[200.7 tok/s at conc-32](https://gauravmm.github.io/autobench/configs/diffusiongemma-26b-a4b-vllm-nvfp4/)** (NVFP4, 107 GB peak). That batch-1 lead is real but doesn't hold: its throughput is nearly flat with concurrency, so the autoregressive Gemma-4 configs — with or without a drafter — sail past it as batch grows (the diffusion line in [Figure 3](#fig-gemma-26b-crossover)). The catch is the one Google admits: output quality lands below the autoregressive Gemma-4 it's built on.

TODO: Add a reference to Nemotron Twotowers.

### Drafter-assisted prefill

Everything we've discussed here speeds up token output, but there may also be a way to accelerate the prefill stage (where the model reads your entire prompt before it says anything) with a drafter.

**Drafter-assisted prefill** is an area under active research. The basic concept is for the small model to skim the whole prompt and flag which tokens actually matter; the big model prefills only those important tokens. Fewer tokens through the expensive model means a faster first token, up to ~7.7× faster time-to-first-token on a 405B model ([SpecPrefill](https://arxiv.org/abs/2502.02789), ICML 2025) potentially using the *same* drafter as decode.

For long-context, low-concurrency work (exactly the Spark's niche) it's the natural next thing to try.

## So... what should I do?

1. Look at the five rules above
2. Benchmark your model against your actual workload.
3. Keep an eye out for advances in this area, both in speculators and in fundamental models.
