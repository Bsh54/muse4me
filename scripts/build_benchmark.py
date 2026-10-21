"""Validate a muse4me benchmark file and report its status.

Also usable as a module to append new, real post-cutoff entries. A valid entry
must carry real paper provenance before its results are reported as rediscovery.
"""

import argparse
import json
import os
import sys

REQUIRED = ["id", "research_question", "background_survey",
            "ground_truth_hypothesis", "keypoints"]


def validate_entry(entry):
    problems = []
    for k in REQUIRED:
        if not entry.get(k):
            problems.append(f"missing/empty '{k}'")
    src = entry.get("source") or {}
    if entry.get("status") == "real" and not src.get("url"):
        problems.append("status=real but no source.url (provenance required)")
    return problems


def validate_file(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"{len(data)} entries in {path}")
    n_real, n_example = 0, 0
    for e in data:
        status = e.get("status", "unknown")
        n_real += status == "real"
        n_example += status == "example"
        problems = validate_entry(e)
        flag = "OK" if not problems else "ISSUES"
        print(f"  [{flag}] {e.get('id')} (status={status})"
              + ("" if not problems else "  -> " + "; ".join(problems)))
    print(f"\nreal={n_real}  example={n_example}")
    if n_real == 0:
        print("WARNING: no real post-cutoff entries yet - add them before reporting results.")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--benchmark", required=True)
    args = p.parse_args()
    validate_file(args.benchmark)
