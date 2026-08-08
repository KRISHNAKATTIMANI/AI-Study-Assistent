from __future__ import annotations

import os
from typing import Iterable

import streamlit as st
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI

from utils.vector_store import load_vector_store
from utils.web_search import search_web

load_dotenv()

CHAT_MODEL_NAME = "gemini-2.5-flash"


def _get_api_key() -> str:

    api_key = (
        os.getenv("GOOGLE_API_KEY")
        or os.getenv("GEMINI_API_KEY")
    )

    if not api_key:
        raise RuntimeError(
            "Missing Gemini API key."
        )

    return api_key


@st.cache_resource(show_spinner=False)
def get_chat_model(
    temperature: float = 0.2,
) -> ChatGoogleGenerativeAI:

    return ChatGoogleGenerativeAI(
        model=CHAT_MODEL_NAME,
        temperature=temperature,
        google_api_key=_get_api_key(),
    )


def vector_store_ready_message() -> str:

    return (
        "Upload PDFs and click "
        "'Build Knowledge Base' "
        "to create the FAISS index."
    )


def _format_sources(
    documents: Iterable[Document],
) -> list[Document]:

    return list(documents)


def get_rag_response(
    question: str,
    vector_store=None,
    use_web_search: bool = False,
    top_k: int = 4,
):

    if not question.strip():
        raise ValueError(
            "Please enter a question."
        )

    store = vector_store or load_vector_store()

    pdf_context = ""
    pdf_sources = []

    # -----------------------------
    # PDF Search
    # -----------------------------

    if store is not None:

        pdf_sources = store.similarity_search(
            question,
            k=top_k,
        )

        if pdf_sources:

            pdf_context = "\n\n".join(
                doc.page_content
                for doc in pdf_sources
            )

    # -----------------------------
    # Web Search
    # -----------------------------

    web_context = ""
    web_results = []

    if use_web_search:

        web_results = search_web(
            question,
            max_results=5,
        )

        if web_results:

            web_context = "\n\n".join(
                [
                    f"Title: {item['title']}\n"
                    f"Content: {item['body']}\n"
                    f"URL: {item['href']}"
                    for item in web_results
                ]
            )

    # -----------------------------
    # Nothing Found
    # -----------------------------

    if not pdf_context and not web_context:

        return (
            "I could not find relevant information in PDFs or on the web.",
            [],
            [],
        )

    # -----------------------------
    # Hybrid Prompt
    # -----------------------------

    prompt = f"""
You are an AI Study Assistant.

Answer using the available information.

Priority:

1. Prefer PDF information.
2. Use web information only if needed.
3. Mention when information comes from the web.
4. Never make up facts.

Question:
{question}

PDF Context:
{pdf_context}

Web Context:
{web_context}
"""

    response = get_chat_model().invoke(
        prompt
    )

    answer = str(
        response.content
    ).strip()

    return (
        answer,
        _format_sources(pdf_sources),
        web_results,
    )


def generate_summary(
    text: str,
    summary_style: str = "Chapter Summary",
) -> str:

    if not text.strip():

        raise ValueError(
            "Please add study material."
        )

    prompt = f"""
Create a {summary_style}.

Include:

1. Summary
2. Key Points
3. Important Terms
4. Exam Tips

Notes:

{text}
"""

    response = get_chat_model(
        temperature=0.15
    ).invoke(prompt)

    return str(
        response.content
    ).strip()