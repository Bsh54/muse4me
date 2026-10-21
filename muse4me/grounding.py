"""Literature grounding.

Checks whether a hypothesis's claims are echoed in the research literature, so a
generated hypothesis is not just plausible prose but traceable to real work.

Two backends:
  - `crossref_backend` (default): self-contained, no API key, queries Crossref.
  - an MCP literature tool (e.g. Valency / MCP Bond) if one is supplied.

Grounding is optional and degrades gracefully: any failure returns an empty,
clearly-marked result so the pipeline never depends on an external service.
"""

import json
import re
import urllib.parse
import urllib.request

_STOPWORDS = {
    "the", "a", "an", "of", "for", "and", "or", "to", "in", "on", "with", "by",
    "that", "this", "is", "are", "be", "as", "at", "from", "it", "its", "will",
    "can", "not", "into", "than", "such", "these", "their", "which", "while",
}


def _keyphrase(text, max_words=12):
    """Build a compact search query from the most informative words of a hypothesis."""
    words = re.findall(r"[A-Za-z][A-Za-z\-]+", text or "")
    kept = [w for w in words if w.lower() not in _STOPWORDS and len(w) > 3]
    return " ".join(kept[:max_words]) if kept else (text or "")[:120]


def crossref_backend(query, k=3, mailto="muse4me@example.org"):
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode(
        {"query": query, "rows": k, "select": "title,DOI,issued,container-title", "mailto": mailto}
    )
    req = urllib.request.Request(url, headers={"User-Agent": "muse4me/0.1 (research prototype)"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.load(r)
    refs = []
    for it in data.get("message", {}).get("items", []):
        year = ""
        try:
            year = it.get("issued", {}).get("date-parts", [[None]])[0][0] or ""
        except Exception:  # noqa: BLE001
            pass
        refs.append({
            "title": (it.get("title") or [""])[0],
            "doi": it.get("DOI", ""),
            "venue": (it.get("container-title") or [""])[0],
            "year": year,
        })
    return refs


def ground_hypothesis(hypothesis, backend=crossref_backend, mcp_tool=None, max_refs=3, query=None):
    """Return a grounding report: supporting references for a hypothesis.

    If `mcp_tool` is given it takes precedence (e.g. a Valency / MCP Bond client);
    otherwise the default Crossref backend is used.
    """
    q = query or _keyphrase(hypothesis)
    try:
        refs = mcp_tool(q, max_refs) if mcp_tool is not None else backend(q, max_refs)
    except Exception as e:  # noqa: BLE001
        return {"grounded": False, "query": q, "references": [], "note": f"backend error: {e}"}
    return {"grounded": bool(refs), "query": q, "references": refs or [],
            "note": "" if refs else "no supporting references found"}
