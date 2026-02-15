# Plan: MCP + LangGraph + RAG Agent Example

## Goal

Transform the current "LangChain Study Coach" into an **agent that uses MCP (Model Context Protocol)** to connect external tools (calculator, weather, etc.) and chooses which tools to use based on the user prompt. The stack will showcase **MCP**, **LangGraph**, and **RAG**.

---

## Architecture (high level)

```
User prompt
    → LangGraph agent (create_agent)
        → LLM decides which tools to call
        → Tools come from:
            (1) MCP servers (calculator, weather, …) via langchain-mcp-adapters
            (2) Optional: RAG tool (search over a small doc corpus)
    → Agent returns final answer
```

- **MCP**: We use `langchain-mcp-adapters` to connect to one or more MCP servers (stdio). The adapter turns MCP tools into LangChain `BaseTool` so the agent can call them.
- **LangGraph**: We keep using `create_agent(model, tools=...)` which returns a compiled graph; we invoke it with `{"messages": [HumanMessage(...)]}`.
- **RAG**: We keep the existing vector store + retriever and expose it as one optional tool (e.g. "search_docs") so the agent can answer from a small knowledge base when relevant.

---

## Components

### 1. MCP client (new)

- **File**: `src/mcp_client.py`
- **Role**: Create a `MultiServerMCPClient` (from `langchain-mcp-adapters`) configured with server definitions (transport, command, args). Expose an **async** function that returns a list of LangChain tools (e.g. `async def load_mcp_tools() -> list`).
- **Config**: Server entries (e.g. calculator, weather) will be read from `src/config.py` (e.g. paths to server scripts or commands) so we can add more servers without code changes.

### 2. MCP servers (new, bundled)

To make the project self-contained and runnable without external MCP servers, we add two minimal **stdio** MCP servers in the repo:

- **`mcp_servers/calculator.py`**
  - MCP server (using `mcp` Python SDK, stdio transport).
  - Exposes one tool, e.g. `calculate(expression: str)` that evaluates a safe math expression (e.g. restrict to numbers and +, -, *, /, parentheses) and returns the result as text.
- **`mcp_servers/weather.py`**
  - MCP server (stdio).
  - Exposes one tool, e.g. `get_weather(location: str)` that returns mock weather data (or a simple real API later) so the agent can answer "what's the weather in X?".

Both servers will be runnable as: `python -m mcp_servers.calculator` and `python -m mcp_servers.weather` (or equivalent), and the MCP client will start them via stdio (subprocess with command/args).

### 3. Config

- **File**: `src/config.py`
- **Changes**: Add settings for MCP server definitions (e.g. a dict or list of server configs: name, transport `"stdio"`, `command`, `args`). Use project-relative paths so that the bundled calculator and weather servers are used by default. Optional: allow disabling RAG or disabling specific MCP servers via env vars.

### 4. Agent

- **File**: `src/agent.py`
- **Changes**:
  - **Tools**: Build the tool list from (1) MCP tools (loaded asynchronously) and (2) optional RAG tool (existing `create_search_knowledge_base_tool(retriever)`). So the agent gets e.g. `[calculator, get_weather, search_docs]`.
  - **API**: Because `MultiServerMCPClient.get_tools()` is async, we have two options:
    - **Option A**: Sync wrapper at startup: `asyncio.run(load_mcp_tools())` once, then use sync `agent.invoke` in the CLI. (If the adapter’s tool invocations block on the MCP call, this is fine.)
    - **Option B**: Make the app async: `async def main()`, `build_agent_async()` that `await client.get_tools()`, and `await agent.ainvoke(...)` in the loop.
  - **Choice**: Use **Option B** (async main and ainvoke) to avoid any subtle blocking and to align with the MCP adapter’s async API.
  - **System prompt**: Update to describe the available tools (calculator, weather, and optional doc search) and instruct the agent to choose the right tool(s) based on the user’s question.

### 5. Main CLI

- **File**: `src/main.py`
- **Changes**:
  - Run an **async** `main()` (e.g. `asyncio.run(main())`).
  - In `main()`: call an async agent builder that loads MCP tools and optionally RAG, then builds the graph.
  - Loop: read user input, call `await agent.ainvoke({"messages": [HumanMessage(content=user_input)]})`, print the last message content.
  - Update banner and prompts to describe the new behavior (e.g. “Ask for calculations, weather, or doc search”).

### 6. RAG (optional but kept)

- **Files**: `src/knowledge_base.py`, `src/tools.py`
- **Role**: Keep the existing vector store and `create_search_knowledge_base_tool`. We can rename the tool to something like `search_docs` and keep the corpus as a small “project docs” or “FAQ” so the agent can answer conceptual questions. This demonstrates RAG in the same agent as MCP tools.

### 7. Dependencies

- **File**: `requirements.txt`
- **Add**: `langchain-mcp-adapters`, `mcp` (and any version pins if needed). Keep existing: langchain, langchain-openai, langchain-community, chromadb, python-dotenv.

### 8. Documentation

- **File**: `README.md`
- **Rewrite** to describe:
  - The new purpose: MCP-powered agent with calculator, weather, and optional RAG.
  - Concepts: MCP (tools from external servers), LangGraph (agent graph), RAG (doc search tool).
  - Setup: install deps, set `OPENAI_API_KEY`, run MCP servers (or point to bundled ones).
  - How to run the agent (`python -m src.main`).
  - How to add more MCP servers (config + server script).
  - Optional: link to MCP docs and langchain-mcp-adapters.

---

## File summary

| Action   | File / path |
|----------|-------------|
| **New**  | `PLAN.md` (this file) |
| **New**  | `mcp_servers/calculator.py` – MCP server, calculator tool (stdio) |
| **New**  | `mcp_servers/weather.py` – MCP server, weather tool (stdio, mock) |
| **New**  | `mcp_servers/__init__.py` (empty or minimal) |
| **New**  | `src/mcp_client.py` – MultiServerMCPClient, async `load_mcp_tools()` |
| **Edit** | `src/config.py` – MCP server config (and optional env toggles) |
| **Edit** | `src/agent.py` – Build agent with MCP tools + optional RAG; async build; updated system prompt |
| **Edit** | `src/main.py` – Async main, load agent with MCP tools, ainvoke loop; updated copy |
| **Keep** | `src/knowledge_base.py` – unchanged (RAG) |
| **Edit** | `src/tools.py` – Keep RAG tool only (or leave as-is); no MCP here |
| **Edit** | `requirements.txt` – add langchain-mcp-adapters, mcp |
| **Edit** | `README.md` – New description, setup, run, add more servers |

---

## Implementation order

1. Add `langchain-mcp-adapters` and `mcp` to `requirements.txt`.
2. Implement `mcp_servers/calculator.py` and `mcp_servers/weather.py` (stdio, minimal tools).
3. Add MCP server config to `src/config.py`.
4. Implement `src/mcp_client.py` (MultiServerMCPClient, async `load_mcp_tools()`).
5. Update `src/agent.py`: async `build_agent_async()`, combine MCP tools + RAG tool, new system prompt.
6. Update `src/main.py`: async main, call `build_agent_async`, use `ainvoke`, update prompts.
7. Update `README.md` and optionally `.env.example` if we add new env vars.

After this, the project will be an MCP + LangGraph + RAG agent example that uses calculator, weather, and doc search based on the user prompt.
