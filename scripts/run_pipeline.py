"""Run muse4me end-to-end over a benchmark file.

Example:
    python scripts/run_pipeline.py --config config.json \
        --benchmark data/benchmark/solid_state_electrolytes_2026.json \
        --corpus data/benchmark/inspiration_corpus.json --limit 1
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from muse4me.config import Config
from muse4me.pipeline import run_benchmark, load_json


def main():
    p = argparse.ArgumentParser(description="Run the muse4me pipeline.")
    p.add_argument("--config", required=True)
    p.add_argument("--benchmark", required=True)
    p.add_argument("--corpus", required=True)
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--mode", choices=["far", "near", "none"], default=None,
                   help="override inspiration_mode from the config")
    p.add_argument("--out", default="outputs/run.json")
    args = p.parse_args()

    cfg = Config.load(args.config)
    if args.mode:
        cfg.inspiration_mode = args.mode

    benchmark = load_json(args.benchmark)
    corpus = load_json(args.corpus)

    out = run_benchmark(cfg, benchmark, corpus, limit=args.limit)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print("\n==== SUMMARY ====")
    print(json.dumps(out["summary"], indent=2))
    print(f"\nSaved full results to {args.out}")


if __name__ == "__main__":
    main()
