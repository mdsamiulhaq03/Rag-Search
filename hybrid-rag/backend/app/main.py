"""FastAPI app: /ask, /ingest and /health (UI lives in ../frontend)."""
import logging
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from fastapi import FastAPI, HTTPException
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel, Field

from app.config import settings
from app.generator import generate_answer
from app.ingest import build_index, load_index
from app.llm import PROVIDER_ERRORS, ProviderError, get_chat_model, get_embeddings
from app.retrieval import HybridRetriever, Mode

logger = logging.getLogger(__name__)


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    mode: Mode = Mode.HYBRID
    top_k: int = Field(default=settings.top_k, ge=1, le=20)


class Source(BaseModel):
    n: int
    source: str
    heading: str
    text: str
    score: float
    ranks: dict[str, int]


class AskResponse(BaseModel):
    answer: str
    mode: Mode
    sources: list[Source]


@dataclass
class AppState:
    chat_model: BaseChatModel | None = None
    embeddings: Embeddings | None = None
    retriever: HybridRetriever | None = None
    config_error: str | None = None


def _provider_unavailable(exc: Exception) -> HTTPException:
    logger.error("Model provider error: %s", exc)
    return HTTPException(status_code=503, detail=f"Model provider error: {exc}")


def create_app(
    chat_model: BaseChatModel | None = None,
    embeddings: Embeddings | None = None,
    docs_dir: Path = settings.docs_dir,
    index_dir: Path = settings.index_dir,
) -> FastAPI:
    app = FastAPI(title="Refer API")
    state = AppState()
    try:
        state.chat_model = chat_model or get_chat_model()
        state.embeddings = embeddings or get_embeddings()
        state.retriever = load_index(index_dir, state.embeddings)
    except ProviderError as exc:
        state.config_error = str(exc)
        logger.warning(state.config_error)
    except FileNotFoundError:
        logger.warning("No index found; call POST /ingest first.")

    def require_config() -> None:
        if state.config_error:
            raise HTTPException(status_code=503, detail=state.config_error)

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok", "indexed": state.retriever is not None, "config_error": state.config_error}

    @app.get("/documents")
    def documents() -> list[dict]:
        """Indexed source files with their chunk counts (named /documents: /docs is Swagger)."""
        if state.retriever is None:
            return []
        counts = Counter(c.metadata["source"] for c in state.retriever.chunks)
        return [{"source": source, "chunks": n} for source, n in sorted(counts.items())]

    @app.post("/ingest")
    def ingest() -> dict:
        require_config()
        try:
            state.retriever = build_index(docs_dir, index_dir, state.embeddings)
        except PROVIDER_ERRORS as exc:
            raise _provider_unavailable(exc) from exc
        except FileNotFoundError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {"chunks": len(state.retriever.chunks)}

    @app.post("/ask", response_model=AskResponse)
    def ask(req: AskRequest) -> AskResponse:
        require_config()
        if state.retriever is None:
            raise HTTPException(status_code=409, detail="No index yet. Run ingest first.")
        try:
            hits = state.retriever.search(req.question, req.top_k, req.mode)
            answer = generate_answer(req.question, hits, state.chat_model)
        except PROVIDER_ERRORS as exc:
            raise _provider_unavailable(exc) from exc
        sources = [
            Source(
                n=i,
                source=h.doc.metadata["source"],
                heading=h.doc.metadata.get("heading", ""),
                text=h.doc.page_content,
                score=round(h.score, 5),
                ranks=h.ranks,
            )
            for i, h in enumerate(hits, start=1)
        ]
        return AskResponse(answer=answer, mode=req.mode, sources=sources)

    return app


app = create_app()
