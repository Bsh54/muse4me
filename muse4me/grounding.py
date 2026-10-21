"""Optional literature grounding.

A thin, optional hook that checks whether the claims in a hypothesis are
supported by the research literature. It is designed to plug into an MCP-based
literature service (Valency / MCP Bond) when one is configured, and to degrade
gracefully (returning an empty result) when it is not, so the pipeline never
depends on an external service being available.
"""


def ground_hypothesis(hypothesis, mcp_tool=None, max_refs=3):
    """Return a grounding report for a hypothesis.

    Parameters
    ----------
    hypothesis : str
    mcp_tool   : callable or None
        A function (query:str, k:int) -> list[dict(title, url, snippet)] that
        queries a literature backend. If None, grounding is skipped.
    """
    if mcp_tool is None:
        return {"grounded": False, "references": [], "note": "no literature backend configured"}
    try:
        refs = mcp_tool(hypothesis, max_refs)
    except Exception as e:  # noqa: BLE001
        return {"grounded": False, "references": [], "note": f"backend error: {e}"}
    return {"grounded": bool(refs), "references": refs or [], "note": ""}
