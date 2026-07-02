"""Pydantic models matching the exact API schema from the assignment spec.

The schema is non-negotiable: deviating breaks the automated evaluator.
"""
from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]


class Recommendation(BaseModel):
    name: str
    url: str
    test_type: str


class ChatResponse(BaseModel):
    reply: str
    recommendations: List[Recommendation] = Field(default_factory=list)
    end_of_conversation: bool = False


class HealthResponse(BaseModel):
    status: str = "ok"


# Internal schema the LLM is asked to produce (before catalog validation).
# Kept separate from ChatResponse because raw LLM output may reference
# catalog items only by name/url and needs to be cross-checked against
# the real catalog before it becomes a ChatResponse.
class RawLLMOutput(BaseModel):
    reply: str
    recommendations: List[Recommendation] = Field(default_factory=list)
    end_of_conversation: bool = False
    action: Optional[Literal["clarify", "recommend", "refine", "compare", "refuse"]] = None
