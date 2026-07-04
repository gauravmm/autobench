#!/usr/bin/env -S uv run --with seaborn --with pandas --no-project python
"""Generate the blog's data charts as SVG.

Run:  ./assets/make_plots.py         (uv pulls seaborn/pandas into a throwaway env)
Data: assets/data/*.csv   →   Output: assets/plots/*.svg  (gitignored, regenerate on demand)

Add a chart = add a CSV + a function + one call at the bottom. No framework.
"""
import pathlib
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import matplotlib.ticker
import pandas as pd
import seaborn as sns

HERE = pathlib.Path(__file__).parent
DATA = HERE / "data"
OUT = HERE / "plots"
OUT.mkdir(exist_ok=True)

# dataviz palette (light mode, validated): neutral baseline + blue/aqua categorical slots.
BASE, MTP, AQUA = "#898781", "#2a78d6", "#1baf7a"
EAGLE = "#c96a2b"  # 4th categorical slot (burnt orange) — distinct from blue/aqua/grey
sns.set_theme(style="whitegrid", font="sans-serif", rc={"grid.color": "#eeeeee"})

# ponytail: static SVG for a Jekyll post — no hover/dark-mode/table-view layer (those
# are the interactive-HTML path). Relief rule met by direct value labels on every bar.


def label_bars(ax, fmt="{:.0f}"):
    for c in ax.containers:
        ax.bar_label(c, fmt=fmt, padding=2, fontsize=8, color="#52514e")


def base_vs_mtp():
    df = pd.read_csv(DATA / "base_vs_mtp.csv")
    df["label"] = df["model"] + "\n" + df["quant"]
    long = df.melt(id_vars="label", value_vars=["base", "mtp"],
                   var_name="config", value_name="decode")
    long["config"] = long["config"].map({"base": "base", "mtp": "+ MTP"})

    fig, ax = plt.subplots(figsize=(10, 4.2))
    sns.barplot(long, x="label", y="decode", hue="config",
                palette={"base": BASE, "+ MTP": MTP}, saturation=1, ax=ax)
    label_bars(ax)
    ax.set_xlabel("")
    ax.set_ylabel("decode tok/s (aggregate, conc-32)")
    ax.set_title("Native MTP vs base — vLLM, ShareGPT V3")
    ax.legend(title="", frameon=False)
    ax.tick_params(axis="x", labelsize=8)
    sns.despine(ax=ax)
    fig.tight_layout()
    fig.savefig(OUT / "base_vs_mtp.svg")
    plt.close(fig)
    print("wrote", OUT / "base_vs_mtp.svg")


def mtp_vs_dflash():
    df = pd.read_csv(DATA / "mtp_vs_dflash_35b.csv")
    fig, ax = plt.subplots(figsize=(7, 4.4))
    order = ["base", "MTP", "DFlash"]
    sns.lineplot(df, x="concurrency", y="decode", hue="method", style="method",
                 hue_order=order, style_order=order, markers=True, dashes=False,
                 markersize=8, linewidth=2,
                 palette={"base": BASE, "MTP": MTP, "DFlash": AQUA}, ax=ax)
    ax.set_xscale("log", base=2)
    ax.set_yscale("log", base=10)
    ax.set_xticks(sorted(df.concurrency.unique()))
    ax.set_yticks([100, 200, 300, 500, 750])
    ax.xaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.yaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    ax.grid(True, axis="y", which="major")

    # direct value labels at both ends instead of relying on the legend (aqua is sub-3:1 → relief rule).
    # conc-1 points cluster (base 75 · MTP 94 · DFlash 100), so nudge the two close ones apart vertically.
    left_dy = {"base": 0, "MTP": -6, "DFlash": 6}
    for method, color in (("base", BASE), ("MTP", MTP), ("DFlash", AQUA)):
        pts = df[df.method == method].sort_values("concurrency")
        end = pts.iloc[-1]
        ax.annotate(f"{method} {end.decode:.0f}/s", (end.concurrency, end.decode),
                    xytext=(6, 0), textcoords="offset points", va="center",
                    fontsize=9, color=color, fontweight="bold")
        start = pts.iloc[0]
        ax.annotate(f"{start.decode:.0f}", (start.concurrency, start.decode),
                    xytext=(-7, left_dy[method]), textcoords="offset points",
                    ha="right", va="center", fontsize=9, color=color, fontweight="bold")

    # conc-32 = the headline operating point: thick vertical rule + bare value labels there.
    ax.axvline(32, color="#eeeeee", lw=3, zorder=0)  # match gridline grey
    c32 = {"base": (430.76, BASE, dict(xytext=(0, 7), va="bottom")),     # above
           "MTP": (541.26, MTP, dict(xytext=(0, 7), va="bottom")),      # above
           "DFlash": (407.07, AQUA, dict(xytext=(0, -8), va="top"))}    # below
    for _m, (val, color, kw) in c32.items():
        ax.annotate(f"{val:.0f}/s", (32, val), textcoords="offset points",
                    ha="center", color=color, fontsize=9, fontweight="bold", **kw)

    # crossover: DFlash leads only at conc-1 (101.9 > 93.9); MTP is ahead from conc-2 on.
    ax.annotate("MTP overtakes\nby conc-2", (2, 161.21), xytext=(1.6, 300),
                textcoords="data", ha="center", fontsize=8, color="black",
                arrowprops=dict(arrowstyle="->", color="black", lw=1, shrinkA=4, shrinkB=8))
    # MTP knees at c128 (750, +12% over c64); DFlash flat from c32 (~425); c128 is the memory ceiling.
    ax.annotate("DFlash is flat, MTP is saturating,\nbut base still climbs", (64, 420.35),
                xytext=(90, 193), textcoords="data", fontsize=8, color="black", ha="center",
                arrowprops=dict(arrowstyle="->", color="black", lw=1, shrinkA=4, shrinkB=8))

    ax.set_xlabel("concurrency (requests)")
    ax.set_ylabel("decode tok/s (aggregate)")
    ax.set_title("Qwen3.6-35B-A3B NVFP4, vLLM")
    ax.legend(title="", frameon=False, loc="upper left")
    ax.margins(x=0.12)
    # ponytail: DFlash conc-8/32 not measured — footnote it rather than hide the gap.
    sns.despine(ax=ax)
    fig.tight_layout()
    fig.savefig(OUT / "mtp_vs_dflash_35b.svg")
    plt.close(fig)
    print("wrote", OUT / "mtp_vs_dflash_35b.svg")


