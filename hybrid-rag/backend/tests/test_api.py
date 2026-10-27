import shutil

import pytest
from fastapi.testclient import TestClient
from langchain_core.embeddings import Embeddings
from langchain_google_genai.chat_models import GoogleGenerativeAIError

from app import main
from app.config import BASE_DIR
from app.llm import ProviderError
from tests.conftest import FAKE_ANSWER


@pytest.fixture
def client(tmp_path, chat_model, embeddings):
    docs = tmp_path / "docs"
    shutil.copytree(BASE_DIR / "docs", docs)
    app = main.create_app(chat_model=chat_model, embeddings=embeddings, docs_dir=docs, index_dir=tmp_path / "index")
    return TestClient(app)


def test_health_before_and_after_ingest(client):
    assert client.get("/health").json()["indexed"] is False
    assert client.post("/ingest").json()["chunks"] > 5
    assert client.get("/health").json()["indexed"] is True


def test_documents_lists_indexed_sources(client):
    assert client.get("/documents").json() == []
    client.post("/ingest")
    docs = client.get("/documents").json()
    assert [d["source"] for d in docs] == sorted(d["source"] for d in docs)
    assert {"source": "expense-policy.md", "chunks": 3} in docs


def test_ask_requires_index(client):
    assert client.post("/ask", json={"question": "hi"}).status_code == 409


def test_ask_returns_answer_and_sources(client):
    client.post("/ingest")
    res = client.post("/ask", json={"question": "EXP-204 hotel cap", "mode": "hybrid"})
    body = res.json()
    assert res.status_code == 200
    assert body["answer"] == FAKE_ANSWER
    assert body["sources"][0]["source"] == "expense-policy.md"
    assert set(body["sources"][0]["ranks"]) == {"bm25", "vector"}


@pytest.mark.parametrize("mode", ["bm25", "vector"])
def test_ask_single_mode(client, mode):
    client.post("/ingest")
    sources = client.post("/ask", json={"question": "hotel EXP-204", "mode": mode}).json()["sources"]
    assert all(set(s["ranks"]) == {mode} for s in sources)


@pytest.mark.parametrize("payload", [{"question": ""}, {"question": "x" * 1001}, {"question": "x", "mode": "bad"}])
def test_ask_validation(client, payload):
    assert client.post("/ask", json=payload).status_code == 422


class BrokenEmbeddings(Embeddings):
    def embed_documents(self, texts):
        raise GoogleGenerativeAIError("quota exceeded")

    def embed_query(self, text):
        raise GoogleGenerativeAIError("quota exceeded")


def test_provider_error_returns_503(tmp_path, chat_model):
    app = main.create_app(chat_model=chat_model, embeddings=BrokenEmbeddings(),
                          docs_dir=BASE_DIR / "docs", index_dir=tmp_path / "index")
    res = TestClient(app).post("/ingest")
    assert res.status_code == 503
    assert "quota exceeded" in res.json()["detail"]


def test_missing_api_key_returns_503(tmp_path, monkeypatch):
    def no_key():
        raise ProviderError("GOOGLE_API_KEY is not set.")

    monkeypatch.setattr(main, "get_chat_model", no_key)
    client = TestClient(main.create_app(index_dir=tmp_path / "index"))
    assert client.get("/health").json()["config_error"] == "GOOGLE_API_KEY is not set."
    assert client.post("/ingest").status_code == 503
    assert client.post("/ask", json={"question": "hi"}).status_code == 503


def test_ingest_missing_docs_dir(tmp_path, chat_model, embeddings):
    app = main.create_app(chat_model=chat_model, embeddings=embeddings,
                          docs_dir=tmp_path / "nope", index_dir=tmp_path / "index")
    assert TestClient(app).post("/ingest").status_code == 400
