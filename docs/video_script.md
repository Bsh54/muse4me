# muse4me — 4-minute video script

Goal: show, live, that an AI rediscovers a real breakthrough it never saw — and that we can *prove* it never saw it. Keep it fast, concrete, honest.

---

## 0:00–0:30 — The hook
> "In 2026, every lab claims their AI makes discoveries. But two things are almost never checked: did the model just *remember* the paper, and who *verified* the result? We built muse4me to settle both."

On screen: title card, then the one-line pitch.

## 0:30–1:10 — The idea (distant inspiration)
> "Great discoveries come from far away — Kekulé dreamed of a snake to crack benzene. muse4me gives an AI only the *problem*, then makes it borrow ideas from deliberately *distant* fields."

On screen: the problem card for the **LLNOF** case (how can an oxide conduct lithium as fast as a sulfide?). No answer shown.

## 1:10–1:50 — Proof it doesn't already know (leakage control)
> "First, the integrity check. We ask the model, from memory alone: do you know the answer?"

On screen: run `leakage_check` live → `recalled: NO KNOWN RESULT` / low match. 
> "It doesn't. So whatever it finds next is a real rediscovery — not recall. Our filter even caught a June paper it *had* memorised, and we threw it out."

## 1:50–2:50 — The rediscovery (the money shot)
> "Now we let muse4me run."

On screen: marimo app — pick the LLNOF problem, mode = *distant*, press Run. Show the distant inspirations it chose (e.g. counter-motion / doorway gating). Then the generated hypothesis appears.
> "It proposes that the framework *gets out of the way* as lithium hops — a cooperative counter-motion that lowers the barrier."

Cut to the real paper's hypothesis side by side (fluoride relaxation). 
> "Here's the real JACS 2026 result. Independent judge — a different model family — scores the match: **{BEST_SCORE}/5.** It rediscovered the core idea it had never read."

## 2:50–3:30 — The ablation (why distant matters)
On screen: Figure 1 bar chart.
> "Is the 'distant' trick real? We ran the ablation: distant inspiration beats near-neighbour retrieval and beats no inspiration. Far-field is what drives rediscovery."

## 3:30–4:00 — Close (impact + integrity)
> "muse4me turns 'AI discovers' into something you can measure: leakage-controlled, independently verified, reproducible for a few cents. Same protocol, any science — just change one line. That's the point: not an AI that talks, an AI whose discoveries you can check."

On screen: repo URL, "leakage-controlled · independently verified · reproducible".

---

### Shot list / assets
- Problem cards (LLNOF, mussel composite) — no answers.
- Terminal: `leakage_check.py` live.
- marimo app: run + result + side-by-side with real hypothesis.
- `outputs/ablation.png`.
- Repo URL end card.
