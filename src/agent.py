from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

from .config import get_settings
from .mcp_client import load_mcp_tools
from .knowledge_base import build_retriever
from .tools import create_search_knowledge_base_tool


async def build_agent_async(debug: bool = False):
    settings = get_settings()

    model = ChatOpenAI(
        model=settings.openai_model,
        temperature=0.0,
    )

    tools = await load_mcp_tools()

    if settings.use_rag_tool:
        retriever = build_retriever()
        rag_tool = create_search_knowledge_base_tool(retriever)
        tools = [*tools, rag_tool]

    system_prompt = (
        "You are a helpful assistant with access to tools. "
        "Use the calculator tool for math expressions. "
        "Use the get_weather tool for weather questions. "
    )
    if settings.use_rag_tool:
        system_prompt += (
            "For questions about LangChain, agents, MCP, RAG, or vector databases, "
            "use the search_knowledge_base tool to find relevant notes, then answer. "
        )
    system_prompt += "Be concise."

    agent = create_react_agent(
        model=model,
        tools=tools,
        prompt=system_prompt,
    )

    return agent
