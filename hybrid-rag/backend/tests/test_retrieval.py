import pytest
from langchain_core.vectorstores import InMemoryVectorStore

from app.generator import NOT_FOUND, format_context, generate_answer
from app.retrieval import HybridRetriever, Mode, SearchHit, tokenize
from tests.conftest import FAKE_ANSWER


@pytest.fixture
def retriever(chunks, embeddings):
    store = InMemoryVectorStore(embeddings)
    store.add_documents(chunks)
    return HybridRetriever(chunks, store, rrf_k=60)


def test_tokenize_keeps_codes_and_drops_stop_words():
    assert tokenize("What is EXP-204, really?") == ["exp-204", "really"]


def test_bm25_ignores_filler_words(retriever):
    # "how", "do", "get" appear nowhere useful; only real terms may match
    assert retriever.search("how do I get vacation", 3, Mode.BM25) == []


def test_bm25_finds_exact_code(retriever):
    hits = retriever.search("EXP-204", 3, Mode.BM25)
    assert [h.doc.id for h in hits] == ["a"]  # non-matching docs are dropped
    assert hits[0].ranks == {"bm25": 1}
    assert hits[0].score == pytest.approx(1 / 61)


def test_bm25_no_overlap_returns_nothing(retriever):
    assert retriever.search("vacation", 3, Mode.BM25) == []
    assert retriever.search("!!!", 3, Mode.BM25) == []


def test_vector_finds_paraphrase(retriever):
    # no shared keyword with the "annual leave" chunk, but synonyms match in embedding space
    assert retriever.search("vacation", 1, Mode.VECTOR)[0].doc.id == "b"


def test_hybrid_fuses_with_rrf(retriever):
    hits = retriever.search("EXP-204 hotel", 3, Mode.HYBRID)
    top = hits[0]
    assert top.doc.id == "a"
    assert set(top.ranks) == {"bm25", "vector"}
    assert top.score == pytest.approx(sum(0.5 / (60 + r) for r in top.ranks.values()))
    assert [h.score for h in hits] == sorted((h.score for h in hits), reverse=True)


def test_empty_corpus(embeddings):
    empty = HybridRetriever([], InMemoryVectorStore(embeddings))
    assert empty.search("anything", 3, Mode.HYBRID) == []
    assert empty.search("anything", 3, Mode.VECTOR) == []


def test_generator_not_found_skips_llm(chat_model):
    assert generate_answer("q", [], chat_model) == NOT_FOUND


def test_generator_runs_chain(chunks, chat_model):
    assert generate_answer("q", [SearchHit(chunks[0], 0.1)], chat_model) == FAKE_ANSWER


def test_format_context_numbers_passages(chunks):
    context = format_context([SearchHit(chunks[0], 0.1), SearchHit(chunks[1], 0.05)])
    assert "[1] (source: expense.md > EXP-204)" in context
    assert "[2] (source: hr.md > Annual Leave)" in context
