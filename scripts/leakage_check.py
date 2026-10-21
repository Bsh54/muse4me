"""Run the leakage / post-cutoff control over the benchmark.

The generation model is probed for prior knowledge; an independent judge
(model_evaluate) scores the recall against ground truth. Entries that the model
already knows (recall match >= threshold) are flagged as leaked.
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from muse4me.config import Config
from muse4me.llm import LLMClient
from muse4me.evaluate import build_judges
from muse4me.leakage import leakage_check
from muse4me.pipeline import load_json


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True)
    p.add_argument("--benchmark", required=True)
    p.add_argument("--only_real", action="store_true", help="check only status=real entries")
    p.add_argument("--out", default="outputs/leakage.json")
    args = p.parse_args()

    cfg = Config.load(args.config)
    gen = LLMClient(cfg.provider, cfg.api_key, cfg.base_url, cfg.model_generate)
    judges = build_judges(cfg)

    benchmark = load_json(args.benchmark)
    if args.only_real:
        benchmark = [e for e in benchmark if e.get("status") == "real"]

    reports = []
    for e in benchmark:
        r = leakage_check(gen, judges, cfg, e)
        reports.append(r)
        flag = "LEAKED" if r["leaked"] else ("knows?" if r["knows_claim"] else "clean")
        print(f"[{flag}] {r['id']}: recall_match={r['recall_matched']}/5")

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(reports, f, indent=2, ensure_ascii=False)

    n_leaked = sum(1 for r in reports if r["leaked"])
    print(f"\n{n_leaked}/{len(reports)} entries flagged as leaked. "
          f"Generation model = {cfg.model_generate}; judge panel = {cfg.model_judges or [cfg.model_evaluate]}")
    print(f"Saved to {args.out}")


if __name__ == "__main__":
    main()
