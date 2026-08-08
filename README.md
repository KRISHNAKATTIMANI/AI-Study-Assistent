# AI Study Assistant

Gemini-powered Streamlit app for students to upload PDFs, build a local FAISS knowledge base, and study with chat, summaries, quizzes, and flashcards.

## What It Does

- Upload one or more PDFs.
- Extract text safely with `PyPDF2`.
- Split notes into retrieval chunks.
- Build and persist a local FAISS index in `faiss_index/`.
- Ask questions through a RAG chatbot using Gemini 2.5 Flash.
- Generate exam summaries, quiz sets, and flashcards.

## Project Structure

- `app.py`: main Streamlit shell and sidebar navigation
- `pages/chatbot.py`: upload, knowledge-base build, and chat UI
- `pages/summarizer.py`: summary generator
- `pages/quiz_generator.py`: quiz generator
- `pages/flashcards.py`: flashcard review mode
- `utils/pdf_processor.py`: PDF extraction, chunking, and upload storage helpers
- `utils/embeddings.py`: Gemini embedding client
- `utils/vector_store.py`: FAISS create/save/load helpers
- `utils/rag_chain.py`: Gemini RAG and summarization helpers
- `utils/quiz.py`: quiz and flashcard generation helpers
- `uploads/`: local uploaded PDFs
- `faiss_index/`: persisted FAISS index files
- `assets/`: optional static assets

## Installation

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and add your Gemini API key.

## Environment Variables

- `GOOGLE_API_KEY`: required for Gemini chat and embeddings

## Run Commands

Start the app:

```bash
streamlit run app.py
```

If you want to verify the code only:

```bash
python -m compileall AI-Study-Assistant
```

## Deployment Guide

### Streamlit Community Cloud

1. Push the repository to GitHub.
2. Create a new Streamlit app from the repo.
3. Add `GOOGLE_API_KEY` in the app secrets or environment settings.
4. Set the main entry point to `app.py`.

### Render / Similar Hosts

1. Use `streamlit run app.py` as the start command.
2. Configure `GOOGLE_API_KEY` as an environment variable.
3. Ensure the host provides writable local storage for `uploads/` and `faiss_index/`.

## Best Practices

- Use clean PDFs with selectable text for best extraction quality.
- Rebuild the knowledge base after uploading new study material.
- Keep the Gemini API key out of source control.
- Store only study files you are comfortable keeping locally.
- Prefer shorter, focused source PDFs for more precise retrieval.

## Notes

- The app does not use Firebase, Firestore, login, or user accounts.
- If the FAISS index is missing, build it from the chatbot page before asking questions.
