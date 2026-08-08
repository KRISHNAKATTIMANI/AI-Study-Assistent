from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

FAISS_INDEX_PATH = "faiss_index"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def _get_embeddings() -> HuggingFaceEmbeddings:
    """
    Create a local embedding model.

    This does NOT call the Gemini API.
    """

    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={
            "device": "cpu",
        },
        encode_kwargs={
            "normalize_embeddings": True,
        },
    )


def create_vector_store(
    documents: list[Document],
) -> FAISS:
    """
    Create a FAISS vector store using local embeddings.
    """

    if not documents:
        raise ValueError(
            "No documents were provided for vector store creation."
        )

    embeddings = _get_embeddings()

    return FAISS.from_documents(
        documents,
        embeddings,
    )


def save_vector_store(
    vector_store: FAISS,
) -> None:
    """
    Save FAISS index locally.
    """

    Path(FAISS_INDEX_PATH).mkdir(
        parents=True,
        exist_ok=True,
    )

    vector_store.save_local(
        FAISS_INDEX_PATH
    )


def load_vector_store() -> FAISS | None:
    """
    Load an existing FAISS index.
    """

    faiss_file = os.path.join(
        FAISS_INDEX_PATH,
        "index.faiss",
    )

    if not os.path.exists(faiss_file):
        return None

    embeddings = _get_embeddings()

    return FAISS.load_local(
        FAISS_INDEX_PATH,
        embeddings,
        allow_dangerous_deserialization=True,
    )