# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store
# BÁO CÁO LAB 07 - NHÓM 18
*Chủ đề: Dịch vụ & Nội quy Thư viện Đại học FPT (FPT University Library Services & Regulations)*

**Nhóm:** Nhóm 18 (Lớp K4-L3A - Đại học FPT)  
**Thành viên phụ trách:**
- **Tuấn** (R1 · Data Lead)
- **Khánh — Nguyễn Nam Khánh** (R2 · Benchmark Lead)
- **Vĩ** (R3 · Strategy Lead)
- **Nhật** (R4 · Report & Demo Lead)  
**Ngày:** 2026-09-19

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Dịch vụ và Quy định Thư viện Đại học FPT (FPT University Library Services & Regulations)

**Tại sao nhóm chọn chủ đề này?**
> Nhóm chọn chủ đề Dịch vụ và Quy chế Thư viện vì đây là nghiệp vụ cốt lõi, gắn liền với toàn bộ sinh viên và cán bộ giảng viên trong trường. Văn bản quy định có cấu trúc phân cấp điều khoản rõ ràng, nhiều mốc số liệu định lượng cụ thể (hạn mượn, số lượt gia hạn, phí phạt quá hạn) và có sự phân hóa đối tượng (`audience`: `student` vs `faculty`), rất lý tưởng để thực nghiệm, so sánh các chiến lược chia nhỏ (chunking) và kiểm chứng hiệu quả của việc lọc trước bằng metadata (metadata pre-filtering).

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Quy định mượn trả tài liệu cho sinh viên | https://library.fpt.edu.vn/Pages/Index/9 | 2026-09-19 / 2021-05-14 | 2.020 | `doc_id`, `audience: student`, `category: circulation`, `department: library` |
| 2 | Chính sách mượn trả tài liệu cho CBGV | https://library.fpt.edu.vn/Pages/Index/9 | 2026-09-19 / 2021-05-14 | 1.714 | `doc_id`, `audience: faculty`, `category: circulation`, `department: library` |
| 3 | Quy định phí thư viện & thanh toán quá hạn | https://library.fpt.edu.vn/Pages/Index/18 | 2026-09-19 / 2024-04-12 | 1.922 | `doc_id`, `audience: student`, `category: finance`, `department: library` |
| 4 | Quy định đặt & sử dụng phòng học nhóm | https://library.fpt.edu.vn/Pages/Index/17 | 2026-09-19 / 2023-09-22 | 1.908 | `doc_id`, `audience: student`, `category: facility`, `department: library` |
| 5 | Hướng dẫn các phương thức gia hạn sách | https://library.fpt.edu.vn/Pages/Index/1 | 2026-09-19 / 2021-05-14 | 2.019 | `doc_id`, `audience: all`, `category: services`, `department: library` |
| 6 | Thời gian hoạt động & lịch phục vụ mượn trả | https://library.fpt.edu.vn/Pages/Index/3 | 2026-09-19 / 2021-05-14 | 1.465 | `doc_id`, `audience: all`, `category: general`, `department: library` |
| 7 | Nội quy chung bạn đọc tại Thư viện | https://library.fpt.edu.vn/Pages/Index/15 | 2026-09-19 / 2022-12-12 | 2.095 | `doc_id`, `audience: all`, `category: policy`, `department: library` |
| 8 | Chính sách tiếp cận tài nguyên số FPTU | https://library.fpt.edu.vn/Pages/Index/22 | 2026-09-19 / 2025-09-29 | 1.894 | `doc_id`, `audience: all`, `category: digital`, `department: library` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | string | `fpt-muon-sach-sinh-vien` | Định danh duy nhất file gốc, phục vụ truy vết nguồn và hàm `delete_document` |
| `audience` | string | `student`, `faculty`, `all` | Phân tách đối tượng bạn đọc, bắt buộc dùng cho pre-filtering tránh trả về sai hạn mức |
| `category` | string | `circulation`, `finance`, `facility` | Thu hẹp không gian tìm kiếm theo nhóm dịch vụ chuyên biệt (mượn trả, phí, phòng học) |
| `department` | string | `library` | Phân định đơn vị quản lý nghiệp vụ trong cơ sở dữ liệu học vụ toàn trường |
| `source_url` | string | `https://library.fpt.edu.vn/...` | Cung cấp liên kết gốc để người dùng và agent kiểm chứng độ xác thực (source provenance) |
| `document_version` | string | `2024-04-12` | Xác định độ mới và tính hiệu lực của chính sách |

