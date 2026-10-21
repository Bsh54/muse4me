"""Interactive muse4me demo (marimo).

Run with:  marimo run app/muse4me_app.py
Pick a benchmark problem and an inspiration mode, hit Run, and watch muse4me
try to rediscover the real published hypothesis it was never trained on.
"""

import marimo

__generated_with = "0.9.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import json
    import os
    import sys

    repo_root = os.path.abspath(os.path.join(os.getcwd()))
    # make the package importable whether launched from repo root or /app
    for cand in (repo_root, os.path.dirname(repo_root)):
        if os.path.isdir(os.path.join(cand, "muse4me")):
            sys.path.insert(0, cand)
            repo_root = cand
            break
    return json, os, repo_root, sys


@app.cell
def _(mo):
    mo.md(
        """
        # muse4me
        ### Rediscovering recent breakthroughs via *distant* inspiration
        Pick a problem and an inspiration mode, then press **Run**.
        """
    )
    return


@app.cell
def _(json, os, repo_root):
    cfg_path = os.path.join(repo_root, "config.json")
    bench_path = os.path.join(repo_root, "data", "benchmark", "solid_state_electrolytes_2026.json")
    corpus_path = os.path.join(repo_root, "data", "benchmark", "inspiration_corpus.json")

    have_config = os.path.exists(cfg_path)
    benchmark = json.load(open(bench_path, encoding="utf-8")) if os.path.exists(bench_path) else []
    corpus = json.load(open(corpus_path, encoding="utf-8")) if os.path.exists(corpus_path) else []
    return bench_path, benchmark, cfg_path, corpus, corpus_path, have_config


@app.cell
def _(benchmark, have_config, mo):
    entry_ids = [e.get("id", f"entry {i}") for i, e in enumerate(benchmark)]
    entry_dd = mo.ui.dropdown(options=entry_ids, value=entry_ids[0] if entry_ids else None,
                              label="Problem")
    mode_dd = mo.ui.dropdown(options=["far", "near", "none"], value="far",
                             label="Inspiration mode")
    run_btn = mo.ui.run_button(label="Run muse4me")
    warn = "" if have_config else mo.md("> **Note:** no `config.json` found - add one to run live.")
    mo.vstack([mo.hstack([entry_dd, mode_dd]), run_btn, warn])
    return entry_dd, mode_dd, run_btn, warn, entry_ids


@app.cell
def _(benchmark, corpus, entry_dd, mode_dd, run_btn, cfg_path, have_config, mo):
    mo.stop(not run_btn.value, mo.md("*Press Run to start.*"))
    mo.stop(not have_config, mo.md("**Cannot run:** add a `config.json` with your API key first."))

    from muse4me.config import Config
    from muse4me.pipeline import run_entry

    cfg = Config.load(cfg_path)
    cfg.inspiration_mode = mode_dd.value
    entry = next(e for e in benchmark if e.get("id") == entry_dd.value)

    logs = []
    result = run_entry(cfg, entry, corpus, log=lambda m: logs.append(str(m)))
    return cfg, entry, result, logs


@app.cell
def _(entry, result, mo):
    top = result["hypotheses"][0]
    header = mo.md(f"## Problem\n{entry['research_question']}")
    insp = mo.md("**Distant inspirations used:** " + (", ".join(result["inspirations"]) or "(none)"))
    best = mo.md(
        f"## muse4me's best hypothesis\n{top['text']}\n\n"
        f"*self-score {top['avg_score']:.2f}/5*"
    )
    if "best_matched_score" in result:
        score = result["best_matched_score"]
        panel = result.get("judge_panel", [])
        panel_md = "\n".join(
            f"- `{p['judge'].split('/')[-1]}` → **{p['score']}/5**" for p in panel if p.get("score") is not None
        )
        verdict = mo.callout(
            mo.md(f"### Rediscovery score — independent panel median: **{score}/5**\n{panel_md}\n\n"
                  f"{result.get('best_matched_reason','')}"),
            kind="success" if score >= 3 else "warn",
        )
    else:
        verdict = mo.md("*(no ground-truth hypothesis for this entry)*")
    refs = (result.get("grounding") or {}).get("references", [])
    if refs:
        refs_md = "\n".join(f"- {(r.get('title') or '')[:90]} ({r.get('doi','')})" for r in refs)
        grounding = mo.md(f"### Literature grounding (Crossref)\n{refs_md}")
    else:
        grounding = mo.md("")
    mo.vstack([header, insp, best, verdict, grounding])
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
