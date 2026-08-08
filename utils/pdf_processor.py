from __future__ import annotations

from pathlib import Path
from uuid import uuid4
from typing import BinaryIO, Iterable

from PyPDF2 import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Better RAG settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def _source_name(file_object: BinaryIO) -> str:

    return Path(
        getattr(
            file_object,
            "name",
            "uploaded.pdf",
        )
    ).name


def _read_pdf(file_object: BinaryIO) -> str:

    try:

        reader = PdfReader(file_object)

        if getattr(
            reader,
            "is_encrypted",
            False,
        ):

            try:
                reader.decrypt("")
            except Exception as exc:
                raise ValueError(
                    "The PDF is encrypted and could not be opened."
                ) from exc

        pages_text = []

        for page in reader.pages:

            page_text = (
                page.extract_text()
                or ""
            ).strip()

            if page_text:
                pages_text.append(page_text)

        return "\n".join(
            pages_text
        ).strip()

    except Exception as exc:

        raise ValueError(
            f"Could not read {_source_name(file_object)}: {exc}"
        ) from exc


def extract_pdf_text(
    files: Iterable[BinaryIO],
) -> str:
    """
    Extract and combine text from PDFs.
    """

    combined_text = []

    for file_object in files:

        text = _read_pdf(
            file_object
        )

        if text:

            combined_text.append(
                f"[Source: {_source_name(file_object)}]\n{text}"
            )

    return "\n\n".join(
        combined_text
    ).strip()


def split_text_into_chunks(
    text: str,
) -> list[str]:
    """
    Split text into chunks.
    """

    if not text.strip():
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            "",
        ],
    )

    return splitter.split_text(
        text
    )


def build_documents_from_pdfs(
    files: Iterable[BinaryIO],
) -> list[Document]:
    """
    Convert uploaded PDFs into LangChain documents.
    """

    documents = []

    for file_object in files:

        try:

            reader = PdfReader(
                file_object
            )

            source = _source_name(
                file_object
            )

            for page_number, page in enumerate(
                reader.pages,
                start=1,
            ):

                page_text = (
                    page.extract_text()
                    or ""
                ).strip()

                if not page_text:
                    continue

                chunks = split_text_into_chunks(
                    page_text
                )

                for chunk_index, chunk in enumerate(
                    chunks,
                    start=1,
                ):

                    documents.append(
                        Document(
                            page_content=chunk,
                            metadata={
                                "source": source,
                                "page": page_number,
                                "chunk": chunk_index,
                            },
                        )
                    )

        except Exception:
            continue

    return documents


def save_uploaded_files(
    files: Iterable[BinaryIO],
    destination_dir: Path,
) -> list[Path]:
    """
    Save uploaded PDFs locally.
    """

    destination_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    saved_paths = []

    for file_object in files:

        source_path = Path(
            _source_name(
                file_object
            )
        )

        target_path = (
            destination_dir
            / f"{source_path.stem}_{uuid4().hex[:8]}{source_path.suffix}"
        )

        with open(
            target_path,
            "wb",
        ) as handle:

            handle.write(
                file_object.getbuffer()
            )

        saved_paths.append(
            target_path
        )

    return saved_paths