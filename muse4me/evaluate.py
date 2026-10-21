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
        scores, avg = self_evaluate(client, cfg, c["text"])
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
