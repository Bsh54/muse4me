"""Prompt templates for muse4me.

Every prompt asks the model to answer with explicit "Label:" markers so the
output can be parsed deterministically (see llm.extract_field / extract_scores).
All prompts are parameterised by `domain` so the engine is domain-agnostic.
"""


def screening_prompt(domain, mode, research_question, background, candidates_block):
    if mode == "near":
        criterion = (
            "Select the papers that are the most SEMANTICALLY SIMILAR to the research "
            "question (closest topic, same sub-field)."
        )
    else:  # "far"
        criterion = (
            "Select the papers with the highest POTENTIAL TO INSPIRE a novel hypothesis, "
            "even if they come from a DISTANT or seemingly unrelated field. Do not reward "
            "mere topical similarity; reward transferable mechanisms, analogies and principles."
        )
    return (
        f"You are helping a researcher in {domain}.\n"
        f"Research question:\n{research_question}\n\n"
        f"Background (state of the art):\n{background}\n\n"
        f"Below are candidate inspiration papers (title + abstract):\n{candidates_block}\n\n"
        f"{criterion}\n"
        f"Choose the 3 best candidates. For each, answer on its own block exactly as:\n"
        f"Title: <exact title of the chosen paper>\n"
        f"Reason: <one sentence on why it can inspire a hypothesis>\n"
    )


def hypothesis_initial_prompt(domain, research_question, background, inspiration):
    return (
        f"You are a creative researcher in {domain}.\n"
        f"Research question:\n{research_question}\n\n"
        f"Background (state of the art):\n{background}\n\n"
        f"Inspiration paper:\nTitle: {inspiration['title']}\nAbstract: {inspiration['abstract']}\n\n"
        f"Propose ONE specific, testable scientific hypothesis that answers the research "
        f"question by transferring an idea from the inspiration. Be concrete about the "
        f"mechanism, materials and conditions.\n\n"
        f"Answer exactly as:\n"
        f"Hypothesis: <the hypothesis>\n"
        f"Key Reasoning: <one or two sentences on the core logic>\n"
    )


def hypothesis_mutation_prompt(domain, research_question, background, inspiration, prev_hyps):
    prev_block = "\n".join(f"- {h}" for h in prev_hyps)
    return (
        f"You are a creative researcher in {domain}.\n"
        f"Research question:\n{research_question}\n\n"
        f"Background:\n{background}\n\n"
        f"Inspiration paper:\nTitle: {inspiration['title']}\nAbstract: {inspiration['abstract']}\n\n"
        f"You have already proposed these hypotheses, which you must AVOID repeating:\n{prev_block}\n\n"
        f"Propose a DIFFERENT specific, testable hypothesis that explores a distinct mechanism.\n\n"
        f"Answer exactly as:\n"
        f"Hypothesis: <the hypothesis>\n"
        f"Key Reasoning: <one or two sentences>\n"
    )


def feedback_prompt(domain, hypothesis):
    return (
        f"You are a rigorous reviewer in {domain}. Critique the following hypothesis on four "
        f"axes: validity (is it physically sound?), novelty (is it non-obvious?), significance "
        f"(would it matter?), and clarity (is it specific and testable?). Give concrete, "
        f"actionable suggestions to improve it.\n\n"
        f"Hypothesis: {hypothesis}\n\n"
        f"Answer exactly as:\n"
        f"Feedback: <your critique and suggestions>\n"
    )


def refine_prompt(domain, research_question, background, inspiration, hypothesis, feedback):
    return (
        f"You are a researcher in {domain} improving your own hypothesis using reviewer feedback.\n"
        f"Research question:\n{research_question}\n\n"
        f"Background:\n{background}\n\n"
        f"Inspiration:\nTitle: {inspiration['title']}\nAbstract: {inspiration['abstract']}\n\n"
        f"Current hypothesis: {hypothesis}\n\n"
        f"Reviewer feedback: {feedback}\n\n"
        f"Produce an improved hypothesis that keeps what is strong and fixes the weaknesses. "
        f"Stay specific and testable; do not add unsupported detail.\n\n"
        f"Answer exactly as:\n"
        f"Refined Hypothesis: <the improved hypothesis>\n"
        f"Key Reasoning: <one or two sentences>\n"
    )


def recombine_prompt(domain, research_question, background, hyp_a, hyp_b):
    return (
        f"You are a researcher in {domain}. Two promising hypotheses were developed from "
        f"different inspirations. Combine their strongest, compatible ideas into a single, "
        f"coherent, testable hypothesis (do not just concatenate them).\n\n"
        f"Research question:\n{research_question}\n\n"
        f"Background:\n{background}\n\n"
        f"Hypothesis A: {hyp_a}\n"
        f"Hypothesis B: {hyp_b}\n\n"
        f"Answer exactly as:\n"
        f"Hypothesis: <the combined hypothesis>\n"
        f"Key Reasoning: <one or two sentences>\n"
    )


def self_eval_prompt(domain, hypothesis):
    return (
        f"You are an expert panel in {domain}. Score the hypothesis from 1 (poor) to 5 "
        f"(excellent) on four axes. Be strict.\n\n"
        f"Hypothesis: {hypothesis}\n\n"
        f"Answer exactly as:\n"
        f"Score 1 (validity): <1-5>\n"
        f"Score 2 (novelty): <1-5>\n"
        f"Score 3 (significance): <1-5>\n"
        f"Score 4 (clarity): <1-5>\n"
    )


def matched_score_prompt(domain, generated_hypothesis, ground_truth_hypothesis, keypoints):
    return (
        f"You are an impartial judge in {domain}. Compare a GENERATED hypothesis to the real "
        f"GROUND-TRUTH hypothesis of a published breakthrough. Judge how many of the ground-truth "
        f"key points the generated hypothesis captures. Use this scale:\n"
        f"0 = unrelated; 1 = same general area; 2 = captures one key point; 3 = captures several; "
        f"4 = captures most key points; 5 = captures essentially all key innovations.\n\n"
        f"Ground-truth key points: {keypoints}\n\n"
        f"Ground-truth hypothesis: {ground_truth_hypothesis}\n\n"
        f"Generated hypothesis: {generated_hypothesis}\n\n"
        f"Answer exactly as:\n"
        f"Matched score: <0-5>\n"
        f"Reason: <one sentence on which key points matched>\n"
    )
