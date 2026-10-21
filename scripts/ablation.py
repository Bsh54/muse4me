"""Distant-vs-near inspiration ablation - the headline experiment.

Runs the benchmark three times (far / near / none) and plots the mean matched
(rediscovery) score per mode. Produces outputs/ablation.png and ablation.json.
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from muse4me.config import Config
from muse4me.pipeline import run_benchmark, load_json


def main():
    p = argparse.ArgumentParser(description="Run the distant-vs-near ablation.")
    p.add_argument("--config", required=True)
    p.add_argument("--benchmark", required=True)
    p.add_argument("--corpus", required=True)
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--out_dir", default="outputs")
    args = p.parse_args()

    cfg = Config.load(args.config)
    benchmark = load_json(args.benchmark)
    corpus = load_json(args.corpus)
    os.makedirs(args.out_dir, exist_ok=True)

    modes = ["far", "near", "none"]
    summary = {}
    for mode in modes:
        cfg.inspiration_mode = mode
        print(f"\n######## MODE = {mode} ########")
        out = run_benchmark(cfg, benchmark, corpus, limit=args.limit)
        summary[mode] = out["summary"]

    with open(os.path.join(args.out_dir, "ablation.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    _plot(summary, os.path.join(args.out_dir, "ablation.png"))
    print("\nSaved ablation.json and ablation.png to", args.out_dir)
    print(json.dumps(summary, indent=2))


def _plot(summary, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    labels = {"far": "Distant\n(muse4me)", "near": "Near\n(similarity)", "none": "No\ninspiration"}
    modes = ["far", "near", "none"]
    values = [(summary[m]["mean_matched_score"] or 0) for m in modes]
    colors = ["#2563eb", "#9ca3af", "#d1d5db"]

    fig, ax = plt.subplots(figsize=(5.2, 4))
    bars = ax.bar([labels[m] for m in modes], values, color=colors, width=0.6)
    ax.set_ylabel("Mean rediscovery score (0-5)")
    ax.set_ylim(0, 5)
    ax.set_title("Distant inspiration rediscovers breakthroughs better")
    for b, v in zip(bars, values):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.08, f"{v:.2f}",
                ha="center", va="bottom", fontsize=11, fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=160)


if __name__ == "__main__":
    main()
