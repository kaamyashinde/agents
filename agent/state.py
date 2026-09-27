"""Shared state for one meeting-note → action-items run."""

from typing import TypedDict


class AgentState(TypedDict):
    note: str
    who: str
    what: str
    deadline: str
    missing: list[str]
    action_items: str
    drafts: int
    vague: bool
    message: str
