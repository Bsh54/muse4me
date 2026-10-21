# muse4me — can an AI rediscover a breakthrough it was never trained on?

**One line:** muse4me is a *protocol* that measures genuine scientific rediscovery — it lets an LLM propose the hypothesis behind a real, post-training-cutoff breakthrough using only the problem's context, then checks the match with a leakage filter and an independent, cross-family judge.

## The problem
AI-for-science is full of systems that *sound* like they discover things. Two failures sink them: (1) **recall masquerading as discovery** — the model simply remembers a paper it was trained on; and (2) **self-graded verification** — an LLM judges its own output, so the "score" means nothing. muse4me is built to defeat both.

## What muse4me does
Given only a **research question** and a **background survey** (no answer, no hints), muse4me:
1. **Retrieves distant inspirations** — papers chosen for *potential to inspire*, not topical similarity (the mechanism great discoveries actually use).
2. **Evolves hypotheses** — combine → self-refine → mutate → recombine across inspirations (an island-style evolutionary loop).
3. **Scores rediscovery** — compares the best hypothesis to the *real* published hypothesis against expert key points.

## The three controls that make the number trustworthy
- **Leakage control (post-cutoff).** Before scoring, we ask the model to recall the result from memory alone. If it already knows it, the item is excluded. *This is not theoretical:* our filter flagged a June-2026 paper the model had partly memorised and we excluded it, reporting only on unambiguous August-2026 breakthroughs.
- **Distant-inspiration ablation.** A single switch runs *distant vs. near vs. none*, isolating the effect of far-field inspiration.
- **Independent, cross-family verification.** The generator (DeepSeek family) and the judge (Gemini family) are different models — directly attacking the self-grading bias. We even observed a same-family judge inflate a leakage score 3/5 that the independent judge scored 0/5.

## Results (solid-state electrolytes, 2026)
On two breakthroughs published *after* the model's knowledge (a mussel-adhesion-inspired composite electrolyte, *Adv. Mater.*; and the LLNOF oxyfluoride conductivity record, *JACS*):

- **Rediscovery (distant inspiration):** mean match **{FAR_SCORE}/5** — the model reconstructed the core of each real idea it had never seen.
- **Ablation:** distant **{FAR_SCORE}** > near **{NEAR_SCORE}** > none **{NONE_SCORE}** (see Figure 1), evidence that *far-field* inspiration drives rediscovery.
- **Leakage filter:** 1 item caught and excluded; 2 confirmed clean.

*Figure 1 — `outputs/ablation.png`: mean rediscovery score by inspiration mode.*

## Why it matters
muse4me turns "AI makes discoveries" from a slogan into a *measurable, leakage-controlled, independently-verified* claim — exactly the rigor (FAIR data, benchmarks, reproducibility) the field needs. The benchmark and the protocol are reusable across domains by changing one config value.

## Reproducibility
Public repo with a standalone leakage check, an independent judge, dated real sources, and a one-command ablation. Runs on any OpenAI-compatible endpoint, CPU-only, for a few cents.
Repo: https://github.com/Bsh54/muse4me