---

## 2. Thiết kế chiến lược & Đánh giá phân rã văn bản (15 điểm)

Để tối ưu hóa Vector Store, nhóm đã tiến hành phân rã bộ tài liệu gốc bằng 4 chiến lược khác nhau:

### Bảng Phân Tích So Sánh Chiến Lược Của 4 Thành Viên

| Thành viên phụ trách | Tên Chiến lược | Số lượng Chunk sinh ra | Điểm Benchmark | Đánh giá & Nhận xét sơ bộ |
|---|---|:---:|:---:|---|
| **Tuấn (Data)** | `SentenceChunker` | 48 | **6/10** | Cắt theo từng câu nên số lượng chunk sinh ra nhiều nhất. Tuy nhiên, ngữ cảnh bị vỡ vụn, thường xuyên làm mất từ khóa nối câu khiến điểm truy xuất thấp nhất. |
| **Nhật (Report)** | `FixedSizeChunker` | 14 | **4/10** | Cắt cứng theo số lượng ký tự (150 char). Ưu điểm là rất ít chunk, nhưng nhược điểm là đoạn văn bị chẻ đôi giữa chừng một cách máy móc. Câu 4 và 5 bị cắt đứt đoạn chứa Keyword quan trọng nên lấy sai hoàn toàn. |
| **Khánh (Benchmark)** | `RecursiveChunker` | 31 | **8/10** | Cắt đệ quy rất linh hoạt (chunk_size=600, ưu tiên phân tách Markdown), dung hòa tốt giữa số lượng chunk và ngữ cảnh. Lấy được điểm tuyệt đối ở 4/5 câu hỏi. |
| **Vĩ (Strategy)** | `HeadingChunker` | 32 | **9/10** | **Chiến lược xuất sắc nhất.** Tự động cắt theo các thẻ `#` và `##` của Markdown, giúp giữ trọn vẹn 100% ngữ cảnh của một "Điều luật" hay một "Quy định" vào chung một chunk. |

### Chi Tiết Chiến Lược Của Từng Thành Viên

**1. Tuấn (Data) — `SentenceChunker`**
- **Loại chiến lược:** SentenceChunker (`max_sentences_per_chunk=3`)
- **Mô tả:** Tách theo ranh giới câu bằng Regex lookbehind `(?<=[.!?])\s+`.
- **Code snippet:**
```python
from src.chunking import SentenceChunker
chunker = SentenceChunker(max_sentences_per_chunk=3)
chunks = chunker.chunk(document_body)
```

**2. Nhật (Report) — `FixedSizeChunker`**
- **Loại chiến lược:** FixedSizeChunker (`chunk_size=150, overlap=30`)
- **Mô tả:** Cắt cố định 150 ký tự với cửa sổ trượt.
- **Code snippet:**
```python
from src.chunking import FixedSizeChunker
chunker = FixedSizeChunker(chunk_size=150, overlap=30)
chunks = chunker.chunk(document_body)
```

**3. Khánh (Benchmark) — `RecursiveChunker`**
- **Loại chiến lược:** RecursiveChunker cải tiến (`chunk_size=600`)
- **Mô tả:** Tách đệ quy đa tầng với danh sách ưu tiên `["\n## ", "\n### ", "\n\n", "\n", ". ", " "]`, dung hòa hoàn hảo giữa độ dài chunk và ranh giới đề mục Markdown.
- **Code snippet:**
```python
from src.chunking import RecursiveChunker
chunker = RecursiveChunker(
    separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " ", ""],
    chunk_size=600,
)
chunks = chunker.chunk(document_body)
```

