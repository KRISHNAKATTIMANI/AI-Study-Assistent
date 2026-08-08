from __future__ import annotations

import re

from langchain_core.messages import HumanMessage

from utils.rag_chain import get_chat_model

WORD_PATTERN = re.compile(r"[A-Za-z]{4,}")


def _validate_text(text: str) -> None:
    if not text.strip():
        raise ValueError("Add study material before generating questions or flashcards.")


def _format_quiz_output(content: str) -> str:
    """Format and pad LLM quiz responses to guarantee clean multi-line Streamlit Markdown rendering."""
    if not content:
        return ""

    # Ensure bolding on headers like Correct Answer:, Explanation:, Answer:, Model Answer:
    content = re.sub(
        r"(?<!\*)\b(Correct Answer|Answer|Explanation|Model Answer):\s*",
        r"**\1:** ",
        content,
        flags=re.IGNORECASE,
    )

    # Put double linebreaks before options A), B), C), D) or A., B., C., D.
    content = re.sub(
        r"([^\n])\s*([A-D][\.\)]\s+)",
        r"\1\n\n\2",
        content,
    )

    # Put double linebreaks before Answer / Correct Answer / Explanation / Model Answer
    content = re.sub(
        r"([^\n])\s*(\*\*(?:Correct Answer|Answer|Explanation|Model Answer):\*\*|\b(?:Correct Answer|Answer|Explanation|Model Answer):)",
        r"\1\n\n\2",
        content,
        flags=re.IGNORECASE,
    )

    # Put double linebreaks before numbered questions (1., 2., etc.)
    content = re.sub(
        r"([^\n])\s*(\b\d+[\.\)]\s+)",
        r"\1\n\n\2",
        content,
    )

    # Clean up any excess consecutive blank lines (more than 2)
    content = re.sub(r"\n{3,}", "\n\n", content)

    return content.strip()


def _generate_quiz_block(question_type: str, text: str, count: int, difficulty: str) -> str:
    _validate_text(text)

    # Base configuration instructions
    base_instruction = (
        f"You are a precise exam question generator. Create {count} {question_type} questions at {difficulty} difficulty "
        f"using ONLY the study notes provided below. Never use outside information.\n\n"
    )

    # Dynamic strict format templates per question type to guarantee clean Streamlit rendering
    if question_type == "MCQ":
        format_instruction = (
            "CRITICAL FORMATTING RULES FOR STREAMLIT RENDER:\n"
            "1. Put EVERY option (A, B, C, D) on its OWN SEPARATE line with a blank line between options.\n"
            "2. Put TWO blank lines between each question.\n"
            "3. State the correct answer and a brief explanation on separate lines below the options.\n\n"
            "Follow this exact structural layout example:\n"
            "1. [Question Text Here]?\n\n"
            "   A) Option One\n\n"
            "   B) Option Two\n\n"
            "   C) Option Three\n\n"
            "   D) Option Four\n\n"
            "   **Correct Answer:** A\n\n"
            "   **Explanation:** [One-line explanation here]\n\n"
        )
    elif question_type == "True/False":
        format_instruction = (
            "CRITICAL FORMATTING RULES FOR STREAMLIT RENDER:\n"
            "1. Put TWO blank lines between questions.\n"
            "2. Put Answer and Explanation on separate lines.\n\n"
            "Follow this exact structural layout example:\n"
            "1. [Statement Text Here]\n\n"
            "   **Answer:** True\n\n"
            "   **Explanation:** [One-line explanation here]\n\n"
        )
    elif question_type == "Fill in the Blank":
        format_instruction = (
            "CRITICAL FORMATTING RULES FOR STREAMLIT RENDER:\n"
            "1. Put TWO blank lines between questions.\n"
            "2. Put Answer on its own line below the sentence.\n\n"
            "Follow this exact structural layout example:\n"
            "1. [Sentence text with a _____ blank space.]\n\n"
            "   **Answer:** (Missing Word)\n\n"
        )
    else:  # Short and Long answers
        format_instruction = (
            "CRITICAL FORMATTING RULES FOR STREAMLIT RENDER:\n"
            "1. Put TWO blank lines between questions.\n"
            "2. Put Model Answer on its own line below the question.\n\n"
            "Follow this exact structural layout example:\n"
            "1. [Question Text Here]?\n\n"
            "   **Model Answer:** [Concise target answer here]\n\n"
        )

    prompt = (
        f"{base_instruction}"
        f"{format_instruction}\n"
        f"Study Notes:\n{text}"
    )

    response = get_chat_model(temperature=0.35).invoke([HumanMessage(content=prompt)])
    raw_output = str(response.content).strip()
    return _format_quiz_output(raw_output)


def generate_mcq(text: str, count: int = 5, difficulty: str = "Medium") -> str:
    return _generate_quiz_block("MCQ", text, count, difficulty)


def generate_true_false(text: str, count: int = 5, difficulty: str = "Medium") -> str:
    return _generate_quiz_block("True/False", text, count, difficulty)


def generate_fill_blank(text: str, count: int = 5, difficulty: str = "Fill in the Blank") -> str:
    return _generate_quiz_block("Fill in the Blank", text, count, difficulty)


def generate_short_questions(text: str, count: int = 5, difficulty: str = "Medium") -> str:
    return _generate_quiz_block("Short Answer", text, count, difficulty)


def generate_long_questions(text: str, count: int = 5, difficulty: str = "Medium") -> str:
    return _generate_quiz_block("Long Answer", text, count, difficulty)


def generate_flashcards(text: str, count: int = 20) -> list[dict[str, str]]:
    """Generate flashcards as a structured list so the UI can paginate them."""
    _validate_text(text)
    prompt = (
        f"You are a study flashcard generator. Create {count} flashcards from the notes below. "
        f"Return only valid JSON as a list of objects with keys front and back. Keep every front as a question and every back as a concise answer.\n\n"
        f"Study Notes:\n{text}"
    )
    response = get_chat_model(temperature=0.25).invoke([HumanMessage(content=prompt)])
    raw_content = str(response.content).strip()

    if raw_content.startswith("```"):
        raw_content = raw_content.strip("`")
        raw_content = raw_content.removeprefix("json").strip()

    try:
        import json

        payload = json.loads(raw_content)
        cards = []
        for item in payload:
            cards.append(
                {
                    "front": str(item.get("front", "Question")),
                    "back": str(item.get("back", "Answer")),
                }
            )
        return cards[:count]

    except Exception:
        fallback_words = WORD_PATTERN.findall(text.lower())
        unique_words = []
        for word in fallback_words:
            if word not in unique_words:
                unique_words.append(word)
        if not unique_words:
            return [{"front": "No content", "back": "Add notes to generate flashcards."}]
        return [
            {
                "front": f"What is {word}?",
                "back": f"A key term extracted from the uploaded notes: {word}.",
            }
            for word in unique_words[:count]
        ]
