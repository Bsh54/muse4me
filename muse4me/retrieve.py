"""Stage 1 - inspiration retrieval.

Screens an inspiration corpus with a sliding window and keeps the most promising
papers for the research question. The `mode` controls the selection criterion:
  - "far"  : potential to inspire (distant, cross-domain)  [default]
  - "near" : semantic similarity to the research question
  - "none" : skip retrieval entirely (ablation baseline)
"""

from .prompts import screening_prompt
from .llm import extract_field


def _candidates_block(candidates):
    lines = []
    for i, c in enumerate(candidates):
        lines.append(f"[{i}] Title: {c['title']}\nAbstract: {c['abstract']}")
    return "\n\n".join(lines)


def _match_title(title, corpus):
    """Map a model-written title back to the exact corpus entry (best effort)."""
    title_l = title.strip().lower()
    for c in corpus:
        if c["title"].strip().lower() == title_l:
            return c
    # loose containment match
    for c in corpus:
        ct = c["title"].strip().lower()
        if ct and (ct in title_l or title_l in ct):
            return c
    return None


def one_round(client, cfg, research_question, background, candidates):
    """Run one screening pass over the candidates, keeping the best ones."""
    kept = []
    window = max(cfg.retrieve_window, cfg.retrieve_keep + 1)
    start = 0
    while start < len(candidates):
        chunk = candidates[start:start + window]
        start += window
        if len(chunk) <= cfg.retrieve_keep:
            kept.extend(chunk)
            continue
        block = _candidates_block(chunk)
        prompt = screening_prompt(cfg.domain, cfg.inspiration_mode,
                                  research_question, background, block)
        raw = client.generate(prompt, temperature=0.0)
        # parse repeated "Title:" markers
        for part in raw.split("Title:")[1:]:
            title = part.split("\n")[0].strip()
            match = _match_title(title, chunk)
            if match and match not in kept:
                reason = ""
                if "Reason:" in part:
                    reason = extract_field("Reason:" + part.split("Reason:", 1)[1], "Reason")
                entry = dict(match)
                entry["reason"] = reason
                kept.append(entry)
    return kept


def retrieve_inspirations(client, cfg, research_question, background, corpus):
    """Return a short ranked list of inspiration papers for the research question."""
    if cfg.inspiration_mode == "none":
        return []
    candidates = list(corpus)
    rounds = max(1, cfg.retrieve_rounds)
    for _ in range(rounds):
        candidates = one_round(client, cfg, research_question, background, candidates)
        if len(candidates) <= cfg.retrieve_keep:
            break
    return candidates
