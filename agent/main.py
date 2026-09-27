"""CLI runner: invoke sample notes and write architecture.png."""

from pathlib import Path

from dotenv import load_dotenv

from agent.graph import build_graph
from agent.state import AgentState

load_dotenv()

DIAGRAM_PATH = Path(__file__).resolve().parent.parent / "architecture.png"

INCOMPLETE_NOTE = "Talked to Kari about the demo."
COMPLETE_NOTE = (
    "Talked to Kari about the demo. We decided Kari will prepare the slides "
    "and present them by next Friday."
)


def initial_state(note: str) -> AgentState:
    """Build the starting state for one meeting note."""
    return {
        "note": note,
        "who": "",
        "what": "",
        "deadline": "",
        "missing": [],
        "action_items": "",
        "drafts": 0,
        "vague": False,
        "message": "",
    }


def main() -> None:
    """Run incomplete and complete notes, then write the architecture diagram."""
    app = build_graph()

    incomplete = app.invoke(initial_state(INCOMPLETE_NOTE))
    print("incomplete note")
    print(incomplete["missing"])
    print(incomplete["message"])
    print(f"drafts: {incomplete['drafts']}")
    print()

    complete = app.invoke(initial_state(COMPLETE_NOTE))
    print("complete note")
    print(f"who={complete['who']!r} what={complete['what']!r} deadline={complete['deadline']!r}")
    print(complete["action_items"])
    print(complete["message"])
    print(f"drafts: {complete['drafts']} vague: {complete['vague']}")
    print()

    app.get_graph().draw_mermaid_png(output_file_path=str(DIAGRAM_PATH))
    print(f"architecture: {DIAGRAM_PATH}")


if __name__ == "__main__":
    main()
