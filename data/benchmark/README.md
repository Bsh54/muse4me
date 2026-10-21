# muse4me benchmark

A **post-cutoff** rediscovery benchmark: each entry is a real scientific
breakthrough published *after* the evaluated model's training cutoff, so a high
match is a genuine rediscovery rather than recall.

## Entry schema

```json
{
  "id": "sse-0001",
  "domain": "solid-state electrolytes",
  "status": "real",                     // "real" or "example"
  "source": {
    "title": "<paper title>",
    "venue": "<journal>",
    "year": 2026,
    "pub_date": "2026-07-01",
    "url": "<link to the paper>"
  },
  "research_question": "<the problem, with NO leakage of the answer>",
  "background_survey": "<prior state of the art, NO leakage of the hypothesis or its inspirations>",
  "ground_truth_hypothesis": "<the real published hypothesis>",
  "keypoints": "<the key innovations used to score a match>",
  "ground_truth_inspirations": ["<distant field / paper that inspired it>"]
}
```

## Integrity rules

1. **No leakage.** `research_question` and `background_survey` must not reveal the
   hypothesis, its mechanism, or its named inspirations.
2. **Real provenance.** Every `status: "real"` entry must link to a real paper
   (`source.url`) published after the model cutoff. Verify the date.
3. **Examples are not results.** Entries marked `status: "example"` exist only so
   the pipeline runs end-to-end as a demo. They are **not** real papers and must
   never be reported as rediscovery results.

Validate a file with:

```bash
python scripts/build_benchmark.py --benchmark data/benchmark/solid_state_electrolytes_2026.json
```

## Inspiration corpus

`inspiration_corpus.json` is a pool of papers (title + abstract) the retrieval
stage searches for *distant* inspiration. The seed shipped here is illustrative;
expand it with real abstracts (e.g. exported from a literature service) for
real runs.
