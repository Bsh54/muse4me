"""Pre-flight cost estimator - runs with ZERO API calls.

Computes how many LLM calls a run would make and a rough USD estimate, so a paid
run is never launched blind. Always run this before spending.
"""

import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from muse4me.config import Config


def entry_calls(cfg, corpus_size, mode):
    n_judges = len(cfg.model_judges or [cfg.model_evaluate])
    per_insp = 1 + cfg.num_refine_iters * 2 + max(0, cfg.num_mutations - 1) * (1 + cfg.num_refine_iters * 2)
    if mode == "none":
        retrieve = 0
        gen = 1 + cfg.num_refine_iters * 2
        candidates = 1
    else:
        retrieve = cfg.retrieve_rounds * math.ceil(corpus_size / max(cfg.retrieve_window, 1))
        n_insp = min(cfg.max_inspirations, max(1, corpus_size))
        gen = n_insp * per_insp + (1 if n_insp >= 2 else 0)
        candidates = n_insp * cfg.num_mutations + (1 if n_insp >= 2 else 0)
    self_eval = candidates
    panel = n_judges
    total = retrieve + gen + self_eval + panel
    return {"retrieve": retrieve, "generate": gen, "self_eval": self_eval, "panel": panel, "total": total}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True)
    p.add_argument("--corpus_size", type=int, default=12)
    p.add_argument("--entries", type=int, default=2)
    p.add_argument("--modes", default="far,near,none")
    p.add_argument("--avg_tokens", type=int, default=1500, help="rough tokens per call (in+out)")
    p.add_argument("--price_per_m", type=float, default=0.30, help="rough blended USD per 1M tokens")
    args = p.parse_args()

    cfg = Config.load(args.config)
    modes = [m.strip() for m in args.modes.split(",") if m.strip()]
    grand = 0
    print(f"config: gen={cfg.model_generate}  judges={cfg.model_judges or [cfg.model_evaluate]}")
    print(f"params: mutations={cfg.num_mutations} refine={cfg.num_refine_iters} "
          f"rounds={cfg.retrieve_rounds} max_insp={cfg.max_inspirations} corpus={args.corpus_size}\n")
    for mode in modes:
        c = entry_calls(cfg, args.corpus_size, mode)
        per_mode = c["total"] * args.entries
        grand += per_mode
        print(f"  mode={mode:4s}  calls/entry={c['total']:3d}  x{args.entries} entries = {per_mode}   {c}")
    tokens = grand * args.avg_tokens
    usd = tokens / 1_000_000 * args.price_per_m
    print(f"\nTOTAL LLM calls: {grand}")
    print(f"~tokens: {tokens:,}  ~cost: ${usd:.3f}  (at {args.avg_tokens} tok/call, ${args.price_per_m}/1M)")


if __name__ == "__main__":
    main()
