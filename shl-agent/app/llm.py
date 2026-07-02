"""Pluggable LLM backend.

Set LLM_PROVIDER env var to "gemini" (default, matches the assignment's
suggested free tier), "anthropic", or "mock" (no network / no API key,
used for local development and CI - see tests/).

Every provider implements the same contract:
    generate_json(system_prompt: str, messages: list[dict]) -> dict
returning a dict that (hopefully) matches schemas.RawLLMOutput. The
caller (agent.py) is responsible for validating/repairing this - never
trust it blindly.
"""
import json
import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any

RAW_OUTPUT_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "reply": {"type": "string"},
        "action": {
            "type": "string",
            "enum": ["clarify", "recommend", "refine", "compare", "refuse"],
        },
        "recommendations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "url": {"type": "string"},
                    "test_type": {"type": "string"},
                },
                "required": ["name", "url", "test_type"],
            },
        },
        "end_of_conversation": {"type": "boolean"},
    },
    "required": ["reply", "action", "recommendations", "end_of_conversation"],
}


class LLMError(Exception):
    pass


class BaseLLM(ABC):
    @abstractmethod
    def generate_json(self, system_prompt: str, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        ...


class GeminiLLM(BaseLLM):
    """Uses the current `google-genai` SDK (the old `google-generativeai`
    package is deprecated and should not be used for new code)."""

    def __init__(self, model: str = None):
        from google import genai

        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise LLMError("GOOGLE_API_KEY is not set")
        self.client = genai.Client(api_key=api_key)
        self.model_name = model or os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")

    def generate_json(self, system_prompt: str, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        from google.genai import types

        contents = [
            types.Content(
                role="user" if m["role"] == "user" else "model",
                parts=[types.Part.from_text(text=m["content"])],
            )
            for m in messages
        ]
        resp = self.client.models.generate_content(
            model=self.model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=RAW_OUTPUT_JSON_SCHEMA,
                temperature=0.2,
            ),
        )
        try:
            return json.loads(resp.text)
        except (json.JSONDecodeError, AttributeError) as e:
            raise LLMError(f"Gemini returned non-JSON output: {e}")


class AnthropicLLM(BaseLLM):
    def __init__(self, model: str = None):
        import anthropic

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise LLMError("ANTHROPIC_API_KEY is not set")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model_name = model or os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5")

    def generate_json(self, system_prompt: str, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        tool = {
            "name": "emit_chat_response",
            "description": "Emit the structured chat response.",
            "input_schema": RAW_OUTPUT_JSON_SCHEMA,
        }
        resp = self.client.messages.create(
            model=self.model_name,
            max_tokens=1500,
            system=system_prompt,
            messages=[{"role": m["role"], "content": m["content"]} for m in messages],
            tools=[tool],
            tool_choice={"type": "tool", "name": "emit_chat_response"},
        )
        for block in resp.content:
            if block.type == "tool_use":
                return block.input
        raise LLMError("Anthropic response had no tool_use block")


class MockLLM(BaseLLM):
    """Deterministic, network-free stand-in used for local dev / tests.

    Implements a *very* simple rule set so the surrounding FastAPI/
    validation/guardrail plumbing can be exercised without any API key.
    This is NOT meant to pass the real evaluation - it's a plumbing test.
    """

    def __init__(self, catalog=None):
        from app.catalog import get_catalog

        self.catalog = catalog or get_catalog()

    def generate_json(self, system_prompt: str, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        user_turns = [m["content"] for m in messages if m["role"] == "user"]
        last = user_turns[-1].lower() if user_turns else ""

        off_topic_markers = ["legal advice", "lawsuit", "salary negotiation", "visa"]
        if any(k in last for k in off_topic_markers):
            return {
                "reply": "I can only help with finding and comparing SHL assessments, not legal or general hiring advice.",
                "action": "refuse",
                "recommendations": [],
                "end_of_conversation": False,
            }

        combined = " ".join(user_turns).lower()
        keyword_hits = [
            a for a in self.catalog.items
            if any(tok in combined for tok in a.name.lower().split() if len(tok) > 3)
        ]

        enough_context = len(combined.split()) > 12 or len(user_turns) >= 2

        if not enough_context:
            return {
                "reply": "Got it - could you tell me a bit more? For example, the role/skills you're hiring for and roughly what seniority level.",
                "action": "clarify",
                "recommendations": [],
                "end_of_conversation": False,
            }

        picks = keyword_hits[:5] or self.catalog.items[:5]
        return {
            "reply": f"Here are {len(picks)} assessments that look like a good fit based on what you've told me.",
            "action": "recommend",
            "recommendations": [
                {"name": a.name, "url": a.url, "test_type": a.test_type} for a in picks
            ],
            "end_of_conversation": False,
        }


def get_llm() -> BaseLLM:
    provider = os.environ.get("LLM_PROVIDER", "gemini").lower()
    if provider == "gemini":
        return GeminiLLM()
    if provider == "anthropic":
        return AnthropicLLM()
    if provider == "mock":
        return MockLLM()
    raise LLMError(f"Unknown LLM_PROVIDER: {provider}")
