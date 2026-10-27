"""Runtime settings, overridable via environment variables or a .env file."""
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    chat_model: str = os.getenv("CHAT_MODEL", "gemini-3.5-flash-lite")
    embed_model: str = os.getenv("EMBED_MODEL", "models/gemini-embedding-001")
    request_timeout: float = float(os.getenv("REQUEST_TIMEOUT", "30"))  # seconds per model call
    max_retries: int = int(os.getenv("MAX_RETRIES", "2"))
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "800"))  # characters per chunk
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "100"))
    top_k: int = int(os.getenv("TOP_K", "5"))
    rrf_k: int = int(os.getenv("RRF_K", "60"))
    docs_dir: Path = Path(os.getenv("DOCS_DIR", str(BASE_DIR / "docs")))
    index_dir: Path = Path(os.getenv("INDEX_DIR", str(BASE_DIR / "index")))


settings = Settings()
