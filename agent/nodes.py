"""Node functions: intake, ask_missing, draft, and review (OpenAI-backed)."""

import json
import os
import time

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from agent.state import AgentState

load_dotenv()

REQUIRED_FIELDS = ("who", "what", "deadline")

# #region agent log
_DEBUG_LOG = "/Users/kaamyashinde/Desktop/ntnu/MIDT/Sem1/ov/.cursor/debug-1ee824.log"


def _dbg(hypothesis_id: str, location: str, message: str, data: dict) -> None:
    payload = {
        "sessionId": "1ee824",
        "runId": "pre-fix",
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
        "timestamp": int(time.time() * 1000),
    }
    with open(_DEBUG_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")


# #endregion


class IntakeExtract(BaseModel):
    """Structured extraction from a short meeting note."""

    who: str = Field(description="Person involved, or empty if absent")
    what: str = Field(description="What was decided, or empty if absent")
    deadline: str = Field(description="Deadline or due timing, or empty if absent")


class ReviewVerdict(BaseModel):
    """Whether every action item has an owner and a date."""

    vague: bool = Field(
        description="True if any item lacks a clear owner or a clear date"
    )
    reason: str = Field(description="Brief reason for the verdict")


def _llm() -> ChatOpenAI:
    """Shared ChatOpenAI client from env."""
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0,
    )


def intake(state: AgentState) -> dict:
    """Normalize the note and extract who / what / deadline via OpenAI."""
    # #region agent log
    _dbg(
        "A",
        "nodes.py:intake:entry",
        "intake received state",
        {
            "keys": sorted(list(state.keys())) if hasattr(state, "keys") else str(type(state)),
            "has_note": "note" in state if hasattr(state, "__contains__") else False,
            "note_type": type(state.get("note")).__name__ if hasattr(state, "get") else None,
            "note_empty": not bool((state.get("note") or "") if hasattr(state, "get") else False),
            "state_preview": {
                k: (v[:80] if isinstance(v, str) else type(v).__name__)
                for k, v in (dict(state).items() if hasattr(state, "items") else [])
            },
        },
    )
    # #endregion
    note = " ".join(state["note"].split())
    extractor = _llm().with_structured_output(IntakeExtract)
    result: IntakeExtract = extractor.invoke(
        [
            SystemMessage(
                content=(
                    "Extract who (person), what (decision), and deadline from the "
                    "meeting note. Use an empty string for any field that is not "
                    "clearly present. Do not invent details."
                )
            ),
            HumanMessage(content=note),
        ]
    )
    who = (result.who or "").strip()
    what = (result.what or "").strip()
    deadline = (result.deadline or "").strip()
    values = {"who": who, "what": what, "deadline": deadline}
    missing = [field for field in REQUIRED_FIELDS if not values[field]]
    return {
        "note": note,
        "who": who,
        "what": what,
        "deadline": deadline,
        "missing": missing,
        "action_items": "",
        "drafts": 0,
        "vague": False,
        "message": "",
    }


def ask_missing(state: AgentState) -> dict:
    """Ask for the facts the note does not contain."""
    needed = ", ".join(state["missing"])
    return {
        "message": f"Please add these before drafting action items: {needed}.",
    }


def draft(state: AgentState) -> dict:
    """Write action items from who / what / deadline via OpenAI."""
    drafts = state["drafts"] + 1
    rewrite_hint = ""
    if drafts > 1:
        rewrite_hint = (
            " The previous draft was too vague. Every item MUST name a specific "
            "owner and a specific date or deadline."
        )
    response = _llm().invoke(
        [
            SystemMessage(
                content=(
                    "Turn the meeting facts into a short numbered list of action "
                    "items. Each item should include an owner and a deadline when "
                    "the facts support it."
                    + rewrite_hint
                )
            ),
            HumanMessage(
                content=(
                    f"Who: {state['who']}\n"
                    f"What: {state['what']}\n"
                    f"Deadline: {state['deadline']}\n"
                    f"Original note: {state['note']}"
                )
            ),
        ]
    )
    action_items = response.content
    if isinstance(action_items, list):
        action_items = "".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in action_items
        )
    return {"action_items": str(action_items).strip(), "drafts": drafts}


def review(state: AgentState) -> dict:
    """Check that every action item has an owner and a date via OpenAI."""
    reviewer = _llm().with_structured_output(ReviewVerdict)
    verdict: ReviewVerdict = reviewer.invoke(
        [
            SystemMessage(
                content=(
                    "Decide if the action items are specific enough. Set vague=true "
                    "if any item is missing a clear owner (person) or a clear date / "
                    "deadline. Set vague=false only when every item has both."
                )
            ),
            HumanMessage(content=state["action_items"]),
        ]
    )
    message = ""
    if not verdict.vague:
        message = "Action items look complete (owner and date on each)."
    elif state["drafts"] >= 2:
        message = f"Stopped after rewrite cap. Review note: {verdict.reason}"
    return {"vague": verdict.vague, "message": message}
