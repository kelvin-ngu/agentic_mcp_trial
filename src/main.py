"""
CLI for the MCP + LangGraph + RAG agent.

Run from project root: python -m src.main

Then ask for calculations, weather, or doc search; the agent picks the right tools.
"""

from __future__ import annotations

import asyncio
import traceback
import sys
from textwrap import dedent

from langchain_core.messages import HumanMessage

from .agent import build_agent_async


async def main_async() -> None:
    agent = await build_agent_async(debug=True)

    print(
        dedent(
            """
            ============================================
            MCP + LangGraph + RAG Agent
            ============================================

            Ask anything — e.g. "What is 123 * 45?",
            "Weather in Tokyo?", or "What is RAG?"

            Type 'exit' or 'quit' to stop.
            """
        ).strip()
    )

    while True:
        try:
            user_input = input("\nYou (or 'exit'): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye.")
            break

        if user_input.lower() in ("exit", "quit"):
            print("Bye.")
            break

        if not user_input:
            continue

        try:
            state = {"messages": [HumanMessage(content=user_input)]}
            result = await agent.ainvoke(state)
        except Exception as exc:
            print("\n[ERROR]")
            traceback.print_exc()
            continue


        messages = result.get("messages", [])
        if not messages:
            print("\n[WARN] No messages in result.")
            continue

        last = messages[-1]
        content = getattr(last, "content", last)
        if isinstance(content, list):
            parts = []
            for block in content:
                if isinstance(block, dict) and "text" in block:
                    parts.append(block["text"])
                elif hasattr(block, "text"):
                    parts.append(block.text)
                else:
                    parts.append(str(block))
            content = "\n".join(parts) if parts else str(content)

        print("\nAgent:\n")
        print(content)


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
