"""
Configuration for the MCP + LangGraph + RAG agent.

Centralizes environment variables and MCP server definitions used by
langchain-mcp-adapters (stdio transport).
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

# Project root (parent of src/) so MCP subprocess can resolve -m mcp_servers.*
_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _default_mcp_servers() -> dict:
    """Default MCP server config for stdio.

    Uses the current Python executable so the subprocess has the same venv
    and can import mcp. cwd is set to project root so -m mcp_servers.* works.
    """
    return {
        "calculator": {
            "transport": "stdio",
            "command": sys.executable,
            "args": ["-m", "mcp_servers.calculator"],
            "cwd": str(_PROJECT_ROOT),
        },
        "weather": {
            "transport": "stdio",
            "command": sys.executable,
            "args": ["-m", "mcp_servers.weather"],
            "cwd": str(_PROJECT_ROOT),
        },
    }


@dataclass
class Settings:
    """Configuration values: API keys, model names, MCP servers."""

    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    mcp_servers: dict = field(default_factory=_default_mcp_servers)
    use_rag_tool: bool = True


def get_settings() -> Settings:
    """Load settings from environment variables.

    Raises a helpful error if required values are missing so you see failures
    early and clearly.
    """

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. "
            "Set it in your environment or .env file before running the project."
        )

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    use_rag = os.getenv("USE_RAG_TOOL", "true").lower() in ("true", "1", "yes")

    return Settings(
        openai_api_key=api_key,
        openai_model=model,
        openai_embedding_model=embedding_model,
        mcp_servers=_default_mcp_servers(),
        use_rag_tool=use_rag,
    )

