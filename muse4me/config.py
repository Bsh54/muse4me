"""Configuration loading for muse4me."""

import json
import os
from dataclasses import dataclass, field


@dataclass
class Config:
    provider: str = "openai"            # "openai" (OpenAI-compatible) or "gemini"
    api_key: str = ""
    base_url: str = "https://api.openai.com/v1"
    model_retrieve: str = "gpt-4o"
    model_generate: str = "gpt-4o"
    model_evaluate: str = "gpt-4o"
    model_judges: list = field(default_factory=list)   # independent panel for rediscovery/leakage scoring
    domain: str = "solid-state electrolytes"
    temperature: float = 1.0
    num_mutations: int = 3
    num_refine_iters: int = 2
    retrieve_window: int = 12
    retrieve_keep: int = 3
    retrieve_rounds: int = 2
    max_inspirations: int = 4           # hard cap on inspirations evolved per entry (bounds cost/time)
    inspiration_mode: str = "far"       # "far" (potential) or "near" (similarity) or "none"
    extra: dict = field(default_factory=dict)

    @classmethod
    def load(cls, path: str) -> "Config":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        known = {k: data[k] for k in data if k in cls.__dataclass_fields__}
        extra = {k: data[k] for k in data if k not in cls.__dataclass_fields__}
        cfg = cls(**known)
        cfg.extra = extra
        # allow the API key to come from the environment instead of the file
        if not cfg.api_key or cfg.api_key == "YOUR_API_KEY_HERE":
            cfg.api_key = os.environ.get("MUSE4ME_API_KEY", cfg.api_key)
        return cfg
