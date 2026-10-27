"""Load .md / .txt files from a directory as LangChain Documents."""
from pathlib import Path

from langchain_core.documents import Document

SUPPORTED_EXTENSIONS = {".md", ".txt"}


def load_documents(docs_dir: Path) -> list[Document]:
    if not docs_dir.is_dir():
        raise FileNotFoundError(f"Docs directory not found: {docs_dir}")

    paths = sorted(
        p for p in docs_dir.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    )
    return [
        Document(
            page_content=p.read_text(encoding="utf-8"),
            metadata={"source": p.relative_to(docs_dir).as_posix()},
        )
        for p in paths
    ]
