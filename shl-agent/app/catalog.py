"""Loads the scraped SHL Individual Test Solutions catalog and provides:

1. A compact text rendering of the whole catalog to ground the LLM prompt
   (346 items comfortably fits in a modern context window, so we don't need
   a vector DB - the model sees the *entire* catalog every turn, which
   removes an entire class of retrieval-recall bugs).
2. Keyword-based candidate narrowing (used only to trim the prompt further
   if needed, and as a cheap backstop signal - not the primary retrieval
   mechanism).
3. Strict validation: every (name, url) pair the LLM returns is checked
   against the real catalog. Anything that doesn't match exactly is
   dropped. This is what actually guarantees "no hallucinated URLs",
   not the prompt wording.
"""
import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "catalog.json")


@dataclass(frozen=True)
class Assessment:
    id: str
    name: str
    url: str
    remote_testing: bool
    adaptive_irt: bool
    test_type: str  # single-letter code, e.g. "K"
    test_type_name: str
    duration_minutes: Optional[int]


class Catalog:
    def __init__(self, path: str = DATA_PATH):
        with open(path, "r") as f:
            raw = json.load(f)
        self.items: List[Assessment] = [Assessment(**r) for r in raw]
        # Fast lookups for grounding/validation
        self._by_url: Dict[str, Assessment] = {a.url.rstrip("/"): a for a in self.items}
        self._by_name_lower: Dict[str, Assessment] = {a.name.lower(): a for a in self.items}

    def __len__(self):
        return len(self.items)

    def lookup(self, name: Optional[str] = None, url: Optional[str] = None) -> Optional[Assessment]:
        """Resolve an LLM-provided (name, url) pair to a real catalog item.

        Tries URL first (most reliable), then falls back to exact
        case-insensitive name match. Returns None if nothing matches -
        callers must drop the item in that case.
        """
        if url:
            hit = self._by_url.get(url.rstrip("/"))
            if hit:
                return hit
        if name:
            hit = self._by_name_lower.get(name.strip().lower())
            if hit:
                return hit
        return None

    def as_prompt_text(self) -> str:
        """Compact one-line-per-item rendering for the system prompt.

        Format: name | url | type_code (type_name) | duration_min |
                remote:Y/N | adaptive:Y/N
        """
        lines = []
        for a in self.items:
            dur = f"{a.duration_minutes}min" if a.duration_minutes is not None else "duration:unknown"
            lines.append(
                f"- {a.name} | {a.url} | {a.test_type} ({a.test_type_name}) | "
                f"{dur} | remote:{'Y' if a.remote_testing else 'N'} | "
                f"adaptive:{'Y' if a.adaptive_irt else 'N'}"
            )
        return "\n".join(lines)

    def type_legend(self) -> str:
        codes = {}
        for a in self.items:
            codes[a.test_type] = a.test_type_name
        return ", ".join(f"{k}={v}" for k, v in sorted(codes.items()))


_catalog_singleton: Optional[Catalog] = None


def get_catalog() -> Catalog:
    global _catalog_singleton
    if _catalog_singleton is None:
        _catalog_singleton = Catalog()
    return _catalog_singleton
