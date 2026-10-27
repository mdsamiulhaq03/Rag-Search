"""Gemini chat + embedding models via LangChain."""
from google.genai.errors import APIError
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_google_genai.chat_models import GoogleGenerativeAIError

from app.config import settings

PROVIDER_ERRORS = (GoogleGenerativeAIError, APIError)


class ProviderError(RuntimeError):
    """Raised when the model provider is misconfigured or a call fails."""


def _require_key() -> str:
    if not settings.google_api_key:
        raise ProviderError(
            "GOOGLE_API_KEY is not set. Get a free key at https://aistudio.google.com/apikey "
            "and put it in the .env file."
        )
    return settings.google_api_key


def get_chat_model() -> BaseChatModel:
    return ChatGoogleGenerativeAI(
        model=settings.chat_model,
        google_api_key=_require_key(),
        temperature=0,
        timeout=settings.request_timeout,
        max_retries=settings.max_retries,
    )


def get_embeddings() -> Embeddings:
    return GoogleGenerativeAIEmbeddings(model=settings.embed_model, google_api_key=_require_key())
