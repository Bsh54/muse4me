"""Stage 3 - self-evaluation, ranking, and rediscovery scoring.

Two kinds of scores:
  - self scores (validity/novelty/significance/clarity): used to RANK candidates.
  - matched score (0-5): compares a candidate to the real published hypothesis.
    This is the rediscovery metric and is only available for benchmark entries
    that carry a ground-truth hypothesis.
"""

from . import prompts
from .llm import extract_field, extract_scores


def self_evaluate(client, cfg, hypothesis):
    raw = client.generate(prompts.self_eval_prompt(cfg.domain, hypothesis), temperature=0.0)
    scores = extract_scores(raw, n=4)
    return scores, sum(scores) / len(scores)


def score_candidates(client, cfg, candidates):
    """Attach self-eval scores to each candidate and return them ranked (desc)."""
    for c in candidates:
        try:
            scores, avg = self_evaluate(client, cfg, c["text"])
        except Exception:  # noqa: BLE001 - a failed self-eval defaults to neutral, never aborts ranking
            scores, avg = [3, 3, 3, 3], 3.0
        c["scores"] = scores
        c["avg_score"] = avg
    return sorted(candidates, key=lambda c: c["avg_score"], reverse=True)


def matched_score(client, cfg, generated_hypothesis, ground_truth_hypothesis, keypoints):
    raw = client.generate(
        prompts.matched_score_prompt(cfg.domain, generated_hypothesis,
                                     ground_truth_hypothesis, keypoints),
        temperature=0.0,
    )
    scores = extract_scores(raw, n=1)
    reason = extract_field(raw, "Reason")
    return scores[0] if scores else 0, reason


def build_judges(cfg):
    """Instantiate the independent judge panel (falls back to model_evaluate)."""
    from .llm import LLMClient
    names = cfg.model_judges or [cfg.model_evaluate]
    return [(n, LLMClient(cfg.provider, cfg.api_key, cfg.base_url, n)) for n in names]


def panel_matched_score(judges, cfg, generated_hypothesis, ground_truth_hypothesis, keypoints):
    """Score rediscovery with a panel of independent judges; aggregate by median.

    Returns (median_score, per_judge) where per_judge is a list of
    {judge, score, reason}. The median resists a single lenient or harsh judge.
    """
    import statistics
    per = []
    for name, jc in judges:
        try:
            s, reason = matched_score(jc, cfg, generated_hypothesis, ground_truth_hypothesis, keypoints)
        except Exception as e:  # noqa: BLE001 - a flaky judge must not sink the panel
            s, reason = None, f"judge error: {e}"
        per.append({"judge": name, "score": s, "reason": reason})
    scores = [p["score"] for p in per if isinstance(p["score"], int)]
    agg = int(round(statistics.median(scores))) if scores else 0
    return agg, per
