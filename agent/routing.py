"""Branch labels and route helpers for conditional edges."""

from typing import Literal

from agent.state import AgentState

MAX_DRAFTS = 2

MISSING_FACTS = "missing facts"
NOTE_COMPLETE = "note complete"
VAGUE_AND_UNDER_CAP = "vague and under cap"
SPECIFIC_OR_CAP_REACHED = "specific or cap reached"


def route_after_intake(
    state: AgentState,
) -> Literal["missing facts", "note complete"]:
    """Send an incomplete note to a follow-up; a complete one to draft."""
    if state["missing"]:
        return MISSING_FACTS
    return NOTE_COMPLETE


def route_after_review(
    state: AgentState,
) -> Literal["vague and under cap", "specific or cap reached"]:
    """Rewrite a vague draft once, then stop."""
    if state["vague"] and state["drafts"] < MAX_DRAFTS:
        return VAGUE_AND_UNDER_CAP
    return SPECIFIC_OR_CAP_REACHED
