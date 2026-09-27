# Wire nodes and edges into a StateGraph; export compiled `graph` for Studio.
# langgraph.json loads this as "./agent/graph.py:graph" — keep that name.

from langgraph.graph import END, START, StateGraph

from agent.nodes import ask_missing, draft, intake, review
from agent.routing import (
    MISSING_FACTS,
    NOTE_COMPLETE,
    SPECIFIC_OR_CAP_REACHED,
    VAGUE_AND_UNDER_CAP,
    route_after_intake,
    route_after_review,
)
from agent.state import AgentState


def build_graph():
    """Compile the meeting-notes → action-items graph."""
    builder = StateGraph(AgentState)
    builder.add_node("intake", intake)
    builder.add_node("ask_missing", ask_missing)
    builder.add_node("draft", draft)
    builder.add_node("review", review)

    builder.add_edge(START, "intake")
    builder.add_conditional_edges(
        "intake",
        route_after_intake,
        {MISSING_FACTS: "ask_missing", NOTE_COMPLETE: "draft"},
    )
    builder.add_edge("ask_missing", END)
    builder.add_edge("draft", "review")
    builder.add_conditional_edges(
        "review",
        route_after_review,
        {VAGUE_AND_UNDER_CAP: "draft", SPECIFIC_OR_CAP_REACHED: END},
    )
    return builder.compile()


graph = build_graph()
