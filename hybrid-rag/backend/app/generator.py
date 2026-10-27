"""Grounded answer generation as an LCEL chain: prompt | chat model | string parser."""
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.retrieval import SearchHit

NOT_FOUND = "I couldn't find anything about that in the internal docs."

SYSTEM_PROMPT = (
    "You answer questions about internal company documents. "
    "Use ONLY the numbered context passages. Cite passages inline like [1] or [2]. "
    "If the answer is not in the context, say you don't know. Be concise."
)

PROMPT = ChatPromptTemplate.from_messages(
    [("system", SYSTEM_PROMPT), ("human", "Context:\n{context}\n\nQuestion: {question}")]
)


def format_context(hits: list[SearchHit]) -> str:
    def label(hit: SearchHit) -> str:
        heading = hit.doc.metadata.get("heading")
        return hit.doc.metadata["source"] + (f" > {heading}" if heading else "")

    return "\n\n".join(
        f"[{i}] (source: {label(h)})\n{h.doc.page_content}" for i, h in enumerate(hits, start=1)
    )


def generate_answer(question: str, hits: list[SearchHit], chat_model: BaseChatModel) -> str:
    if not hits:
        return NOT_FOUND
    chain = PROMPT | chat_model | StrOutputParser()
    return chain.invoke({"context": format_context(hits), "question": question})
