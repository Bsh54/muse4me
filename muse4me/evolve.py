"""Stage 2 - evolutionary hypothesis generation.

For each inspiration we:
  1. generate an initial hypothesis,
  2. self-refine it with reviewer feedback (a few iterations),
  3. spawn distinct mutations.
Then we recombine the best hypotheses across different inspirations.
Each surviving hypothesis is scored by self-evaluation (done in evaluate.py).
"""

from . import prompts
from .llm import extract_field


def _gen(client, cfg, prompt):
    raw = client.generate(prompt, temperature=cfg.temperature)
    field = "Refined Hypothesis" if "Refined Hypothesis:" in raw else "Hypothesis"
    return extract_field(raw, field)


def generate_initial(client, cfg, rq, bg, inspiration):
    return _gen(client, cfg, prompts.hypothesis_initial_prompt(cfg.domain, rq, bg, inspiration))


def self_refine(client, cfg, rq, bg, inspiration, hypothesis):
    current = hypothesis
    for _ in range(max(0, cfg.num_refine_iters)):
        fb_raw = client.generate(prompts.feedback_prompt(cfg.domain, current),
                                  temperature=cfg.temperature)
        feedback = extract_field(fb_raw, "Feedback")
        current = _gen(client, cfg,
                       prompts.refine_prompt(cfg.domain, rq, bg, inspiration, current, feedback))
    return current


def mutate(client, cfg, rq, bg, inspiration, prev_hyps):
    raw = client.generate(
        prompts.hypothesis_mutation_prompt(cfg.domain, rq, bg, inspiration, prev_hyps),
        temperature=cfg.temperature,
    )
    return extract_field(raw, "Hypothesis")


def recombine(client, cfg, rq, bg, hyp_a, hyp_b):
    raw = client.generate(prompts.recombine_prompt(cfg.domain, rq, bg, hyp_a, hyp_b),
                          temperature=cfg.temperature)
    return extract_field(raw, "Hypothesis")


def evolve(client, cfg, rq, bg, inspirations, log=print):
    """Return a list of candidate hypotheses (dicts with text + provenance).

    When no inspirations are given (ablation "none"), a single hypothesis is
    generated directly from the background with no inspiration.
    """
    candidates = []

    if not inspirations:
        log("  [evolve] no inspiration (baseline)")
        base_prompt = prompts.hypothesis_initial_prompt(
            cfg.domain, rq, bg,
            {"title": "(none)", "abstract": "No inspiration provided; reason from first principles."},
        )
        hyp = self_refine(client, cfg, rq, bg,
                          {"title": "(none)", "abstract": ""}, _gen(client, cfg, base_prompt))
        candidates.append({"text": hyp, "inspiration": None, "origin": "baseline"})
        return candidates

    best_per_insp = []
    for idx, insp in enumerate(inspirations):
        log(f"  [evolve] inspiration {idx + 1}/{len(inspirations)}: {insp['title'][:60]}")
        line_hyps = []
        hyp = generate_initial(client, cfg, rq, bg, insp)
        hyp = self_refine(client, cfg, rq, bg, insp, hyp)
        line_hyps.append(hyp)
        candidates.append({"text": hyp, "inspiration": insp["title"], "origin": "refined"})
        for _ in range(max(0, cfg.num_mutations - 1)):
            mut = mutate(client, cfg, rq, bg, insp, line_hyps)
            mut = self_refine(client, cfg, rq, bg, insp, mut)
            line_hyps.append(mut)
            candidates.append({"text": mut, "inspiration": insp["title"], "origin": "mutation"})
        best_per_insp.append(line_hyps[0])

    # cross-inspiration recombination of the two leading lines
    if len(best_per_insp) >= 2:
        log("  [evolve] recombining across inspirations")
        combo = recombine(client, cfg, rq, bg, best_per_insp[0], best_per_insp[1])
        candidates.append({"text": combo, "inspiration": "recombination", "origin": "recombination"})

    return candidates
