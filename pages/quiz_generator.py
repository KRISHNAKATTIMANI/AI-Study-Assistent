from __future__ import annotations

import streamlit as st

from utils.quiz import (
    generate_fill_blank,
    generate_long_questions,
    generate_mcq,
    generate_short_questions,
    generate_true_false,
)


def render_quiz_generator_page() -> None:
    st.header("Quiz Generator")
    st.write("Generate exam practice questions from your uploaded study materials.")

    source_text = st.text_area(
        "Paste notes or study content",
        value=st.session_state.get("summary_source_text", ""),
        height=220,
    )
    question_type = st.selectbox(
        "Question type",
        ["MCQ", "True / False", "Fill in the blanks", "Short Answers", "Long Answers"],
    )
    difficulty = st.select_slider("Difficulty", ["Easy", "Medium", "Hard"], value="Medium")
    count = st.selectbox("Question count", [5, 10, 20, 50], index=0)

    if st.button("Generate Questions", use_container_width=True):
        if not source_text.strip():
            st.warning("Add notes or upload PDFs before generating questions.")
            return

        with st.spinner("Creating quiz content with Gemini..."):
            if question_type == "MCQ":
                output = generate_mcq(source_text, count=count, difficulty=difficulty)
            elif question_type == "True / False":
                output = generate_true_false(source_text, count=count, difficulty=difficulty)
            elif question_type == "Fill in the blanks":
                output = generate_fill_blank(source_text, count=count, difficulty=difficulty)
            elif question_type == "Short Answers":
                output = generate_short_questions(source_text, count=count, difficulty=difficulty)
            else:
                output = generate_long_questions(source_text, count=count, difficulty=difficulty)

        st.markdown(output)
        source_documents = st.session_state.get("source_documents", [])
        if source_documents:
            with st.expander("Sources"):
                for document in source_documents[:12]:
                    metadata = document.metadata or {}
                    st.write(f"- {metadata.get('source', 'Unknown PDF')} | Chunk {metadata.get('chunk', '?')}")
        else:
            st.info("Source: Uploaded study notes")
