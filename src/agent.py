from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3, metadata_filter: dict | None = None) -> str:
        if metadata_filter:
            results = self.store.search_with_filter(question, top_k=top_k, metadata_filter=metadata_filter)
        else:
            results = self.store.search(question, top_k=top_k)
        context_parts = [r["content"] for r in results if "content" in r and r["content"]]
        context = "\n\n".join(context_parts)
        prompt = (
            f"Context information is below:\n"
            f"---------------------\n"
            f"{context}\n"
            f"---------------------\n"
            f"Given the context information and not prior knowledge, "
            f"answer the question: {question}\n"
        )
        return self.llm_fn(prompt)
