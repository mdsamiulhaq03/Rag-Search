"""Hybrid retrieval with LangChain: BM25Retriever + vector store, fused by EnsembleRetriever (RRF)."""
import re
from dataclasses import dataclass, field
from enum import Enum

from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore

TOKEN_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
WEIGHTS = (0.5, 0.5)  # bm25, vector

# Filler words that otherwise make BM25 match unrelated passages ("how do I get...").
# Keep in sync with frontend/src/lib/highlight.ts.
STOP_WORDS = frozenset(
    "a an and are as at be by can do does for from get got how i if in is it me my of on or so "
    "the to was we what when where which who why will with you your".split()
)


def tokenize(text: str) -> list[str]:
    """Lowercase alphanumeric tokens minus stop words; keeps codes like 'exp-204' intact."""
    return [t for t in TOKEN_RE.findall(text.lower()) if t not in STOP_WORDS]


class Mode(str, Enum):
    HYBRID = "hybrid"
    BM25 = "bm25"
    VECTOR = "vector"


@dataclass(frozen=True)
class SearchHit:
    doc: Document
    score: float
    ranks: dict[str, int] = field(default_factory=dict)  # retriever name -> 1-based rank


class HybridRetriever:
    def __init__(self, chunks: list[Document], vector_store: InMemoryVectorStore, rrf_k: int = 60):
        self.chunks = list(chunks)
        self.vector_store = vector_store
        self.rrf_k = rrf_k
        self.bm25 = (
            BM25Retriever.from_documents(self.chunks, preprocess_func=tokenize)
            if self.chunks
            else None
        )
        self.ensemble = (
            EnsembleRetriever(
                retrievers=[self.bm25, vector_store.as_retriever()],
                weights=list(WEIGHTS),
                c=rrf_k,
                id_key="id",
            )
            if self.bm25
            else None
        )

    def _bm25_search(self, query: str, n: int) -> list[Document]:
        """BM25Retriever always returns n docs, even with score 0, so drop docs sharing no terms."""
        terms = set(tokenize(query))
        if self.bm25 is None or not terms:
            return []
        self.bm25.k = n
        return [d for d in self.bm25.invoke(query) if terms & set(tokenize(d.page_content))]

    def _vector_search(self, query: str, n: int) -> list[Document]:
        return self.vector_store.similarity_search(query, k=n) if self.chunks else []

    def search(self, query: str, k: int, mode: Mode = Mode.HYBRID) -> list[SearchHit]:
        candidates = k * 3  # retrieve wider before fusing
        lists: dict[str, list[Document]] = {}
        if mode in (Mode.HYBRID, Mode.BM25):
            lists["bm25"] = self._bm25_search(query, candidates)
        if mode in (Mode.HYBRID, Mode.VECTOR):
            lists["vector"] = self._vector_search(query, candidates)

        ranks: dict[str, dict[str, int]] = {}
        for name, docs in lists.items():
            for rank, doc in enumerate(docs, start=1):
                ranks[doc.id] = {**ranks.get(doc.id, {}), name: rank}

        if mode is Mode.HYBRID and self.ensemble:
            ordered = self.ensemble.weighted_reciprocal_rank([lists["bm25"], lists["vector"]])
            weights = dict(zip(("bm25", "vector"), WEIGHTS))
        else:
            ordered = next(iter(lists.values()))
            weights = {name: 1.0 for name in lists}

        return [
            SearchHit(
                doc=doc,
                score=sum(weights[name] / (self.rrf_k + r) for name, r in ranks[doc.id].items()),
                ranks=ranks[doc.id],
            )
            for doc in ordered[:k]
        ]