**4. Vĩ (Strategy) — `HeadingChunker`**
- **Loại chiến lược:** HeadingChunker (Custom Markdown Header Splitter)
- **Mô tả:** Tự động cắt theo các thẻ `#`, `##`, `###` của Markdown, giữ trọn vẹn 100% một điều khoản quy định vào một chunk.
- **Code snippet:**
```python
import re

class HeadingChunker:
    """Tự động phân rã văn bản theo thẻ tiêu đề Markdown."""
    def chunk(self, text: str) -> list[str]:
        sections = re.split(r'(?=\n#{1,3}\s)', text.strip())
        return [s.strip() for s in sections if s.strip()]
```

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> **HeadingChunker** (và **RecursiveChunker**) là chiến lược xuất sắc nhất cho bộ tài liệu Quy định & Dịch vụ Thư viện FPT. Lý do vì văn bản pháp quy được soạn thảo theo từng điều khoản rõ ràng; việc giữ nguyên vẹn văn bản từ thẻ Header này đến thẻ Header tiếp theo giúp Vector Store bảo toàn 100% ngữ cảnh logic và các cặp số liệu ràng buộc (như "2 giờ" đi liền với "hủy sau 15 phút"), không bị xé vụn như SentenceChunker hay FixedSizeChunker.

---

## 3. Câu hỏi đánh giá & Kết quả Benchmark (10 điểm)

Nhóm sử dụng bộ 5 câu hỏi chuẩn để kiểm thử hệ thống. Điểm số dưới đây lấy từ chiến lược tốt nhất (`HeadingChunker` của Vĩ):

| # | Loại câu hỏi | Câu hỏi đánh giá (Query) | Câu trả lời chuẩn (Gold Answer) | Kết quả truy xuất thực tế | Điểm |
|:---:|---|---|---|---|:---:|
| **1** | Fact & Numbers | Sinh viên được mượn tối đa bao nhiêu tài liệu về nhà và thời hạn mượn sách tham khảo tiếng Việt, ngoại văn là bao lâu? | Sinh viên được mượn tối đa 10 tài liệu cùng lúc về nhà; sách tiếng Việt mượn 7 ngày; sách ngoại văn và song ngữ mượn 14 ngày. | Đạt đúng ý nhưng top-1 bị nhầm lẫn nhẹ sang quy định của giảng viên do không có filter | **1 / 2đ** |
| **2** | Conditions | *(Cần Filter)* Hạn ngạch được phép mượn tài liệu về nhà tối đa là bao nhiêu cuốn cùng một lúc? | 10 tài liệu đối với sinh viên (nếu là cán bộ giảng viên thì được mượn tối đa 20 tài liệu). | Đạt 2/2 điểm tuyệt đối nhờ sử dụng Metadata Filter `{"audience": "student"}` | **2 / 2đ** |
| **3** | Finance | Mức phí phạt trả sách quá hạn mỗi ngày là bao nhiêu và có những phương thức thanh toán trực tuyến nào? | Phí phạt quá hạn là 5.000 VNĐ / tài liệu / ngày; có 2 phương thức thanh toán: qua ví FAP và qua cổng DNG. | Bốc chính xác tài liệu `fpt-phi-thu-vien` ở Top-1 | **2 / 2đ** |
| **4** | Facility | Thời gian sử dụng phòng học nhóm tối đa là bao lâu mỗi ca và sau bao nhiêu phút không đến nhận phòng thì ca đặt sẽ bị hủy? | Thời gian sử dụng tối đa 2 giờ / ca (1 ca / nhóm / ngày); sau 15 phút không đến nhận phòng sẽ tự động bị hủy. | Trích xuất đúng con số `2 giờ` và `15 phút` trong cùng một chunk | **2 / 2đ** |
| **5** | Channels | Mỗi cuốn sách được phép gia hạn tối đa mấy lượt và bạn đọc có thể thực hiện gia hạn qua những kênh nào? | Mỗi cuốn sách được phép gia hạn tối đa 4 lượt; gia hạn qua 4 kênh: cổng OPAC, gửi email, gọi điện thoại, Fanpage. | Trích xuất đầy đủ 4 lượt và 4 kênh gia hạn linh hoạt | **2 / 2đ** |

👉 **Tổng điểm hệ thống: 9 / 10 điểm.**

---

