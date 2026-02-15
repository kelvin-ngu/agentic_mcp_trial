"""
Load LangChain tools from MCP servers via langchain-mcp-adapters.

Uses MultiServerMCPClient so the subprocess uses the same Python and cwd
(config sets command=sys.executable and cwd=project root).
"""

from __future__ import annotations

from langchain_core.tools import BaseTool

from .config import get_settings


async def load_mcp_tools() -> list[BaseTool]:
    """Connect to configured MCP servers and return all tools as LangChain BaseTools.

    Server config (including cwd) is passed through so stdio subprocesses
    resolve -m mcp_servers.* correctly. Call from async context (e.g. async def main).
    """
    from langchain_mcp_adapters.client import MultiServerMCPClient

    settings = get_settings()
    client = MultiServerMCPClient(settings.mcp_servers)
    tools = await client.get_tools()
    return list(tools)
