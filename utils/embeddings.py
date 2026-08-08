from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings


load_dotenv()

EMBEDDING_MODEL_NAME = "models/gemini-embedding-001"


def _get_api_key() -> str:
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing Gemini API key. Add GOOGLE_API_KEY to your .env file before using embeddings."
        )
    return api_key


@st.cache_resource(show_spinner=False)
def create_embeddings() -> GoogleGenerativeAIEmbeddings:
    """Create and cache the Gemini embeddings client."""

    return GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL_NAME,
        google_api_key=_get_api_key(),
    )
