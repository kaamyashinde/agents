# LangGraph agent starter

Empty reusable skeleton for any agentic LangGraph task. Layout: state, nodes, routing, graph, and a small CLI entrypoint. The Python modules are intentionally blank (purpose comment only) so you fill them for your use case.

## Requirements

- Python **3.11+** (the in-memory LangGraph Studio server needs 3.11 or newer)
- A [LangSmith](https://smith.langchain.com) account and API key for the interactive Studio UI

## Setup

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Environment (`.env`)

`.env` is already present with empty placeholders. Fill in your key (or copy from the example):

```bash
cp .env.example .env   # optional; .env already exists
```

| Variable | What it does |
| --- | --- |
| `LANGSMITH_API_KEY` | Your LangSmith API key (LangSmith → Settings). Studio uses it to attach to the local server; tracing uses it when enabled. |
| `LANGSMITH_TRACING` | `true` to send runs to LangSmith, `false` to keep tracing off. |

`.env` is gitignored. Do not commit real keys. `langgraph.json` points at `.env` so `langgraph dev` loads these variables automatically.

## Project layout

```
.
├── README.md
├── .env                 # Secrets / flags (placeholders only until you fill them)
├── .env.example         # Same keys, safe to commit
├── .gitignore
├── requirements.txt     # langgraph + langgraph-cli[inmem]
├── langgraph.json       # Registers the graph for Studio
└── agent/
    ├── __init__.py
    ├── state.py         # Shared state for one run
    ├── nodes.py         # One function per step
    ├── routing.py       # Branch labels and route helpers
    ├── graph.py         # Wires nodes and edges; exports `graph`
    └── main.py          # Script runner + architecture diagram
```

### What each file does

| File | Role |
| --- | --- |
| `agent/state.py` | Define a `TypedDict` (e.g. `AgentState`) with the fields every node reads and writes. |
| `agent/nodes.py` | Step functions. Each takes state and returns a **partial update** dict. |
| `agent/routing.py` | Named branch labels and `route_after_*` helpers for conditional edges (e.g. missing facts vs continue, rewrite loop vs end). |
| `agent/graph.py` | Build a `StateGraph`, add nodes/edges, compile it, and assign the result to a module-level `graph` so Studio can load it. |
| `agent/main.py` | Invoke sample inputs from the terminal; optionally call `app.get_graph().draw_mermaid_png(...)` to write `architecture.png`. |
| `langgraph.json` | Tells the LangGraph CLI which module exports the compiled graph and which env file to load. |
| `requirements.txt` | Pinned LangGraph runtime + CLI (in-memory Studio server). |

### Typical control flow

A common pattern when wiring `graph.py` (adjust names to your domain):

```text
START → intake
          ├─ missing facts  → ask_missing → END
          └─ task complete  → draft → review
                                      ├─ vague and under cap     → draft (loop once)
                                      └─ specific or cap reached → END
```

## What to implement (fill the empty files)

1. **`state.py`** — TypedDict fields for one run (input text, missing slots, draft output, rewrite counter, …).
2. **`nodes.py`** — Step functions such as `intake`, `ask_missing`, `draft`, `review` (add or remove as needed).
3. **`routing.py`** — Labels + `route_after_*` helpers (cap rewrite loops if you have them).
4. **`graph.py`** — `build_graph()` that compiles the graph; keep `graph = build_graph()` at module level for Studio.
5. **`main.py`** — Sample inputs and print results.

Until those are filled, `python -m agent.main` and `langgraph dev` will not run a real agent — that is expected for this starter.

## Run from the terminal (after you implement)

With the venv active, from the project root:

```bash
python -m agent.main
```

Drawing `architecture.png` via Mermaid needs network access.

## Interactive Studio (`langgraph dev`)

LangGraph Studio is the interactive debugger: pick a graph, set input state, step through nodes, and inspect state after each hop.

1. Implement `agent/graph.py` so it exports a compiled `graph`.
2. Activate the venv and put a valid `LANGSMITH_API_KEY` in `.env`.
3. From the **project root** (the folder that contains `langgraph.json`):

   ```bash
   langgraph dev
   ```

4. When the server is ready you get roughly:

   - **API:** `http://127.0.0.1:2024`
   - **Docs:** `http://127.0.0.1:2024/docs`
   - **Studio:** [https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024](https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024)

5. In Studio, select the `agent` graph (id from `langgraph.json`), provide input that matches your state schema, and run.

Hot reload is on by default: edit nodes or routes and the next run picks up the changes.

Useful flags:

```bash
langgraph dev --port 8000      # different port
langgraph dev --no-browser     # do not open the browser
```

## Adapting this starter for a new task

1. **State** — Fields in `agent/state.py`.
2. **Nodes** — Bodies in `agent/nodes.py` (add/remove as needed).
3. **Routing** — Labels and conditions in `agent/routing.py`.
4. **Graph** — Edges in `agent/graph.py`.
5. **Samples** — Inputs in `agent/main.py`.
6. **Studio id** — Key under `graphs` in `langgraph.json` if you rename the graph.
7. **Package name** — Rename `agent/`, update imports, and change the path in `langgraph.json` (e.g. `./my_agent/graph.py:graph`).
