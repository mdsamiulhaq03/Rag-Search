import hashlib
import re

import pytest
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import FakeListChatModel

# Words that should land near each other in "semantic" space for the fake embedder.
SYNONYMS = {"vacation": "leave", "holiday": "leave", "laptop": "device"}
FAKE_ANSWER = "Answer from context [1]."


def fake_embed(text: str, dim: int = 64) -> list[float]:
    """Deterministic bag-of-words hashing embedding with a tiny synonym map."""
    vec = [0.0] * dim
    for word in re.findall(r"[a-z]+", text.lower()):
        word = SYNONYMS.get(word, word)
        vec[int(hashlib.md5(word.encode()).hexdigest(), 16) % dim] += 1.0
    return vec


class FakeEmbeddings(Embeddings):
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [fake_embed(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return fake_embed(text)


@pytest.fixture
def embeddings():
    return FakeEmbeddings()


@pytest.fixture
def chat_model():
    return FakeListChatModel(responses=[FAKE_ANSWER])


def make_chunk(cid: str, source: str, heading: str, text: str) -> Document:
    return Document(id=cid, page_content=text, metadata={"id": cid, "source": source, "heading": heading})


@pytest.fixture
def chunks():
    return [
        make_chunk("a", "expense.md", "EXP-204", "EXP-204: Hotels are capped at USD 180 per night."),
        make_chunk("b", "hr.md", "Annual Leave", "Employees accrue 20 days of annual leave."),
        make_chunk("c", "it.md", "Lost Devices", "Report a lost laptop to the helpdesk."),
    ]
