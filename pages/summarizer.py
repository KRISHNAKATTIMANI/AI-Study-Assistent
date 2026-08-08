from __future__ import annotations

import streamlit as st

from utils.rag_chain import generate_summary


def _render_sources() -> None:

    source_documents = st.session_state.get(
        "source_documents",
        [],
    )

    if not source_documents:

        st.info(
            "Source: Uploaded study notes"
        )

        return

    with st.expander(
        "View Sources"
    ):

        displayed = set()

        for document in source_documents[:20]:

            metadata = document.metadata or {}

            source = metadata.get(
                "source",
                "Unknown PDF",
            )

            page = metadata.get(
                "page",
                "?",
            )

            key = f"{source}-{page}"

            if key in displayed:
                continue

            displayed.add(key)

            st.write(
                f"📄 {source} | Page {page}"
            )


def render_summarizer_page() -> None:

    st.header("📝 AI Summarizer")

    st.write(
        "Generate structured exam-ready summaries from uploaded PDFs or custom notes."
    )

    default_text = st.session_state.get(
        "summary_source_text",
        "",
    )

    text = st.text_area(
        "Study Material",
        value=default_text,
        height=250,
        placeholder="Paste notes or upload PDFs and build the knowledge base...",
    )

    summary_style = st.selectbox(
        "Summary Style",
        [
            "Chapter Summary",
            "Key Points",
            "Important Concepts",
            "Definitions",
            "Formulas",
            "Exam Tips",
        ],
    )

    if st.button(
        "Generate Summary",
        use_container_width=True,
    ):

        if not text.strip():

            st.warning(
                "Add notes or upload PDFs before generating a summary."
            )

            return

        with st.spinner(
            "Generating summary..."
        ):

            summary = generate_summary(
                text,
                summary_style,
            )

        st.session_state.generated_summary = (
            summary
        )

    if "generated_summary" in st.session_state:

        st.divider()

        st.subheader(
            "Generated Summary"
        )

        st.markdown(
            st.session_state.generated_summary
        )

        st.download_button(
            label="Download Summary",
            data=st.session_state.generated_summary,
            file_name="study_summary.txt",
            mime="text/plain",
            use_container_width=True,
        )

        _render_sources()