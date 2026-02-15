"""
Tiny in-memory "knowledge base" about LangChain, agents, and vector databases.

The purpose of this module is to show how to go from **plain text strings**
to a **vector store + retriever** that an agent can use as a tool.
"""

from __future__ import annotations

from typing import List, Tuple

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from .config import get_settings


def _study_notes() -> Tuple[List[str], List[dict]]:
    """Return (texts, metadatas) for a tiny study corpus.

    Each text is intentionally short and opinionated so the agent has something
    concrete to retrieve and quote when answering your questions.
    """

    texts: List[str] = [
        (
            "LangChain is a Python and JavaScript framework for building applications "
            "with large language models (LLMs). It focuses on composing LLMs with "
            "other components such as tools, memory, and vector stores."
        ),
        (
            "An agent in LangChain couples an LLM with tools. The LLM reasons about "
            "what to do next and can decide to call tools, inspect their outputs, "
            "and iterate until it can return a final answer."
        ),
        (
            "A vector database stores numeric embeddings of text. Each piece of text "
            "is turned into a high-dimensional vector. Similar texts live close to "
            "each other in this vector space."
        ),
        (
            "In LangChain, a typical retrieval-augmented generation (RAG) setup uses "
            "an embeddings model plus a vector store, exposed as a retriever, to "
            "supply relevant context to an LLM for a specific user question."
        ),
        (
            "Tools make an LLM more \"agentic\" by letting it take actions. Examples "
            "include web search, database queries, calculators, or a vector-store "
            "retriever that looks up domain knowledge."
        ),
        (
            "When designing an agentic system, keep the tools small and focused. "
            "Each tool should do one thing well and have a clear name and description "
            "so the LLM can choose it correctly."
        ),
        (
            "Chroma is a simple, open-source vector database with an in-process API "
            "that works well for toy projects and prototypes. LangChain integrates "
            "with Chroma via the Chroma vector store wrapper."
        ),
        (
            "Embeddings models like text-embedding-3-small map text to vectors. "
            "You can reuse the same embeddings model for many different retrieval "
            "tasks as long as the language and domain are similar."
        ),
    ]

    metadatas: List[dict] = [
        {"topic": "langchain_overview"},
        {"topic": "agents"},
        {"topic": "vector_databases"},
        {"topic": "rag"},
        {"topic": "tools"},
        {"topic": "agent_design"},
        {"topic": "chroma"},
        {"topic": "embeddings"},
    ]

    assert len(texts) == len(metadatas), "texts and metadatas must have the same length"
    return texts, metadatas


def build_retriever():
    """Create an in-memory Chroma vector store and return a retriever.

    In a real application, you would likely:
    - Persist the Chroma collection to disk
    - Populate it from real documents (Markdown, PDFs, database rows, etc.)

    Here we keep everything in memory to make the example easy to run and reset.
    """

    settings = get_settings()

    texts, metadatas = _study_notes()
    embeddings = OpenAIEmbeddings(model=settings.openai_embedding_model)

    vectorstore = Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas,
        collection_name="langchain_study",
    )

    # The retriever wraps the vector store and exposes a simple interface:
    # `get_relevant_documents(query: str) -> List[Document]`
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    return retriever

