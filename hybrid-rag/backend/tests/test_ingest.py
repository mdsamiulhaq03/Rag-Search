import sys

import pytest

from app import ingest, llm
from app.config import BASE_DIR
from app.llm import ProviderError
from app.retrieval import Mode


def test_build_and_load_index(tmp_path, embeddings):
    built = ingest.build_index(BASE_DIR / "docs", tmp_path, embeddings)
    loaded = ingest.load_index(tmp_path, embeddings)
    assert len(loaded.chunks) == len(built.chunks) > 5
    assert loaded.search("EXP-204", 1, Mode.BM25)[0].doc.metadata["source"] == "expense-policy.md"
    assert loaded.search("EXP-204", 1, Mode.VECTOR)  # vectors restored without re-embedding


def test_load_index_missing(tmp_path, embeddings):
    with pytest.raises(FileNotFoundError):
        ingest.load_index(tmp_path, embeddings)


def test_main_exits_without_api_key(monkeypatch):
    monkeypatch.setattr(llm, "settings", llm.settings.__class__(google_api_key=""))
    monkeypatch.setattr(sys, "argv", ["ingest", str(BASE_DIR / "docs")])
    with pytest.raises(SystemExit) as exc:
        ingest.main()
    assert exc.value.code == 1


def test_missing_key_raises_provider_error(monkeypatch):
    monkeypatch.setattr(llm, "settings", llm.settings.__class__(google_api_key=""))
    with pytest.raises(ProviderError, match="GOOGLE_API_KEY"):
        llm.get_chat_model()


def test_models_built_with_key(monkeypatch):
    monkeypatch.setattr(llm, "settings", llm.settings.__class__(google_api_key="test-key"))
    assert llm.get_chat_model().model.endswith("gemini-3.5-flash-lite")
    assert "gemini-embedding" in llm.get_embeddings().model
