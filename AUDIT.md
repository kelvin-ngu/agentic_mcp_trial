# Code audit: mcp_servers/ and src/

## Critical issues (can break at runtime)

### 1. **src/mcp_client.py – wrong API usage**

The code uses `MCPTool(name=server_name, command=..., args=..., transport=...)` and imports `MCPTool` from `langchain_mcp_adapters.tools`. In that package, `MCPTool` is the **MCP type** `Tool` from `mcp.types` (a tool *definition* schema), not a LangChain tool wrapper. So you're building MCP tool definitions, not runnable tools, and the agent will not get the intended tools (or it may fail when binding/invoking).

**Fix:** Use `MultiServerMCPClient(settings.mcp_servers)` and `await client.get_tools()` again, and pass `cwd` in each server config (already in config.py). The adapter’s `create_session` accepts `cwd` in the connection dict.

---

### 2. **src/agent.py – system prompt doesn’t mention RAG**

When `use_rag_tool` is True, the agent has `search_knowledge_base`, but the system prompt only says: *"Use the calculator tool for math expressions. Use the get_weather tool for weather questions."* So the model is never told to use the doc-search tool for conceptual questions (e.g. “What is RAG?”).

**Fix:** Extend the system prompt when RAG is enabled, e.g.: *"For questions about LangChain, agents, MCP, RAG, or vector databases, use the search_knowledge_base tool to find relevant notes, then answer."*

---

## Medium / robustness

### 3. **mcp_servers/calculator.py – float display**

`result == int(result)` can be brittle for floats (e.g. 2.9999999999999996). Prefer something like: use `result.is_integer()` when `isinstance(result, float)`, then format as int, else as float.

### 4. **mcp_servers – schema key: inputSchema vs input_schema**

We use `inputSchema` (camelCase) in `types.Tool(...)`. The MCP SDK’s lowlevel server uses `tool.inputSchema` in jsonschema validation, so camelCase is correct. If you switch to another SDK or type set, confirm the expected key.

### 5. **src/main.py – last message may not be AI content**

We take `messages[-1]` and print its `content`. In a ReAct loop the last message could be a human turn or a tool message. For a single user turn + agent response this is usually fine; for multi-turn or interrupted flows you may want the last **AI** message.

### 6. **src/main.py – content can be a list**

Some chat models use `message.content` as a list of blocks (e.g. text + image). Doing `print(content)` then prints something like `[<object>, ...]`. Safer: if `isinstance(content, list)`, join text parts (e.g. `block.get("text", str(block))`) before printing.

### 7. **src/config.py – cwd only used if mcp_client passes it**

Config correctly sets `cwd` per server. The adapter’s stdio connection supports `cwd`. Once mcp_client uses `MultiServerMCPClient` and the same connection dict (including `cwd`), the subprocess will run with the right working directory.

---

## Minor / consistency

### 8. **src/__init__.py – outdated docstring**

Still says “LangChain Study Coach”; could say “MCP + LangGraph + RAG agent” or similar.

### 9. **mcp_servers – main() return 0**

`anyio.run(arun)` runs until the server is stopped, so `return 0` after it is dead code. Harmless; could remove or replace with a comment.

### 10. **src/agent.py – debug flag unused**

`build_agent_async(debug=True)` is called but `create_react_agent` doesn’t take `debug`. The flag is effectively ignored.

### 11. **src/knowledge_base.py – texts vs metadatas length**

If someone adds a text and forgets a metadata entry (or the other way around), lengths can mismatch and Chroma may error. A one-line assert `assert len(texts) == len(metadatas)` would catch that.

---

## Summary

- **Fixed in code:** (1) mcp_client – now uses MultiServerMCPClient + get_tools(); config already has cwd. (2) agent – RAG mentioned in system prompt when use_rag_tool is True. (3) calculator float display. (6) main.py list content. (8) __init__ docstring. (11) assert in knowledge_base.
- **Optional / already correct:** (4) inputSchema is correct; (5) last message OK for single-turn; (7) cwd used via config; (9)–(10) minor.
