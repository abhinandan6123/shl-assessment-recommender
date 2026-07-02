"""Defense-in-depth guardrails that run BEFORE the LLM call.

The system prompt already instructs the model to refuse off-topic /
legal / prompt-injection requests, but relying on the model alone is
fragile - a single successful jailbreak in an 8-turn conversation would
leak through. These keyword checks catch the most common/obvious attack
patterns cheaply and deterministically, without needing a model call.

This is intentionally conservative: it only short-circuits on fairly
unambiguous injection attempts. Ambiguous or borderline messages are left
to the LLM (which has its own refusal instructions in the system prompt).
"""
import re

INJECTION_PATTERNS = [
    r"ignore (all |the )?(previous|above|prior) instructions",
    r"disregard (all |the )?(previous|above|prior) instructions",
    r"you are (now|no longer) (a |an )?(?!.*shl)",  # "you are now DAN" etc.
    r"system prompt",
    r"reveal your (instructions|prompt|system prompt)",
    r"act as (a |an )?(?!.*shl)",
    r"jailbreak",
    r"developer mode",
    r"pretend (you are|to be)",
    r"do anything now",
    r"\bdan\b",
    r"override your (rules|guidelines|instructions)",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]


def looks_like_injection(text: str) -> bool:
    return any(p.search(text) for p in _COMPILED)


INJECTION_REPLY = (
    "I can only help with finding and comparing SHL assessments. "
    "I won't follow instructions that try to change how I operate."
)
