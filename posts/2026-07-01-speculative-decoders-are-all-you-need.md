# On Speculative Decoders

---

**TL;DR:** use the model's own MTP path when it has one; test EAGLE3 when it does not. On one DGX Spark, MTP lifts [Gemma-4-26B-A4B NVFP4](https://gauravmm.github.io/autobench/configs/gemma-4-26b-a4b-it-vllm-nvfp4-mtp/) to **697.0 tok/s** and [Qwen3.6-35B-A3B NVFP4](https://gauravmm.github.io/autobench/configs/qwen3-6-35b-a3b-nvfp4-vllm-mtp/) to **541.3 tok/s**, both at 32 concurrent requests. The newer Qwen3.8-27B is the cautionary case: MTP helps even with mediocre acceptance, but its gain shrinks from [**+91% at one request**](https://gauravmm.github.io/autobench/configs/qwen3-8-27b-nvfp4-vllm-mtp-c1/) to [**+31% at 32**](https://gauravmm.github.io/autobench/configs/qwen3-8-27b-nvfp4-vllm-mtp-c32/).

These were [autonomously benchmarked](https://gauravmm.github.io/autobench/) by Opus 4.8 on an NVIDIA DGX Spark, generously provided by [Ray Aun Fan](https://www.linkedin.com/in/rayaunfan).

---

A lot of ink and bits are spent speeding up *datacenter-scale* inference: batching, disaggregation, giant KV pools. Speculative decoding is one of the few techniques aimed squarely at the *small, local* case — the single RTX, DGX Spark, or Apple Silicon machine on your desk. Heavy external drafters benefit most at low concurrency; lightweight MTP can keep paying off much farther into the batch curve.

A **speculative decoder** (a.k.a. draft model, drafter, or speculator) is a small, cheap predictor that *guesses the next few tokens* the big model is about to produce. The big ("target") model then performs its decode pass, accepting guesses that match; the first disagreement is where normal decoding resumes. When the guesses are good, you get several tokens for the price of one.

Accepted tokens are nearly free, but running the drafter is not. The rest of this article measures that tradeoff.

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

Four families matter here:

- **[MTP (multi-token prediction)](https://arxiv.org/abs/2404.19737):** prediction heads shipped in the model, or a model-matched assistant checkpoint exposed through the engine's MTP path. This is usually the lightest option.
- **[EAGLE3](https://arxiv.org/abs/2503.01840):** a *separate*, small draft head grafted into the model, reads activations at multiple levels to make its predictions. Quality depends entirely on *which* draft you load.
- **[DFlash](https://github.com/z-lab/dflash):** an external diffusion-based drafter that speculates many (up to 16) tokens per step. High fixed cost, with the chance for huge speedups.
- **[DDTree](https://liranringel.github.io/ddtree/) (emerging):** DFlash with a tree instead of a single draft line. Amazingly quick when it works.

The numbers below come from [**199 completed benchmark configs**](https://gauravmm.github.io/autobench/) on an NVIDIA DGX Spark, generously provided by [Ray Aun Fan](https://www.linkedin.com/in/rayaunfan) — thank you, Ray. The runs were driven semi-autonomously by an Opus 4.8 agent. Unless noted otherwise, concurrency is 32.

## Five rules of speculation

The drafter runs first and proposes a short continuation — 3 tokens for MTP, 5-16 for DFlash depending on the config. This imposes a **fixed cost**, and buys a **variable speedup** depending on how many tokens are accepted. This only pays off when our spare compute and acceptance rates are both good enough.

### Rule 1 — Drafters trade compute for speed {#drafters-trade-compute-for-speed}

Once the GPU is saturated, the drafter must compete with real requests for compute. Native MTP drafters are almost free and provide a fantastic tradeoff. It's the heavy external DFlash drafters that *spend spare compute to buy low-concurrency throughput* — and a busy server has none to spend.

![Decode throughput vs concurrency for Qwen3.6-35B-A3B NVFP4 on vLLM, log-log, three lines: no-spec base, MTP, and DFlash. DFlash narrowly leads at conc-1; MTP leads from conc-2 and climbs to 750 tok/s at conc-128. DFlash beats base only at low batch, then flattens around 425 tok/s and sits below the no-spec baseline from conc-32 on.](assets/plots/mtp_vs_dflash_35b.svg)
{: #fig-concurrency-crossover}

**Figure 1 — The concurrency crossover.** DFlash narrowly wins at conc-1; MTP overtakes it at conc-2 and reaches 750 tok/s at conc-128. The heavy DFlash drafter beats the no-spec baseline only at low concurrency and slips below it from conc-32 on.
{: .figcaption}

Even with spare compute, the heavy DFlash drafter barely beats the built-in MTP; once the batch saturates the GPU it loses badly, even slipping below the no-drafter baseline at conc-32 (407 vs 431). The trade-off curve belongs to the *drafter's cost*, not to speculation itself.

As with everything in LLMs, the exact tradeoff curve is a fingerprint of the method, not a universal law. Later on we'll discuss other trends that confound this simple rule.

### Rule 2 — Agreement is critical to performance {#agreement-is-critical-to-performance}

In one target forward pass, the model computes the probability of each speculated token in parallel. Where the target agrees, we **pretend the token was there all along**; at the first disagreement we discard the rest and let the target generate that token normally. Agreement is a major factor in speedup, but it is not sufficient: draft cost, verification cost, scheduling, and memory decide whether those accepted tokens pay for themselves.

Agreement rates can vary wildly based on methods and tasks. Briefly:

- **MTP** ≈ 3.0 of 4 ([Qwen3.6-27B](https://gauravmm.github.io/autobench/tags/model/#qwen3-6-27b), [35B-A3B](https://gauravmm.github.io/autobench/tags/model/#qwen3-6-35b-a3b)) — that's ~2 of 3 drafted tokens accepted plus the one free "bonus" token from the verify pass. Very efficient.
- **Qwen3.8 MTP** ≈ [2.6](https://gauravmm.github.io/autobench/configs/qwen3-8-27b-nvfp4-vllm-mtp-c32/)–[2.8](https://gauravmm.github.io/autobench/configs/qwen3-8-27b-nvfp4-vllm-mtp-c1/) of 4, or ~52–57% of drafted tokens accepted — weaker than Qwen3.6, yet still useful.
- **EAGLE3** ≈ 2.0-2.4 of 4 ([Gemma-4](https://gauravmm.github.io/autobench/tags/model/#gemma-4-31b); [gpt-oss](https://gauravmm.github.io/autobench/tags/model/#gpt-oss-120b) only with a workload-matched draft).
- **DFlash** ≈ 3.2-4.4 of 11 serving [Qwen3.6-35B-A3B](https://gauravmm.github.io/autobench/tags/model/#qwen3-6-35b-a3b) — collapses after a few positions, leading to much waste.
- **DDTree** reaches **9.74 of 16** at the fastest tree budget and **10.50** at the larger, slower budget on code; chat falls as low as 3.2 of 16 ([Qwen3-Coder-30B-A3B](https://gauravmm.github.io/autobench/tags/model/#qwen3-coder-30b-a3b), research harness).

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

A speculative decoder is a multiplier, not a fix. Three comparisons make the point. Qwen3.6-35B-A3B on NVFP4 with no drafter ([430.8](https://gauravmm.github.io/autobench/configs/qwen3-6-35b-a3b-nvfp4-vllm/)) beats FP8 + MTP ([407.9](https://gauravmm.github.io/autobench/configs/qwen3-6-35b-a3b-vllm-fp8-mtp/)). Qwen3.8-27B repeats the pattern: plain NVFP4 ([210.0](https://gauravmm.github.io/autobench/configs/qwen3-8-27b-nvfp4-vllm-c32/)) edges out FP8 + MTP ([203.0](https://gauravmm.github.io/autobench/configs/qwen3-8-27b-fp8-vllm-mtp-c32/)). And gpt-oss-120b on the stronger vLLM base ([252.8](https://gauravmm.github.io/autobench/configs/gpt-oss-120b-vllm-mxfp4/)) beats the SGLang + EAGLE3 stack ([171.9](https://gauravmm.github.io/autobench/configs/gpt-oss-120b-sglang-mxfp4-eagle3-c32/)).

Get the quant and engine right *first*; speculation compounds a good setup, it can't paper over a bad one.

## The Models

Which method you even *get* is largely decided by the family: MTP needs a shipped head or matched assistant, while EAGLE3 needs a draft trained for that exact model. The tour below follows those boundaries.

![Grouped bar chart of decode tok/s, base vs +MTP at conc-32 on vLLM, for ten Qwen3.6, Qwen3.8, and Gemma-4 configs; MTP adds +26% to +94%, peaking at Gemma-4-E4B FP8 at 1262 tok/s.](assets/plots/base_vs_mtp.svg)
{: #fig-base-vs-mtp}

**Figure 2 — MTP across three model families.** Decode tok/s, base vs +MTP at conc-32 on vLLM, across ten Qwen3.6, Qwen3.8, and Gemma-4 configs; MTP adds +26% to +94%.
{: .figcaption}

### Qwen3.6 — native MTP {#qwen36-native-mtp}

The **[35B-A3B MoE on NVFP4 + MTP hits 541.3 tok/s](https://gauravmm.github.io/autobench/configs/qwen3-6-35b-a3b-nvfp4-vllm-mtp/)**. More important than its rank is why it is quick: it lands on the right side of each of our five rules.

**[Rule 1 — Drafters trade compute for speed](#drafters-trade-compute-for-speed).** Native MTP is nearly free: after DFlash's narrow conc-1 win, MTP leads from conc-2 through conc-128, without the steep spare-compute tax that makes heavy DFlash fade under load.

**[Rule 2 — Agreement](#agreement-is-critical-to-performance).** High acceptance — ~66%, ~3.0 of 4 including the free bonus token.

**[Rule 3 — Drafters are brittle](#drafters-are-brittle).** Robust here by construction: the MTP head ships with the model, so draft and target are matched.

**[Rule 4 — Slower target, bigger relative win](#slower-target-bigger-relative-win).** A light MoE pass on fast NVFP4 leaves little to amortize, so MTP adds "only" **[+26%](https://gauravmm.github.io/autobench/configs/qwen3-6-35b-a3b-nvfp4-vllm-mtp/)** — the small end of the curve.

**[Rule 5 — Speculation can't rescue a bad config](#speculation-cant-rescue-a-bad-config).** That +26% rides on the fastest quant-and-engine combination we measured for this model. Speculation compounds a good config; here it compounds the right base.

One interesting discovery we made is that minor engine details can greatly affect performance ([Rule 3](#drafters-are-brittle)). On the dense 27B NVFP4 + MTP, the **[+46% gain on vLLM](https://gauravmm.github.io/autobench/configs/qwen3-6-27b-nvfp4-vllm-mtp/)** is only **[+10.5% on SGLang](https://gauravmm.github.io/autobench/configs/qwen3-6-27b-nvfp4-sglang-mtp/)**. This seems to be due to scheduling decisions in the engine.

### Qwen3.8 — acceptance is not the whole story {#qwen38-acceptance-is-not-the-whole-story}

Qwen3.8-27B sharpens two of the rules. Its MTP head accepts only [**~52–57%**](https://gauravmm.github.io/autobench/configs/qwen3-8-27b-nvfp4-vllm-mtp-c32/) of drafted tokens, versus roughly 67% for Qwen3.6-27B. Yet MTP still helps at every measured concurrency:

| concurrency | base → MTP | Δ | mean accept-len |
|---:|---|--:|--:|
| 1 | [11.16](https://gauravmm.github.io/autobench/configs/qwen3-8-27b-nvfp4-vllm-c1/) → [21.35](https://gauravmm.github.io/autobench/configs/qwen3-8-27b-nvfp4-vllm-mtp-c1/) | [**+91%**](https://gauravmm.github.io/autobench/configs/qwen3-8-27b-nvfp4-vllm-mtp-c1/) | ~2.8 of 4 |
| 8 | [75.04](https://gauravmm.github.io/autobench/configs/qwen3-8-27b-nvfp4-vllm-c8/) → [126.68](https://gauravmm.github.io/autobench/configs/qwen3-8-27b-nvfp4-vllm-mtp-c8/) | [**+69%**](https://gauravmm.github.io/autobench/configs/qwen3-8-27b-nvfp4-vllm-mtp-c8/) | ~2.6 of 4 |
| 32 | [209.97](https://gauravmm.github.io/autobench/configs/qwen3-8-27b-nvfp4-vllm-c32/) → [274.74](https://gauravmm.github.io/autobench/configs/qwen3-8-27b-nvfp4-vllm-mtp-c32/) | [**+31%**](https://gauravmm.github.io/autobench/configs/qwen3-8-27b-nvfp4-vllm-mtp-c32/) | ~2.6 of 4 |

**Qwen3.8 concurrency sweep — same acceptance, less spare compute.** Acceptance stays in a narrow band while the gain falls from +91% to +31%. The workload still agrees with the drafter; the increasingly busy GPU has less room to exploit that agreement.
{: .figcaption}

There are two costs. MTP raises time to first token at all three points, and at conc-32 it reduces usable KV-cache capacity by about [**22%**](https://gauravmm.github.io/autobench/configs/qwen3-8-27b-nvfp4-vllm-mtp-c32/). It is therefore a strong interactive decode win, not a free throughput switch. The quant lesson also survives: on the slower official FP8 target, MTP adds **[+41%](https://gauravmm.github.io/autobench/configs/qwen3-8-27b-fp8-vllm-mtp-c32/)**, versus **[+31%](https://gauravmm.github.io/autobench/configs/qwen3-8-27b-nvfp4-vllm-mtp-c32/)** on NVFP4 — but plain NVFP4 still narrowly beats FP8 + MTP.

### Gemma-4 — MTP vs EAGLE3, head to head

**Gemma-4 26B-A4B NVFP4 + MTP reaches [697.0 tok/s](https://gauravmm.github.io/autobench/configs/gemma-4-26b-a4b-it-vllm-nvfp4-mtp/)**, ahead of the comparable Qwen models discussed above.

Gemma-4 is the only family here with both Google's model-matched MTP-assistant path and grafted EAGLE3 heads, so it exercises the widest spread of the rules. This is the one place we can put the two paths head-to-head — and the MTP assistant wins.

![Decode throughput vs concurrency for the Gemma-4 26B-A4B family on vLLM NVFP4, log-log, four lines: no-spec base, MTP, EAGLE3, and DiffusionGemma. DiffusionGemma is fastest at batch-1 but saturates near 200 tok/s. MTP leads EAGLE3 at every measured point and peaks at 1380 tok/s at conc-128; both speculative paths become non-viable at conc-256, while the leaner base reaches 1366 tok/s.](assets/plots/gemma_26b_crossover.svg)
{: #fig-gemma-26b-crossover}

**Figure 3 — Gemma-4 26B-A4B across concurrency.** MTP leads EAGLE3 at every measured point and peaks at 1380 tok/s at conc-128. Both speculative paths become non-viable at conc-256; the leaner base reaches 1366 tok/s. [DiffusionGemma](#diffusion-based-models) wins at batch-1 but saturates near 200 tok/s.
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

**[Rule 2 — Agreement](#agreement-is-critical-to-performance).** The MTP assistant posts a higher accept-len (~2.7-2.8 of 4, ~55-65% draft acceptance) than EAGLE3 (~2.0-2.4 of 4). It beats EAGLE3 by **[+17%](https://gauravmm.github.io/autobench/configs/gemma-4-26b-a4b-it-vllm-nvfp4-mtp/)** on 26B-A4B (697.0 vs 596.3) and **[+22%](https://gauravmm.github.io/autobench/configs/gemma-4-31b-it-vllm-nvfp4-mtp/)** on 31B (323.5 vs 264.7).

**[Rule 3 — Drafters are brittle](#drafters-are-brittle).** Three comparable Gemma-4-12B serving paths show how much the full stack matters. These are not an engine-only experiment: the checkpoint source differs between the NVFP4 rows, and llama.cpp uses Q4_K_M.

| engine · quant | base → MTP | Δ | why |
|---|--:|--:|---|
| vLLM · NVFP4 | 503.8 → **[782.4](https://gauravmm.github.io/autobench/configs/gemma-4-12b-it-redhatai-vllm-nvfp4-mtp/)** | **+55%** | overlap scheduler on ✅ |
| SGLang · NVFP4 | 386.6 → **[399.8](https://gauravmm.github.io/autobench/configs/gemma-4-12b-it-axionml-sglang-nvfp4-mtp/)** | +3.4% | overlap scheduler off ❌ |
| llama.cpp · Q4 | 195.3 → **[202.2](https://gauravmm.github.io/autobench/configs/gemma-4-12b-it-llamacpp-mtp/)** | +3.5% | overlap scheduler off ❌ |

**Table 3 — Comparable model, different serving stacks.** vLLM's path posts a +55% gain; the measured SGLang and llama.cpp paths post only +3–4%. The table is diagnostic, not a controlled engine benchmark.
{: .figcaption}

One plausible mechanism is scheduler overlap: vLLM can hide more drafter and CPU overhead, while that overlap is unavailable in llama.cpp and disabled for this SGLang model path. Because the checkpoints also differ, treat scheduling as the leading explanation rather than isolated proof.

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

**[Rule 5 — Speculation can't rescue a bad config](#speculation-cant-rescue-a-bad-config).** The SGLang + LMSYS stack (171.9) is ~32% below vLLM with **no speculation** (252.8). Within vLLM, the same LMSYS draft reaches 246.7 — almost neutral, but still slower than the base. The fastest gpt-oss-120b we measured is vLLM, no spec.

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

This allows them to effectively hedge the continuation, reducing its brittleness. We measured the performance of this setup using the research-grade code on our single DGX Spark and obtained a small speedup:

| workload | metric | none | DFlash (single line) | **DDTree (budget 64)** | DDTree (budget 256) |
|---|---|--:|--:|--:|--:|
| chat (mt-bench) | accept-len | 1.00 | 2.25 | 3.22 | 3.69 |
| | decode tok/s | 18.52 | 16.95 | **20.75** | 17.32 |
| | our speedup | — | **0.92×** | **1.12×** | 0.94× |
| | paper speedup | — | 2.04× | 3.27× | |
| code (HumanEval) | accept-len | 1.00 | 7.96 | 9.74 | 10.50 |
| | decode tok/s | 17.66 | 47.87 | **49.34** | 41.30 |
| | our speedup | — | **2.7×** | **2.8×** | 2.3× |
| | paper speedup | — | 6.09× | 8.22× | |

**Table 5 — DDTree recovers DFlash's loss.** Qwen3-Coder-30B-A3B at batch-1 in the paper's PyTorch harness; the paper reports 8.22× lossless on HumanEval; we measure ~2.8×. Paper columns: [DDTree paper](https://arxiv.org/abs/2604.12989) Table 1, Qwen3-Coder-30B, temp 0.
{: .figcaption}

Where the workload already suits DFlash (code), DDTree performs about the same. On the chat workload, where DFlash fails, DDTree rescues its performance. The speedup depends heavily on how much spare compute the hardware has, so the paper's claimed speedups (on high-end server hardware) are substantially higher than on our little DGX Spark.

**[Rule 1 — Drafters trade compute for speed](#drafters-trade-compute-for-speed).** Even with the tree, there's a tradeoff between the tree budget and time. Even though the larger 256 budget has a higher acceptance, it is *slower* than budget 64 both times. The extra acceptance costs more to verify than it saves.

This is new technology, hot off the presses, so it isn't in vLLM or [SGLang](https://github.com/sgl-project/sglang/discussions/24605). Watch this closely; it's likely going to be a huge part of the future.

### The catch — engine bugs

The speculation math is *lossless* by construction, and adding a drafter should never change what it answers. The catch is that the code delivering that guarantee is young, always changing, and it tends to break when brand-new model architectures are added. [Rule 3: Drafters are brittle](#drafters-are-brittle) applies here too.

These failures surface as failures on launch, unimplemented kernels, unexpected slowdowns, or in the worst-case, quietly wrong output. We repeatedly encountered these errors during our work. Notably:

**Qwen 3.6 + MTP may silently emit incorrect output on vLLM.** These failures are being tracked as malformed tool calls ([#35800](https://github.com/vllm-project/vllm/issues/35800)) and, worse, output collapsing into gibberish ([#36872](https://github.com/vllm-project/vllm/issues/36872)). The only known workaround is to turn MTP off.

When we deployed Qwen 3.6 to run on our own machine, we encountered this exact problem. Thankfully, Qwen is quick enough on [single-stream inference](https://gauravmm.github.io/autobench/configs/qwen3-6-35b-a3b-nvfp4-vllm-c1/) — 74.7 tok/s with MTP off — that MTP is not a strict requirement.

**Qwen 3.6's hybrid attention breaks DFlash/DDTree.** The special attention design of Qwen 3.6 35B-A3B MoE greatly speeds up inference, but makes it much harder to rewind to the last accepted token on token rejection. This leads to blocked runs on [DFlash](https://gauravmm.github.io/autobench/configs/ornith-1-0-35b-aeon-vllm-nvfp4-dflash-blocked/) and [DDTree](https://gauravmm.github.io/autobench/configs/qwen3-6-35b-a3b-ddtree-blocked/).

**Gemma-4's E4B MTP drafter fought the attention kernel.** Native MTP was blocked on vLLM because it was missing a hand-written kernel that could supports both the attention model and the drafter at NVFP4 quantization.

**gpt-oss's harmony channel breaks with EAGLE3.** gpt-oss speaks in structured "harmony" channels, and EAGLE3 corrupts the channel itself, failing requests rather than slowing them. More subtle bugs exist, such as model output collapse ([#27626](https://github.com/vllm-project/vllm/issues/27626)) — drafter on, accuracy gone, tok/s none the wiser.

This pattern repeats across all of our testing. The engine support for MTPs should be treated as brittle, and trusted only when you have tested the specific combination of versions and hardware on a workload that reflects your actual use-case.

## The future

### Diffusion-based Models

DFlash (and DDTree) use a diffusion-based drafter that fills in a whole block of future positions at once, rather than token-by-token. This gives them tremendous speed, but lower accuracy.

Google is taking diffusion all the way into the *target* model with [DiffusionGemma](https://gauravmm.github.io/autobench/tags/model/#diffusiongemma-26b-a4b) — no drafter, no verify pass, the whole model generates 256-token blocks by diffusion and self-corrects as it goes. On the Spark we measured the single-concurrency decode at **[116.0 tok/s at batch-1](https://gauravmm.github.io/autobench/configs/diffusiongemma-26b-a4b-vllm-nvfp4-c1/)** ([Figure 3](#fig-gemma-26b-crossover)). That batch-1 lead is real but doesn't hold: its throughput is nearly flat with concurrency, so the autoregressive Gemma-4 configs — with or without a drafter — sail past it as batch grows (the diffusion line in [Figure 3](#fig-gemma-26b-crossover)). The catch is that output quality lands significantly below the autoregressive Gemma-4 it's built on.

NVIDIA takes a subtler route with [Nemotron-Labs-TwoTower](https://arxiv.org/abs/2606.26493), freezing a standard autoregressive model (Nemotron-3-Nano-30B-A3B) and training a denoiser on top of it. This sidesteps the quality hit DiffusionGemma pays (claimed to keep **98.7%** of the benchmark quality), while achieving a **×2.42×** speedup. The interesting twist is that the same architecture can both verify and *speculate*, blurring the line between a diffusion target and a drafter.

Full two-tower decoding is the most interesting point on the diffusion-vs-autoregressive spectrum right now, and is worth watching closely in the near future.

### Drafter-assisted prefill

Everything we've discussed here speeds up token output, but there may also be a way to accelerate the prefill stage (where the model reads your entire prompt before it says anything) with a drafter.

Drafter-assisted prefill is an area under active research. The basic concept is for the small model to skim the whole prompt and flag which tokens actually matter; the big model prefills only those important tokens. Fewer tokens through the expensive model means a faster first token, up to ~7.7× faster time-to-first-token on a 405B model ([SpecPrefill](https://arxiv.org/abs/2502.02789), ICML 2025) potentially using the *same* drafter as decode.

For long-context, low-concurrency work (exactly the Spark's niche) it's the natural next thing to try.

## So... what should I do?

Start from the five rules. They're the compressed version of everything above, and they'll tell you within a minute whether a given speculator is worth trying:

1. **[Drafters trade compute for speed](#drafters-trade-compute-for-speed)** — a drafter burns spare compute to shorten the critical path, so the win is largest exactly when you have compute to spare (low concurrency) and shrinks as the batch fills the machine.
2. **[Agreement is critical to performance](#agreement-is-critical-to-performance)** — every rejected draft token is wasted work, so acceptance rate (accept-len) is the single number that decides whether a speculator helps or hurts.
3. **[Drafters are brittle](#drafters-are-brittle)** — the same drafter can swing from a huge win to nothing when you change the engine, the workload, or which draft weights you load; nothing here transfers without measuring.
4. **[Slower target, bigger relative win](#slower-target-bigger-relative-win)** — there's more latency to amortize behind a slow target, so the *relative* speedup is largest on the slowest configs and smallest on the ones that were already fast.
5. **[Speculation can't rescue a bad config](#speculation-cant-rescue-a-bad-config)** — a drafter multiplies whatever it's bolted onto, so pick the fastest quant and engine first; a good speculator on a mediocre base still loses to the fast base alone.

None of that substitutes for benchmarking your own model on your own workload. The rules are brittle by their own admission — the numbers here came from one machine, a handful of engines, and two datasets, and Rule 3 is a standing warning that they won't carry cleanly to your setup. Measure the decode rate at the concurrency you actually run, on prompts that look like your traffic, before you commit to a speculator.

And keep watching. This is a fast-moving corner of the field on both sides: new speculators (trees, diffusion drafters, drafter-assisted prefill) and new target models that fold speculation into their architecture, like the two-tower diffusion work above. The right answer six months from now isn't even on this page yet.
