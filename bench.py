#!/usr/bin/env python3
"""
bench.py — Script chạy đánh giá (Benchmark) 5 câu hỏi truy xuất cho Lab 07.
Được chuẩn bị bởi: R2 · Benchmark Lead
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from src.agent import KnowledgeBaseAgent
from src.chunking import FixedSizeChunker, RecursiveChunker, SentenceChunker
from src.embeddings import _mock_embed
from src.models import Document
from src.store import EmbeddingStore

# ==============================================================================
# 1. BỘ 5 CÂU HỎI ĐÁNH GIÁ VÀ CÂU TRẢ LỜI CHUẨN (GOLD ANSWERS)
# ==============================================================================
BENCHMARK_QUERIES = [
    {
        "id": 1,
        "query": "Sinh viên được mượn tối đa bao nhiêu tài liệu về nhà và thời hạn mượn sách tham khảo tiếng Việt, ngoại văn là bao lâu?",
        "gold_answer": "Sinh viên được mượn tối đa 10 tài liệu cùng lúc về nhà; sách tiếng Việt mượn 7 ngày; sách ngoại văn và song ngữ mượn 14 ngày.",
        "key_phrases": ["10", "7 ngày", "14 ngày"],
        "metadata_filter": None,
    },
    {
        "id": 2,
        "query": "Hạn ngạch được phép mượn tài liệu về nhà tối đa là bao nhiêu cuốn cùng một lúc?",
        "gold_answer": "10 tài liệu đối với sinh viên (nếu là cán bộ giảng viên thì được mượn tối đa 20 tài liệu).",
        "key_phrases": ["10", "sinh viên"],
        "metadata_filter": {"audience": "student"},
    },
    {
        "id": 3,
        "query": "Mức phí phạt trả sách quá hạn mỗi ngày là bao nhiêu và có những phương thức thanh toán trực tuyến nào?",
        "gold_answer": "Phí phạt quá hạn là 5.000 VNĐ / tài liệu / ngày; có 2 phương thức thanh toán trực tuyến: qua ví FAP và qua cổng DNG (quét mã QR ngân hàng).",
        "key_phrases": ["5.000", "FAP", "DNG"],
        "metadata_filter": None,
    },
    {
        "id": 4,
        "query": "Thời gian sử dụng phòng học nhóm tối đa là bao lâu mỗi ca và sau bao nhiêu phút không đến nhận phòng thì ca đặt sẽ bị hủy?",
        "gold_answer": "Thời gian sử dụng tối đa 2 giờ / ca (1 ca / nhóm / ngày); sau 15 phút kể từ giờ bắt đầu nếu nhóm không đến nhận phòng hoặc không đủ người tối thiểu thì ca đặt sẽ tự động bị hủy.",
        "key_phrases": ["2 giờ", "15 phút"],
        "metadata_filter": None,
    },
    {
        "id": 5,
        "query": "Mỗi cuốn sách được phép gia hạn tối đa mấy lượt và bạn đọc có thể thực hiện gia hạn qua những kênh nào?",
        "gold_answer": "Mỗi cuốn sách được phép gia hạn tối đa 4 lượt (nếu chưa có người đặt trước); gia hạn qua 4 kênh: cổng OPAC trực tuyến, gửi email, gọi điện thoại (024 6680 5912), hoặc nhắn tin qua Fanpage Thư viện FPTU.",
        "key_phrases": ["4 lượt", "OPAC", "024 6680 5912", "Fanpage"],
        "metadata_filter": None,
    },
]


def load_corpus_and_chunk(data_dir: Path, chunker) -> list[Document]:
    """
    Đọc tất cả các file .md trong thư mục dữ liệu, tách frontmatter và chunking.
    Mỗi chunk được đóng gói thành 1 Document có metadata chứa doc_id gốc.
    """
    documents: list[Document] = []
    md_files = sorted(data_dir.glob("*.md"))

    if not md_files:
        # Tìm trong các thư mục con (ví dụ data/university/)
        md_files = sorted(data_dir.rglob("*.md"))

    for p in md_files:
        raw_text = p.read_text(encoding="utf-8")
        if "---" in raw_text:
            parts = raw_text.split("---", 2)
            fm_raw = parts[1]
            body = parts[2].strip() if len(parts) > 2 else ""
            fm = dict(re.findall(r"^(\w+):\s*(.+)$", fm_raw, re.M))
        else:
            fm = {}
            body = raw_text.strip()

        chunks = chunker.chunk(body)
        for idx, chunk in enumerate(chunks):
            chunk_doc = Document(
                id=f"{p.stem}#{idx}",
                content=chunk,
                metadata={
                    **fm,
                    "doc_id": fm.get("doc_id", p.stem),
                    "chunk_index": idx,
                    "source_file": p.name,
                },
            )
            documents.append(chunk_doc)

    return documents


def run_benchmark(
    data_dir: Path = Path("data/university"),
    output_file: Path = Path("ket_qua_benchmark.txt"),
) -> None:
    print("==================================================")
    print("      LAB 07 — RETRIEVAL STRATEGY BENCHMARK       ")
    print("==================================================")

    # CHIẾN LƯỢC CẢI TIẾN: RecursiveChunker tối ưu cho Markdown
    # - chunk_size=600: bảo toàn toàn bộ một điều khoản quy chế (tránh cắt đôi bảng số liệu)
    # - separators: ưu tiên tách theo đề mục Markdown [##, ###] trước khi tách xuống đoạn và câu
    chunker = RecursiveChunker(
        separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " ", ""],
        chunk_size=600,
    )

    print(f"Chiến lược sử dụng: {chunker.__class__.__name__}")
    print(f"Thư mục dữ liệu: {data_dir}")

    docs = load_corpus_and_chunk(data_dir, chunker)
    print(f"Tổng số chunks đã nạp: {len(docs)}")

    store = EmbeddingStore(collection_name="benchmark_store", embedding_fn=_mock_embed)
    store.add_documents(docs)

    output_lines: list[str] = []
    output_lines.append(f"BENCHMARK RESULTS — Chiến lược: {chunker.__class__.__name__}")
    output_lines.append(f"Số lượng chunks: {len(docs)}\n")

    total_score = 0
    for item in BENCHMARK_QUERIES:
        q_id = item["id"]
        query = item["query"]
        gold = item["gold_answer"]
        flt = item["metadata_filter"]
        keys = item["key_phrases"]

        results = store.search_with_filter(query, top_k=3, metadata_filter=flt)

        print(f"\n--- Câu {q_id}: {query}")
        if flt:
            print(f"    [Có Filter: {flt}]")
        print(f"    Gold Answer: {gold}")

        output_lines.append(f"Câu hỏi {q_id}: {query}")
        output_lines.append(f"Filter: {flt}")
        output_lines.append(f"Gold Answer: {gold}")

        hit = False
        for rank, res in enumerate(results, start=1):
            content = res.get("content", "").replace("\n", " ")
            score = res.get("score", 0.0)
            doc_id = res.get("metadata", {}).get("doc_id", res.get("id"))
            has_key = any(k.lower() in content.lower() for k in keys)

            line = f"  Top-{rank} (Score: {score:.4f}, Doc: {doc_id}): {content[:100]}..."
            print(line)
            output_lines.append(line)

            if has_key and not hit:
                hit = True

        point = 2 if hit else 0
        total_score += point
        print(f"    -> Đánh giá: {'ĐẠT (chứa đáp án chuẩn)' if hit else 'CHƯA ĐẠT'} [{point}/2 điểm]")
        output_lines.append(f"Kết quả: {'ĐẠT' if hit else 'CHƯA ĐẠT'} [{point}/2 điểm]\n")

    summary = f"\nTổng điểm Benchmark: {total_score} / 10 điểm"
    print(summary)
    output_lines.append(summary)

    output_file.write_text("\n".join(output_lines), encoding="utf-8")
    print(f"\nĐã lưu kết quả chi tiết vào: {output_file}")


if __name__ == "__main__":
    run_benchmark()

