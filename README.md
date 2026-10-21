# muse4me

**An LLM agent that rediscovers recent scientific breakthroughs it was never trained on — by drawing distant, cross-domain inspiration.**

muse4me takes only the *context* of a research problem (a research question and a background survey of prior work) and tries to propose the key hypothesis behind a real, recently published breakthrough — a breakthrough the model could not have memorised because it appeared *after* the model's training cutoff.

The core bet: great hypotheses come from **distant** inspiration (ideas borrowed from unrelated fields), not from near-neighbour retrieval. muse4me makes that mechanism explicit and measurable.

---

## Why this is different

Most "AI scientist" systems either (a) generate hypotheses that sound novel but collapse under scrutiny, or (b) grade themselves with an LLM judge, proving nothing. muse4me is built around three ideas instead:

1. **Post-cutoff benchmark.** We evaluate only on breakthroughs published *after* the model's training cutoff, so a match is a genuine rediscovery, not recall. Ground truth is the real published paper.
2. **Distant-inspiration engine.** Hypotheses evolve from inspirations deliberately chosen for *potential*, not semantic similarity. A single switch lets us run an ablation: distant vs. near vs. none.
3. **Grounded evaluation.** A rediscovery score compares each generated hypothesis to the real published hypothesis against annotated key points, with optional literature grounding.

## Method (three stages)

1. **Retrieve** — screen an inspiration corpus and keep the most promising papers for the research question (near/far mode).
2. **Evolve** — combine the problem with each inspiration into a hypothesis, then self-refine, mutate, and recombine (an island-style evolutionary loop).
3. **Evaluate** — self-score each hypothesis on four axes, rank them, and compute a rediscovery score against ground truth.

## Target domain

Materials for energy — **solid-state electrolytes / all-solid-state batteries** — a field rich in recent, clearly structured breakthroughs. The domain is a single config value and can be changed.

---

## Quick start

```bash
pip install -r requirements.txt
cp config.example.json config.json   # then fill in your API key
python scripts/run_pipeline.py --config config.json --benchmark data/benchmark/solid_state_electrolytes_2026.json --limit 1
```

Run the interactive demo:

```bash
marimo run app/muse4me_app.py
```

## Layout

```
muse4me/            core package (retrieve / evolve / evaluate / pipeline)
data/benchmark/     the post-cutoff benchmark + inspiration corpus
scripts/            command-line entry points
app/                interactive demo (marimo)
```

## Configuration

Copy `config.example.json` to `config.json` and set your provider, API key, base URL and model names. Any OpenAI-compatible endpoint works via `base_url`; Gemini is supported with `"provider": "gemini"`.

## License

MIT. See [LICENSE](./LICENSE).
