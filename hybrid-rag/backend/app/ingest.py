"""Build and persist the hybrid index from a docs folder.

Usage: python -m app.ingest [docs_dir]
"""
import json
import logging
import sys
from pathlib import Path

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import InMemoryVectorStore

from app.chunker import chunk_documents
from app.config import settings
from app.loader import load_documents
from app.retrieval import HybridRetriever

logger = logging.getLogger(__name__)


def build_index(docs_dir: Path, index_dir: Path, embeddings: Embeddings, rrf_k: int = settings.rrf_k) -> HybridRetriever:
    docs = load_documents(docs_dir)
    chunks = chunk_documents(docs, settings.chunk_size, settings.chunk_overlap)

    vector_store = InMemoryVectorStore(embeddings)
    if chunks:
        vector_store.add_documents(chunks)

    index_dir.mkdir(parents=True, exist_ok=True)
    vector_store.dump(str(index_dir / "vectors.json"))
    (index_dir / "chunks.json").write_text(
        json.dumps([{"id": c.id, "page_content": c.page_content, "metadata": c.metadata} for c in chunks]),
        encoding="utf-8",
    )
    logger.info("Indexed %d docs into %d chunks", len(docs), len(chunks))
    return HybridRetriever(chunks, vector_store, rrf_k)


def load_index(index_dir: Path, embeddings: Embeddings, rrf_k: int = settings.rrf_k) -> HybridRetriever:
    """Load saved vectors (no re-embedding) and rebuild BM25 from saved chunks."""
    chunks_file = index_dir / "chunks.json"
    if not chunks_file.exists():
        raise FileNotFoundError(f"No index at {index_dir}")
    chunks = [Document(**c) for c in json.loads(chunks_file.read_text(encoding="utf-8"))]
    vector_store = InMemoryVectorStore.load(str(index_dir / "vectors.json"), embeddings)
    return HybridRetriever(chunks, vector_store, rrf_k)


def main() -> None:
    from app.llm import PROVIDER_ERRORS, ProviderError, get_embeddings

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    docs_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else settings.docs_dir
    try:
        build_index(docs_dir, settings.index_dir, get_embeddings())
    except (ProviderError, FileNotFoundError, *PROVIDER_ERRORS) as exc:
        logger.error("Ingest failed: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
