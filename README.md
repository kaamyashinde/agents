# Meeting notes → action items

LangGraph agent that turns a short meeting note into action items using **OpenAI** (real API calls, not mocks).

Intake extracts who, what was decided, and a deadline. If any are missing, the run stops and asks for them. If all are present, a draft node writes action items and a review node checks that every item has an owner and a date. A vague draft is rewritten once.

```text
START → intake
          ├─ missing facts  → ask_missing → END
          └─ note complete  → draft → review
                                      ├─ vague and under cap     → draft (loop once)
                                      └─ specific or cap reached → END
```

## Requirements

- Python **3.11+**
- An [OpenAI](https://platform.openai.com) API key
- A [LangSmith](https://smith.langchain.com) account and API key for the interactive Studio UI

## Setup

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Environment (`.env`)

Fill in your keys (or copy from the example):

```bash
cp .env.example .env
```

| Variable | What it does |
| --- | --- |
| `OPENAI_API_KEY` | Your OpenAI API key. Used by intake, draft, and review. |
| `OPENAI_MODEL` | Chat model id (default `gpt-4o-mini`). |
| `LANGSMITH_API_KEY` | LangSmith API key for Studio / optional tracing. |
| `LANGSMITH_TRACING` | `true` to send runs to LangSmith, `false` to keep tracing off. |

`.env` is gitignored. Do not commit real keys. `langgraph.json` points at `.env` so `langgraph dev` loads these variables automatically.

## Project layout

```
.
├── README.md
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── langgraph.json
└── agent/
    ├── __init__.py
    ├── state.py         # AgentState TypedDict
    ├── nodes.py         # intake / ask_missing / draft / review (OpenAI)
    ├── routing.py       # Conditional edge helpers
    ├── graph.py         # Compiled graph export for Studio
    └── main.py          # Sample runner + architecture.png
```

### What each file does

| File | Role |
| --- | --- |
| `agent/state.py` | Shared fields for one run (`note`, `who`, `what`, `deadline`, `missing`, `action_items`, `drafts`, `vague`, `message`). |
| `agent/nodes.py` | OpenAI-backed intake/draft/review; `ask_missing` is a plain follow-up string. |
| `agent/routing.py` | After intake: missing → ask, else draft. After review: vague under cap → rewrite once, else end. |
| `agent/graph.py` | Builds and compiles the `StateGraph`; exports `graph` for Studio. |
| `agent/main.py` | Runs an incomplete and a complete sample note, then writes `architecture.png`. |

## Run from the terminal

With the venv active and `OPENAI_API_KEY` set:

```bash
python -m agent.main
```

Drawing `architecture.png` via Mermaid needs network access.

## Interactive Studio (`langgraph dev`)

1. Activate the venv and set `OPENAI_API_KEY` plus `LANGSMITH_API_KEY` in `.env`.
2. From the **project root** (the folder that contains `langgraph.json`):

   ```bash
   langgraph dev
   ```

3. When the server is ready:

   - **API:** `http://127.0.0.1:2024`
   - **Docs:** `http://127.0.0.1:2024/docs`
   - **Studio:** [https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024](https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024)

4. Select the `agent` graph and provide input matching `AgentState` (at least a `note` string).

Useful flags:

```bash
langgraph dev --port 8000
langgraph dev --no-browser
```
