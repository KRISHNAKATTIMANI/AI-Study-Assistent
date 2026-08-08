from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

from pages.chatbot import render_chatbot_page
from pages.flashcards import render_flashcards_page
from pages.quiz_generator import render_quiz_generator_page
from pages.summarizer import render_summarizer_page

load_dotenv()

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==================================================
# CUSTOM CSS
# ==================================================

APP_CSS = """
<style>

.main {
    padding-top: 1rem;
}

.app-title {
    text-align: center;
    padding: 10px;
}

.status-box {
    padding: 10px;
    border-radius: 10px;
}

</style>
"""

# ==================================================
# SESSION STATE
# ==================================================

def _initialize_state() -> None:

    defaults = {
        "active_page": "Chatbot",
        "chat_history": [],
        "vector_store": None,
        "source_documents": [],
        "summary_source_text": "",
        "flashcards": [],
        "flashcard_index": 0,

        # Future Hybrid RAG
        "web_search_enabled": False,

        # Future Agent Memory
        "conversation_memory": [],
    }

    for key, value in defaults.items():

        if key not in st.session_state:
            st.session_state[key] = value


# ==================================================
# GEMINI STATUS
# ==================================================

def _has_gemini_key() -> bool:

    return bool(
        os.getenv("GOOGLE_API_KEY")
        or os.getenv("GEMINI_API_KEY")
    )


# ==================================================
# SIDEBAR
# ==================================================

def _sidebar_navigation() -> None:

    with st.sidebar:

        st.markdown(
            """
            # 📚 AI Study Assistant

            Gemini-powered learning from PDFs.

            ---
            """
        )

        st.subheader("Navigation")

        pages = [
            "Chatbot",
            "Quiz Generator",
            "Summarizer",
            "Flashcards",
        ]

        for page in pages:

            if st.button(
                page,
                use_container_width=True,
                key=f"nav_{page}",
            ):
                st.session_state.active_page = page

        st.divider()

        st.subheader("Settings")

        st.session_state.web_search_enabled = st.checkbox(
            "🌐 Enable Web Search",
            value=st.session_state.web_search_enabled,
        )

        st.caption(
            "Currently disabled until web integration is added."
        )

        st.divider()

        st.subheader("System Status")

        st.write(
            "Gemini API Key:",
            "✅ Configured"
            if _has_gemini_key()
            else "❌ Missing",
        )

        st.write("Vector Store: FAISS")

        st.write("Storage: Local PDFs")

        st.write("Mode: Offline RAG")

        st.divider()

        st.caption(
            "Version 2.0 (Hybrid RAG Ready)"
        )


# ==================================================
# PAGE ROUTER
# ==================================================

def _render_page() -> None:

    active_page = st.session_state.active_page

    if active_page == "Chatbot":
        render_chatbot_page()

    elif active_page == "Quiz Generator":
        render_quiz_generator_page()

    elif active_page == "Summarizer":
        render_summarizer_page()

    elif active_page == "Flashcards":
        render_flashcards_page()

    else:
        render_chatbot_page()


# ==================================================
# MAIN
# ==================================================

def main() -> None:

    _initialize_state()

    st.markdown(
        APP_CSS,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="app-title">

        <h1>📚 AI Study Assistant</h1>

        <p>
        Upload PDFs, build a knowledge base,
        chat with notes, generate summaries,
        quizzes, flashcards, and prepare
        smarter with Gemini AI.
        </p>

        </div>
        """,
        unsafe_allow_html=True,
    )

    _sidebar_navigation()

    _render_page()


# ==================================================
# ENTRY POINT
# ==================================================

if __name__ == "__main__":
    main()