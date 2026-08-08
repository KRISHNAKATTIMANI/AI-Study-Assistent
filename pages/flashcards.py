from __future__ import annotations

import streamlit as st

from utils.quiz import generate_flashcards


def _shift_card(direction: int) -> None:
    if not st.session_state.flashcards:
        return
    st.session_state.flashcard_index = (st.session_state.flashcard_index + direction) % len(st.session_state.flashcards)


def render_flashcards_page() -> None:
    st.header("Flashcards")
    st.write("Turn your notes into study cards with front and back answers.")

    if "flashcard_source_text" not in st.session_state:
        st.session_state.flashcard_source_text = st.session_state.get("summary_source_text", "")

    text = st.text_area(
        "Paste notes or study content",
        height=220,
        key="flashcard_source_text",
    )
    count = st.select_slider("Number of cards", options=[10, 20, 30, 40, 50], value=20)

    if st.button("Generate Flashcards", use_container_width=True):
        if not text.strip():
            st.warning("Add notes or upload PDFs before generating flashcards.")
        else:
            with st.spinner("Creating flashcards with Gemini..."):
                st.session_state.flashcards = generate_flashcards(text, count=count)
                st.session_state.flashcard_index = 0

    cards = st.session_state.get("flashcards", [])
    if not cards:
        st.info("Generate flashcards to begin reviewing.")
        return

    index = st.session_state.flashcard_index
    card = cards[index]

    st.caption(f"Card {index + 1} of {len(cards)}")
    st.markdown(
        f"""
        <div style="padding: 1.2rem; border-radius: 1rem; border: 1px solid rgba(148, 163, 184, 0.25); background: white;">
            <h3 style="margin-top: 0;">Front</h3>
            <p>{card['front']}</p>
            <hr />
            <h3>Back</h3>
            <p>{card['back']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    source_documents = st.session_state.get("source_documents", [])
    if source_documents:
        with st.expander("Sources"):
            for document in source_documents[:12]:
                metadata = document.metadata or {}
                st.write(f"- {metadata.get('source', 'Unknown PDF')} | Chunk {metadata.get('chunk', '?')}")
    else:
        st.info("Source: Uploaded study notes")

    nav_left, nav_center, nav_right = st.columns([1, 1, 1])
    with nav_left:
        st.button("Previous Card", use_container_width=True, on_click=_shift_card, args=(-1,))
    with nav_center:
        st.button("Reset", use_container_width=True, on_click=lambda: st.session_state.__setitem__("flashcard_index", 0))
    with nav_right:
        st.button("Next Card", use_container_width=True, on_click=_shift_card, args=(1,))
