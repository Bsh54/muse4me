"""Leakage / post-cutoff control.

The whole premise of muse4me is that the model never saw the breakthrough. This
module checks that directly: it asks the GENERATION model to recall, from its
training knowledge alone (no inspiration corpus), any published result that
answers the problem. An INDEPENDENT judge then matches that recall against the
ground-truth hypothesis. A high recall match means the paper is likely in the
model's training data -> the entry is leaked and must be dropped or flagged.
"""

from .llm import extract_field
from .evaluate import panel_matched_score

LEAK_THRESHOLD = 3  # recall match >= this means the model already knows the answer


def _recall_prompt(domain, research_question, background):
    return (
        f"You are an expert in {domain}. Using ONLY your own training knowledge, and "
        f"without inventing anything, consider this research problem:\n\n"
        f"Research question: {research_question}\n\n"
        f"Background: {background}\n\n"
        f"Do you specifically recall a published study that reports the key result or "
        f"hypothesis answering this exact problem? If yes, state that paper's main "
        f"hypothesis as precisely as you can, and name it if you can. If you do not "
        f"specifically recall one, answer exactly 'NO KNOWN RESULT'.\n\n"
        f"Answer exactly as:\n"
        f"Recall: <the recalled hypothesis, or NO KNOWN RESULT>\n"
    )


def recall(gen_client, cfg, entry):
    raw = gen_client.generate(
        _recall_prompt(cfg.domain, entry["research_question"], entry.get("background_survey", "")),
        temperature=0.0,
    )
    return extract_field(raw, "Recall")


def leakage_check(gen_client, judges, cfg, entry):
    """Return a leakage report for one entry, judged by an independent panel."""
    recalled = recall(gen_client, cfg, entry)
    knows_claim = "NO KNOWN RESULT" not in recalled.upper()
    if knows_claim:
        score, per = panel_matched_score(judges, cfg, recalled,
                                         entry["ground_truth_hypothesis"], entry.get("keypoints", ""))
        reason = "; ".join(f"{p['judge'].split('/')[-1]}:{p['score']}" for p in per)
    else:
        score, per, reason = 0, [], "model reports no known result"
    return {
        "id": entry.get("id"),
        "knows_claim": knows_claim,
        "recall_matched": score,
        "leaked": score >= LEAK_THRESHOLD,
        "recalled": recalled,
        "judge_panel": per,
        "reason": reason,
    }