def gemma_26b_crossover():
    df = pd.read_csv(DATA / "gemma_26b_crossover.csv")
    fig, ax = plt.subplots(figsize=(7, 4.4))
    order = ["base", "MTP", "EAGLE3", "diffusion"]
    colors = {"base": BASE, "MTP": MTP, "EAGLE3": EAGLE, "diffusion": AQUA}
    sns.lineplot(df, x="concurrency", y="decode", hue="method", style="method",
                 hue_order=order, style_order=order, markers=True, dashes=False,
                 markersize=8, linewidth=2, palette=colors, ax=ax)
    ax.set_xscale("log", base=2)
    ax.set_yscale("log", base=10)
    ax.set_xticks(sorted(df.concurrency.unique()))
    ax.set_yticks([30, 50, 100, 200, 400, 700, 1400])
    ax.xaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.yaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    ax.grid(True, axis="y", which="major")

    # direct value labels at both ends (relief rule — legend colors go sub-3:1 on white).
    # conc-1 cluster: base 29 · EAGLE3 50 · MTP 57 · diffusion 116 — nudge the close EAGLE3/MTP apart.
    left_dy = {"base": 0, "EAGLE3": -6, "MTP": 6, "diffusion": 0}
    # MTP & EAGLE3 both end at conc-128; split them (MTP above, EAGLE3 below) so the labels clear.
    end_kw = {"base": dict(xytext=(6, 0), ha="left", va="center"),
              "MTP": dict(xytext=(0, 7), ha="center", va="bottom"),     # above the line at c128
              "EAGLE3": dict(xytext=(6, -4), ha="left", va="center"),   # right of the node, nudged down
              "diffusion": dict(xytext=(6, 0), ha="left", va="center")}
    for method in order:
        pts = df[df.method == method].sort_values("concurrency")
        end = pts.iloc[-1]
        # diffusion: keep only the word to the right; its 201/s value goes below at conc-32 (see c32 group).
        end_text = "diffusion" if method == "diffusion" else f"{method} {end.decode:.0f}/s"
        ax.annotate(end_text, (end.concurrency, end.decode),
                    textcoords="offset points", fontsize=9,
                    color=colors[method], fontweight="bold", **end_kw[method])
        start = pts.iloc[0]
        ax.annotate(f"{start.decode:.0f}", (start.concurrency, start.decode),
                    xytext=(-7, left_dy[method]), textcoords="offset points",
                    ha="right", va="center", fontsize=9, color=colors[method], fontweight="bold")

    # conc-32 = headline operating point: thick gridline-grey rule + bare /s labels below each line.
    ax.axvline(32, color="#eeeeee", lw=3, zorder=0)  # match gridline grey
    c32 = {"base": (421.13, dict(xytext=(0, -8), va="top")),        # below
           "MTP": (696.98, dict(xytext=(0, 7), va="bottom")),      # above
           "EAGLE3": (596.32, dict(xytext=(0, -8), va="top")),     # below
           "diffusion": (200.66, dict(xytext=(0, -8), va="top"))}  # below (word stays to the right)
    for method, (val, kw) in c32.items():
        ax.annotate(f"{val:.0f}/s", (32, val), textcoords="offset points",
                    ha="center", color=colors[method], fontsize=9, fontweight="bold", **kw)

    # crossover: diffusion wins low batch but saturates ~200; autoregressive lines scale past it.
    ax.annotate("diffusion saturates ~200;\nautoregressive scales past it", (16, 199.29),
                xytext=(16, 88), textcoords="data", ha="center", fontsize=8, color="black",
                arrowprops=dict(arrowstyle="->", color="black", lw=1, shrinkA=4, shrinkB=8))
    # ceiling: MTP/EAGLE3 peak at c128 then OOM at c256; base is leaner, survives to 1366.
    ax.annotate("MTP & EAGLE3 hit the\nmemory wall (OOM at c256);\nleaner base survives", (128, 1380),
                xytext=(4, 900), textcoords="data", fontsize=8, color="black",
                arrowprops=dict(arrowstyle="->", color="black", lw=1, shrinkA=4, shrinkB=8))

    ax.set_xlabel("concurrency (requests)")
    ax.set_ylabel("decode tok/s (aggregate)")
    ax.set_title("Gemma-4-26B-A4B NVFP4, vLLM")
    ax.legend(title="", frameon=False, loc="upper left")
    ax.margins(x=0.10)
    sns.despine(ax=ax)
    fig.tight_layout()
    fig.savefig(OUT / "gemma_26b_crossover.svg")
    plt.close(fig)
    print("wrote", OUT / "gemma_26b_crossover.svg")


if __name__ == "__main__":
    base_vs_mtp()
    mtp_vs_dflash()
    gemma_26b_crossover()
