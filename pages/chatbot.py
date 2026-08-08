from __future__ import annotations

from pathlib import Path

import streamlit as st

from utils.pdf_processor import (
    build_documents_from_pdfs,
    extract_pdf_text,
    save_uploaded_files,
)

from utils.rag_chain import (
    get_rag_response,
    vector_store_ready_message,
)

from utils.vector_store import (
    create_vector_store,
    load_vector_store,
    save_vector_store,
)


def _get_vector_store():

    if st.session_state.vector_store is not None:
        return st.session_state.vector_store

    try:
        st.session_state.vector_store = load_vector_store()

    except Exception as exc:
        st.error(f"Error loading FAISS index: {exc}")
        st.session_state.vector_store = None

    return st.session_state.vector_store


def _clear_chat() -> None:

    st.session_state.chat_history = []


def _render_pdf_sources(sources):

    if not sources:
        st.info("No PDF sources available.")
        return

    st.markdown("### 📚 PDF Sources")

    for source in sources:

        metadata = source.metadata or {}

        source_name = metadata.get(
            "source",
            "Unknown PDF",
        )

        chunk_number = metadata.get(
            "chunk",
            "?",
        )

        preview = (
            source.page_content[:250]
            .replace("\n", " ")
        )

        st.write(
            f"📄 **{source_name}** | Chunk {chunk_number}"
        )

        st.caption(preview)


def _render_web_sources(web_sources):

    if not web_sources:
        return

    st.markdown("### 🌐 Web Sources")

    for item in web_sources:

        st.markdown(
            f"**{item['title']}**"
        )

        st.write(
            item["href"]
        )

        st.caption(
            item["body"]
        )


def _build_knowledge_base(
    uploaded_files,
) -> None:

    if not uploaded_files:

        st.warning(
            "Upload one or more PDFs first."
        )

        return

    with st.spinner(
        "Processing PDFs and building knowledge base..."
    ):

        # -----------------------------------
        # Save uploaded files
        # -----------------------------------

        save_uploaded_files(
            uploaded_files,
            Path("uploads"),
        )

        # -----------------------------------
        # Extract PDF text
        # -----------------------------------

        combined_text = extract_pdf_text(
            uploaded_files
        )

        # -----------------------------------
        # Build document chunks
        # -----------------------------------

        documents = build_documents_from_pdfs(
            uploaded_files
        )

        if not documents:

            st.warning(
                "No extractable text found in uploaded PDFs."
            )

            return

        # -----------------------------------
        # Check whether existing FAISS index
        # can be reused
        # -----------------------------------

        existing_store = load_vector_store()

        if existing_store is not None:

            st.info(
                "Existing FAISS knowledge base found. "
                "Rebuilding because new PDFs were uploaded."
            )

        # -----------------------------------
        # Create vector store
        # -----------------------------------

        vector_store = create_vector_store(
            documents
        )

        # -----------------------------------
        # Save vector store
        # -----------------------------------

        save_vector_store(
            vector_store
        )

        # -----------------------------------
        # Store in Streamlit session
        # -----------------------------------

        st.session_state.vector_store = (
            vector_store
        )

        st.session_state.source_documents = (
            documents
        )

        st.session_state.summary_source_text = (
            combined_text
        )

        st.success(
            f"✅ Knowledge Base Ready "
            f"({len(documents)} chunks)"
        )


def render_chatbot_page() -> None:

    st.header("🤖 AI Study Assistant")

    st.write(
        "Upload PDFs, build a knowledge base, and chat with your study material."
    )

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "web_search_enabled" not in st.session_state:
        st.session_state.web_search_enabled = False

    # -----------------------------------
    # Upload Section
    # -----------------------------------

    col_left, col_right = st.columns(
        [2, 1]
    )

    with col_left:

        uploaded_files = st.file_uploader(
            "Upload PDF Notes",
            type=["pdf"],
            accept_multiple_files=True,
            key="chatbot_pdf_uploader",
        )

    with col_right:

        st.button(
            "🗑 Clear Chat",
            use_container_width=True,
            on_click=_clear_chat,
        )

        if st.button(
            "📚 Build Knowledge Base",
            use_container_width=True,
        ):
            _build_knowledge_base(
                uploaded_files
            )

    st.divider()

    # -----------------------------------
    # Hybrid RAG Toggle
    # -----------------------------------

    st.session_state.web_search_enabled = st.checkbox(
        "🌐 Enable Web Search",
        value=st.session_state.web_search_enabled,
    )

    if st.session_state.web_search_enabled:

        st.info(
            """
Hybrid RAG Enabled

1. Search PDF Knowledge Base
2. Search Web
3. Gemini combines both
4. Display PDF + Web sources
"""
        )

    # -----------------------------------
    # Load FAISS
    # -----------------------------------

    store = _get_vector_store()

    if store is None:

        st.info(
            vector_store_ready_message()
        )

        st.warning(
            "Knowledge Base Status: Not Available"
        )

    else:

        st.success(
            "Knowledge Base Status: Ready"
        )

    st.divider()

    # -----------------------------------
    # Chat History
    # -----------------------------------

    for message in st.session_state.chat_history:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )

    # -----------------------------------
    # User Question
    # -----------------------------------

    user_question = st.chat_input(
        "Ask a question..."
    )

    if not user_question:
        return

    if not user_question.strip():

        st.warning(
            "Please enter a valid question."
        )

        return

    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": user_question,
        }
    )

    with st.chat_message(
        "user"
    ):
        st.markdown(
            user_question
        )

    # -----------------------------------
    # Generate Answer
    # -----------------------------------

    with st.chat_message(
        "assistant"
    ):

        with st.spinner(
            "Searching..."
        ):

            answer, pdf_sources, web_sources = (
                get_rag_response(
                    user_question,
                    store,
                    use_web_search=st.session_state.web_search_enabled,
                )
            )

        st.markdown(answer)

        if pdf_sources:

            with st.expander(
                "📚 PDF Sources"
            ):
                _render_pdf_sources(
                    pdf_sources
                )

        if web_sources:

            with st.expander(
                "🌐 Web Sources"
            ):
                _render_web_sources(
                    web_sources
                )

    st.session_state.chat_history.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )