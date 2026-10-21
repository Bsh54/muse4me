"""End-to-end orchestration: retrieve -> evolve -> evaluate.

Also provides a benchmark runner that aggregates the rediscovery rate and
supports the distant-vs-near inspiration ablation.
"""

import json

from .config import Config
from .llm import LLMClient
from .retrieve import retrieve_inspirations
from .evolve import evolve
from .evaluate import score_candidates, build_judges, panel_matched_score
from .grounding import ground_hypothesis


def _clients(cfg: Config):
    c_ret = LLMClient(cfg.provider, cfg.api_key, cfg.base_url, cfg.model_retrieve)
    c_gen = LLMClient(cfg.provider, cfg.api_key, cfg.base_url, cfg.model_generate)
    c_eval = LLMClient(cfg.provider, cfg.api_key, cfg.base_url, cfg.model_evaluate)
    return c_ret, c_gen, c_eval


def run_entry(cfg: Config, entry: dict, corpus: list, clients=None, log=print):
    """Run the full pipeline on one benchmark entry.

    Returns a result dict with the ranked hypotheses and, when the entry has a
    ground-truth hypothesis, the best rediscovery (matched) score.
    """
    c_ret, c_gen, c_eval = clients or _clients(cfg)
    rq = entry["research_question"]
    bg = entry.get("background_survey", "")

    log(f"[retrieve] mode={cfg.inspiration_mode} corpus={len(corpus)}")
    inspirations = retrieve_inspirations(c_ret, cfg, rq, bg, corpus)
    log(f"[retrieve] kept {len(inspirations)} inspirations")

    candidates = evolve(c_gen, cfg, rq, bg, inspirations, log=log)
    log(f"[evolve] produced {len(candidates)} candidate hypotheses")

    ranked = score_candidates(c_eval, cfg, candidates)

    result = {
        "id": entry.get("id"),
        "inspiration_mode": cfg.inspiration_mode,
        "inspirations": [i["title"] for i in inspirations],
        "hypotheses": ranked,
    }

    gt = entry.get("ground_truth_hypothesis")
    if gt:
        keypoints = entry.get("keypoints", "")
        best = ranked[0]
        judges = build_judges(cfg)
        agg, per = panel_matched_score(judges, cfg, best["text"], gt, keypoints)
        result["best_matched_score"] = agg
        result["judge_panel"] = per
        result["best_matched_reason"] = next(
            (p["reason"] for p in per if p["score"] == agg), per[0]["reason"] if per else "")
        log(f"[evaluate] panel matched score = {agg}/5  judges={[p['score'] for p in per]}")

    # literature grounding of the top hypothesis (best-effort, never fatal)
    try:
        result["grounding"] = ground_hypothesis(ranked[0]["text"])
    except Exception:  # noqa: BLE001
        result["grounding"] = {"grounded": False, "references": []}
    return result


def run_benchmark(cfg: Config, benchmark: list, corpus: list, limit=None, log=print):
    """Run over a benchmark and aggregate rediscovery metrics."""
    clients = _clients(cfg)
    # leaked entries are excluded from rediscovery scoring (the model already knows them)
    usable = [e for e in benchmark if not e.get("leaked")]
    entries = usable if limit is None else usable[:limit]
    results, matched = [], []
    for i, entry in enumerate(entries):
        log(f"\n=== entry {i + 1}/{len(entries)} : {entry.get('id')} ===")
        res = run_entry(cfg, entry, corpus, clients=clients, log=log)
        results.append(res)
        if "best_matched_score" in res:
            matched.append(res["best_matched_score"])
    summary = {
        "n": len(results),
        "inspiration_mode": cfg.inspiration_mode,
        "mean_matched_score": (sum(matched) / len(matched)) if matched else None,
        "rediscovery_rate@3": (sum(1 for m in matched if m >= 3) / len(matched)) if matched else None,
    }
    return {"summary": summary, "results": results}


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
