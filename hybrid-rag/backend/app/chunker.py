"""Split documents by markdown heading, then into overlapping character windows."""
import hashlib

from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

HEADER_LEVELS = [("#", "h1"), ("##", "h2"), ("###", "h3")]


def _chunk_id(source: str, index: int) -> str:
    return hashlib.sha1(f"{source}::{index}".encode()).hexdigest()[:16]


def _deepest_heading(metadata: dict) -> str:
    return next((metadata[key] for _, key in reversed(HEADER_LEVELS) if key in metadata), "")


def chunk_document(doc: Document, size: int, overlap: int) -> list[Document]:
    if size <= 0 or not 0 <= overlap < size:
        raise ValueError("chunk size must be > 0 and 0 <= overlap < size")

    # strip_headers=False keeps the heading line in the text so BM25 can match it
    sections = MarkdownHeaderTextSplitter(HEADER_LEVELS, strip_headers=False).split_text(doc.page_content)
    windows = RecursiveCharacterTextSplitter(chunk_size=size, chunk_overlap=overlap).split_documents(sections)

    source = doc.metadata["source"]
    chunks = []
    for i, window in enumerate(w for w in windows if w.page_content.strip()):
        chunk_id = _chunk_id(source, i)
        heading = _deepest_heading(window.metadata)
        chunks.append(
            Document(
                id=chunk_id,
                page_content=window.page_content,
                metadata={"id": chunk_id, "source": source, "heading": heading},
            )
        )
    return chunks


def chunk_documents(docs: list[Document], size: int, overlap: int) -> list[Document]:
    return [chunk for doc in docs for chunk in chunk_document(doc, size, overlap)]