### Bằng Chứng Thực Nghiệm A/B: Metadata Filtering
*(Chứng minh sự cần thiết của lọc siêu dữ liệu trong kiến trúc Multi-tenant)*

**Câu hỏi Test:** *"Hạn ngạch được phép mượn tài liệu về nhà tối đa là bao nhiêu cuốn cùng một lúc?"*

* **TRƯỜNG HỢP 1: KHÔNG SỬ DỤNG FILTER**
  * Vector Store lấy về cả tài liệu `fpt-muon-sach-sinh-vien` (10 cuốn) và `fpt-muon-sach-giang-vien` (20 cuốn).
  * Tài liệu của giảng viên nằm chễm chệ ở Rank 2 với score khá cao (**0.275**). Nếu đưa kết quả này cho LLM, chắc chắn LLM sẽ bị ảo giác (hallucination) và trả lời sai thành 20 cuốn.
* **TRƯỜNG HỢP 2: CÓ SỬ DỤNG FILTER `{"audience": "student"}`**
  * Vector Store loại bỏ hoàn toàn tài liệu của giảng viên từ trước khi tính toán cosine similarity.
  * Hệ thống cô lập 100% dữ liệu, lấy về đúng tài liệu sinh viên (Score: **0.395**).

**💡 Kết luận:** Bắt buộc phải triển khai tính năng Metadata Filtering để đảm bảo an toàn thông tin và tính chính xác, không cho phép sinh viên đọc chéo quy định của giảng viên.

---

## 4. Phân Tích Lỗi (Failure Case Analysis) & Bài Học Demo (5 điểm)

### Phân Tích Lỗi Thực Tế (Failure Case Analysis)

Nhóm đã phát hiện một rủi ro kiến trúc vô cùng lớn khi sử dụng `SentenceChunker` (Thuật toán của Tuấn).

**1. Hiện tượng lỗi:**
Khi hỏi Câu 3: *"Mức phí phạt trả sách quá hạn mỗi ngày là bao nhiêu?"*, chiến lược `SentenceChunker` đạt 0/2 điểm. Top-1 truy xuất trả về một câu hoàn toàn không liên quan: *"Tài khoản thư viện của bạn đọc không trong tình trạng bị khóa hoặc vi phạm nội quy."*

**2. Nguyên nhân (Root Cause):**
Do thuật toán `SentenceChunker` băm văn bản quá nhuyễn (cắt theo từng dấu chấm câu). Câu văn chứa con số "5.000 VNĐ" bị tách rời hoàn toàn khỏi câu văn chứa chữ "Mức phí phạt quá hạn". Khi Vector Store tính khoảng cách ngữ nghĩa, từng câu đơn lẻ không đủ từ khóa ngữ cảnh, dẫn đến Vector bị lạc hướng và nhặt sai tài liệu.

**3. Giải pháp khắc phục:**
Tuyệt đối không dùng SentenceChunker cho các tài liệu dạng Pháp luật / Nội quy vì nó phá vỡ tính liên kết của một "Điều khoản". Phải sử dụng `HeadingChunker` hoặc `RecursiveChunker` tối ưu (giữ nguyên văn bản từ thẻ Header này đến thẻ Header tiếp theo) để gom trọn vẹn ngữ cảnh vào một Vector duy nhất.

### Kịch Bản Thuyết Trình Demo (6–8 phút)
1. **Chủ đề & Bộ tài liệu (1 phút - Tuấn):** Giới thiệu 8 tài liệu quy chế Thư viện FPT, tính minh bạch nguồn và cấu trúc metadata schema.
2. **Chiến lược từng thành viên (2 phút - Nhật & Khánh):** Trình bày sự đối lập giữa FixedSize (cắt cứng) vs Recursive/Heading (tách phân cấp).
3. **So sánh & A/B Metadata Filter (3 phút - Vĩ):** Trình bày bảng so sánh điểm (4 -> 6 -> 8 -> 9/10) và demo case A/B loại trừ tài liệu giảng viên.
4. **Demo trực tiếp & Hỏi đáp (2 phút - Khánh):** Chạy `python bench.py` trực tiếp trên terminal.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|:----------------:|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) & Phân tích lỗi | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |
