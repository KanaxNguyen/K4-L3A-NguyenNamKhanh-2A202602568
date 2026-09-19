from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = max(1, chunk_size)
        self.overlap = max(0, min(overlap, self.chunk_size - 1))

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = max(1, self.chunk_size - self.overlap)
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []
        raw_sentences = [
            s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()
        ]
        if not raw_sentences:
            return []
        chunks: list[str] = []
        step = max(1, self.max_sentences_per_chunk)
        for i in range(0, len(raw_sentences), step):
            group = raw_sentences[i : i + step]
            chunk = " ".join(group).strip()
            if chunk:
                chunks.append(chunk)
        return chunks


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = max(1, chunk_size)

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        return self._split(text, self.separators)

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        if not current_text:
            return []
        if len(current_text) <= self.chunk_size:
            return [current_text]

        if not remaining_separators:
            return [
                current_text[i : i + self.chunk_size]
                for i in range(0, len(current_text), self.chunk_size)
            ]

        sep_idx = -1
        for idx, sep in enumerate(remaining_separators):
            if sep == "" or sep in current_text:
                sep_idx = idx
                break

        if sep_idx == -1:
            return [
                current_text[i : i + self.chunk_size]
                for i in range(0, len(current_text), self.chunk_size)
            ]

        chosen_sep = remaining_separators[sep_idx]
        next_seps = remaining_separators[sep_idx + 1 :]

        if chosen_sep == "":
            return [
                current_text[i : i + self.chunk_size]
                for i in range(0, len(current_text), self.chunk_size)
            ]

        splits = current_text.split(chosen_sep)
        chunks: list[str] = []
        current_pieces: list[str] = []
        current_len = 0

        for piece in splits:
            if not piece:
                continue
            if len(piece) > self.chunk_size:
                if current_pieces:
                    chunks.append(chosen_sep.join(current_pieces))
                    current_pieces = []
                    current_len = 0
                chunks.extend(self._split(piece, next_seps))
            else:
                piece_len = len(piece)
                extra_len = piece_len if not current_pieces else len(chosen_sep) + piece_len
                if current_len + extra_len <= self.chunk_size:
                    current_pieces.append(piece)
                    current_len += extra_len
                else:
                    if current_pieces:
                        chunks.append(chosen_sep.join(current_pieces))
                    current_pieces = [piece]
                    current_len = piece_len

        if current_pieces:
            chunks.append(chosen_sep.join(current_pieces))

        if not chunks:
            return [
                current_text[i : i + self.chunk_size]
                for i in range(0, len(current_text), self.chunk_size)
            ]

        return chunks


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors: (a . b) / (||a|| * ||b||).

    Returns 0.0 if either vector has zero magnitude.
    """
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    if vec_a == vec_b:
        norm_sq = sum(x * x for x in vec_a)
        return 1.0 if norm_sq > 0.0 else 0.0
    dot_prod = sum(x * y for x, y in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(x * x for x in vec_a))
    norm_b = math.sqrt(sum(y * y for y in vec_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    sim = dot_prod / (norm_a * norm_b)
    if math.isnan(sim):
        return 0.0
    if math.isclose(sim, 1.0, abs_tol=1e-9):
        return 1.0
    if math.isclose(sim, -1.0, abs_tol=1e-9):
        return -1.0
    return max(-1.0, min(1.0, sim))


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        chunk_size = max(1, chunk_size)
        fixed_chunker = FixedSizeChunker(
            chunk_size=chunk_size,
            overlap=min(50, max(0, chunk_size // 5)),
        )
        sentence_chunker = SentenceChunker(max_sentences_per_chunk=3)
        recursive_chunker = RecursiveChunker(chunk_size=chunk_size)

        strategies = {
            "fixed_size": fixed_chunker.chunk(text),
            "by_sentences": sentence_chunker.chunk(text),
            "recursive": recursive_chunker.chunk(text),
        }

        results: dict[str, dict] = {}
        for name, chunks in strategies.items():
            count = len(chunks)
            avg_length = sum(len(c) for c in chunks) / count if count > 0 else 0.0
            results[name] = {
                "chunks": chunks,
                "count": count,
                "avg_length": avg_length,
            }
        return results
