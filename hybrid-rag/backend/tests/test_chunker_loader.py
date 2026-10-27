import pytest
from langchain_core.documents import Document

from app.chunker import chunk_document, chunk_documents
from app.loader import load_documents


def doc(text: str, source: str = "a.md") -> Document:
    return Document(page_content=text, metadata={"source": source})


def test_splits_by_heading_and_keeps_deepest_heading():
    chunks = chunk_document(doc("intro text\n# First\nalpha beta\n## Second\ngamma"), size=200, overlap=20)
    assert [c.metadata["heading"] for c in chunks] == ["", "First", "Second"]
    assert "alpha beta" in chunks[1].page_content
    assert "# First" in chunks[1].page_content  # heading kept for BM25


def test_long_section_is_windowed():
    text = " ".join(f"word{i}" for i in range(200))
    chunks = chunk_document(doc(text), size=100, overlap=20)
    assert len(chunks) > 1
    assert all(len(c.page_content) <= 100 for c in chunks)
    assert chunks[-1].page_content.endswith("word199")  # nothing dropped


def test_chunk_ids_are_stable_unique_and_in_metadata():
    d = doc("# A\none\n# B\ntwo")
    first, second = chunk_document(d, 100, 10), chunk_document(d, 100, 10)
    assert [c.id for c in first] == [c.id for c in second]
    assert len({c.id for c in first}) == len(first)
    assert all(c.metadata["id"] == c.id and c.metadata["source"] == "a.md" for c in first)


@pytest.mark.parametrize("size,overlap", [(0, 0), (10, 10), (10, -1)])
def test_invalid_chunk_params(size, overlap):
    with pytest.raises(ValueError):
        chunk_document(doc("x"), size, overlap)


def test_loader_reads_md_and_txt_only(tmp_path):
    (tmp_path / "a.md").write_text("# A\nhello", encoding="utf-8")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.txt").write_text("world", encoding="utf-8")
    (tmp_path / "c.pdf").write_text("ignored", encoding="utf-8")
    docs = load_documents(tmp_path)
    assert [d.metadata["source"] for d in docs] == ["a.md", "sub/b.txt"]
    assert len(chunk_documents(docs, 100, 10)) == 2


def test_loader_missing_dir(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_documents(tmp_path / "nope")
