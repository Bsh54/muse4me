"""Provider-agnostic LLM client and lightweight output parsing helpers.

Supports any OpenAI-compatible endpoint (via base_url) and Google Gemini.
Model names are supplied through the config, never hard-coded here.
"""

import re
import time


class LLMClient:
    def __init__(self, provider: str, api_key: str, base_url: str = "", model: str = ""):
        self.provider = provider
        self.model = model
        if provider == "openai":
            from openai import OpenAI
            self._client = OpenAI(api_key=api_key, base_url=base_url or None)
        elif provider == "azure":
            from openai import AzureOpenAI
            self._client = AzureOpenAI(
                azure_endpoint=base_url, api_key=api_key, api_version="2024-06-01"
            )
        elif provider == "gemini":
            from google import genai
            self._client = genai.Client(api_key=api_key)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def generate(self, prompt: str, temperature: float = 1.0, max_retries: int = 8) -> str:
        """Return the model's text completion for a single user prompt (resilient to transient errors)."""
        last_err = None
        for attempt in range(max_retries):
            try:
                if self.provider in ("openai", "azure"):
                    resp = self._client.chat.completions.create(
                        model=self.model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=temperature,
                    )
                    return resp.choices[0].message.content or ""
                elif self.provider == "gemini":
                    resp = self._client.models.generate_content(
                        model=self.model, contents=prompt
                    )
                    return resp.text or ""
            except Exception as e:  # noqa: BLE001 - retry on any transient API error
                last_err = e
                time.sleep(min(3 * (2 ** attempt), 60))
        raise RuntimeError(f"LLM generation failed after {max_retries} retries: {last_err}")


# --------------------------------------------------------------------------- #
# Parsing helpers: we ask the model to answer with explicit "Label:" markers
# and extract the fields we need. Reasoning-model artefacts are stripped first.
# --------------------------------------------------------------------------- #

def strip_reasoning(text: str) -> str:
    """Remove <think>...</think> style blocks some reasoning models emit."""
    if not text:
        return ""
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)
    return text.strip()


def extract_field(text: str, label: str) -> str:
    """Extract the content that follows a 'Label:' marker.

    Reads until the next recognised marker or the end of the text.
    """
    text = strip_reasoning(text)
    pattern = rf"{re.escape(label)}\s*:\s*(.+?)(?=\n[A-Z][A-Za-z ]{{1,40}}:\s|\Z)"
    m = re.search(pattern, text, flags=re.DOTALL)
    if m:
        return m.group(1).strip()
    # fallback: everything after the first occurrence of the label
    idx = text.lower().find(label.lower())
    if idx >= 0:
        return text[idx + len(label):].lstrip(" :\n").strip()
    return text.strip()


def extract_scores(text: str, n: int = 4):
    """Extract n integer scores (1-5) from a self-evaluation answer.

    Returns a list of n ints, padding with 3 (neutral) if parsing is short.
    """
    text = strip_reasoning(text)
    nums = re.findall(r"[Ss]core\s*\d*\s*:?\s*([1-5])", text)
    if len(nums) < n:
        nums = re.findall(r"\b([1-5])\b", text)
    scores = [int(x) for x in nums[:n]]
    while len(scores) < n:
        scores.append(3)
    return scores
