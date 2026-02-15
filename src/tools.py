"""
LangChain tools used by the Study Coach agent.

Right now we expose a single tool:

- `search_knowledge_base`: run a semantic search over the tiny study corpus.

The important part is not the sophistication of the tool, but **how it is wired**
so the agent can decide when to call it.
"""

from __future__ import annotations

from typing import Any

from langchain.tools import tool
from langchain_core.retrievers import BaseRetriever


def create_search_knowledge_base_tool(retriever: BaseRetriever):
    """Create a LangChain tool that searches the study knowledge base.

    We define the function inside this factory so it can close over the
    `retriever` instance while still being decorated with `@tool`.
    """

    @tool
    def search_knowledge_base(query: str) -> str:
        """Search the local LangChain study notes.

        Use this tool when you need precise definitions or focused explanations
        about LangChain, agents, tools, or vector databases.
        """

        # Newer LangChain retrievers are Runnables (`.invoke`); some older ones
        # expose `.get_relevant_documents`. Support both so this file stays
        # educational and robust across versions.
        if hasattr(retriever, "get_relevant_documents"):
            docs = retriever.get_relevant_documents(query)  # type: ignore[attr-defined]
        else:
            docs = retriever.invoke(query)
        if not docs:
            return "No relevant study notes found."

        joined = []
        for i, doc in enumerate(docs, start=1):
            topic = doc.metadata.get("topic", "unknown_topic")
            joined.append(f"[{i}] (topic={topic}) {doc.page_content}")

        # The agent will see this text and can quote from it or reason over it.
        return "\n\n".join(joined)

    return search_knowledge_base


__all__ = ["create_search_knowledge_base_tool"]

