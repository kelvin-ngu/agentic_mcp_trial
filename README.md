# MCP + LangGraph + RAG Agent Example

A small **agentic AI** example that uses **MCP** (Model Context Protocol) to connect tools (calculator, weather), **LangGraph** for the agent loop, and optional **RAG** (doc search). The agent chooses which tools to call based on your prompt.

## What’s in the stack

- **MCP**: Tools are provided by MCP servers (stdio). This project includes two minimal servers: calculator and weather. [langchain-mcp-adapters](https://github.com/langchain-ai/langchain-mcp-adapters) turns MCP tools into LangChain tools.
- **LangGraph**: The agent is built with `create_agent(model, tools, ...)`, which returns a compiled graph. You invoke it with a message list; the LLM decides when to call which tool.
- **RAG**: An optional “search docs” tool over a tiny in-memory corpus (Chroma + OpenAI embeddings) so the agent can answer conceptual questions (e.g. “What is RAG?”).

## Project layout

| Path | Purpose |
|------|--------|
| `src/main.py` | CLI: async loop, loads agent, `ainvoke` on user input |
| `src/agent.py` | Builds agent: MCP tools + optional RAG tool, system prompt |
| `src/mcp_client.py` | Loads MCP tools via `MultiServerMCPClient` (async) |
| `src/config.py` | Settings: API keys, model names, MCP server config |
| `src/tools.py` | RAG tool: wraps retriever as a LangChain tool |
| `src/knowledge_base.py` | In-memory vector store (Chroma) for RAG |
| `mcp_servers/calculator.py` | MCP server: `calculate(expression)` (stdio) |
| `mcp_servers/weather.py` | MCP server: `get_weather(location)` (stdio, mock) |
| `PLAN.md` | Design notes and implementation plan |

## Prerequisites

- **Python 3.10+**
- **OpenAI API key** (for the LLM and, if using RAG, embeddings)

## Setup

1. **Create and activate a virtualenv** (recommended):

   ```bash
   cd Agentic
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   # source .venv/bin/activate  # macOS/Linux
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set your API key** (env or `.env`):

   ```bash
   set OPENAI_API_KEY=sk-your-key
   ```
   Or copy `.env.example` to `.env` and set `OPENAI_API_KEY` there.

## Run

From the **project root** (so `-m mcp_servers.calculator` / `mcp_servers.weather` resolve):

```bash
python -m src.main
```

Try prompts like:

- *“What is 100 / 3?”* → calculator
- *“Weather in Paris?”* → weather
- *“What is RAG?”* → RAG (search_docs) + answer

## Configuration

- **`OPENAI_API_KEY`** (required): OpenAI API key.
- **`OPENAI_MODEL`** (optional): Chat model (default `gpt-4o-mini`).
- **`USE_RAG_TOOL`** (optional): Set to `false` to disable the RAG tool (default `true`).

MCP servers are defined in `src/config.py` (`mcp_servers`). By default they run as:

- `python -m mcp_servers.calculator`
- `python -m mcp_servers.weather`

You can add more servers there (or switch to SSE/HTTP) and they will be loaded as extra tools.

## Adding more MCP tools

1. Add a new MCP server (e.g. `mcp_servers/my_tool.py`) using the same stdio pattern as `calculator.py` / `weather.py`.
2. Register it in `src/config.py` in `_default_mcp_servers()` (or via env/config), e.g. `"my_tool": {"transport": "stdio", "command": "python", "args": ["-m", "mcp_servers.my_tool"]}`.
3. Restart the app; `load_mcp_tools()` will include the new server’s tools.

## References

- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [langchain-mcp-adapters](https://github.com/langchain-ai/langchain-mcp-adapters)
- [LangGraph / create_agent](https://docs.langchain.com/oss/python/langchain/agents)
