# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Nhóm K4-L3A (Đại học FPT)
**Thành viên:** Nguyễn Thái Dương (R2 · Benchmark Lead), Thành viên 1 (R1 · Data Lead), Thành viên 3 (R3 · Strategy Lead)
**Ngày:** 2026-09-19

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

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

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 3 tài liệu quy chế cốt lõi:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `fpt-muon-sach-sinh-vien.md` | FixedSizeChunker (`fixed_size`) | 13 | 192.3 ký tự | Kém — cắt ngang câu văn và chia đôi điều khoản số liệu |
| `fpt-muon-sach-sinh-vien.md` | SentenceChunker (`by_sentences`) | 8 | 251.0 ký tự | Khá — bảo toàn câu nhưng gộp các ý khác đề mục markdown |
| `fpt-muon-sach-sinh-vien.md` | RecursiveChunker (`recursive`) | 15 | 133.2 ký tự | Rất tốt — giữ trọn cấu trúc đoạn (`\n\n`) và ranh giới đề mục |
| `fpt-phi-thu-vien.md` | FixedSizeChunker (`fixed_size`) | 12 | 196.8 ký tự | Kém — ngắt ngang bảng phí và tên cổng thanh toán |
| `fpt-phi-thu-vien.md` | SentenceChunker (`by_sentences`) | 7 | 272.4 ký tự | Khá — giữ nguyên câu mô tả phí |
| `fpt-phi-thu-vien.md` | RecursiveChunker (`recursive`) | 15 | 126.7 ký tự | Tốt — phân tách mạch lạc giữa các mức phí và cách nộp |
| `fpt-phong-hoc-nhom.md` | FixedSizeChunker (`fixed_size`) | 12 | 195.7 ký tự | Kém — cắt rời quy định giờ ca và điều kiện hủy phòng |
| `fpt-phong-hoc-nhom.md` | SentenceChunker (`by_sentences`) | 7 | 270.4 ký tự | Khá — câu văn độc lập nhưng thiếu tiêu đề mục đi kèm |
| `fpt-phong-hoc-nhom.md` | RecursiveChunker (`recursive`) | 14 | 134.9 ký tự | Rất tốt — bám sát từng quy định và chế tài phòng học |

### Chiến lược của từng thành viên

**Thành viên 1 — Nguyễn Thái Dương (yangtai2504)**
- **Loại chiến lược:** RecursiveChunker cải tiến (Tách đệ quy bám sát Markdown với `chunk_size=600` & Header Injection)
- **Mô tả & lý do chọn cho chủ đề này:** Chiến lược này nâng cấp cơ chế chia để trị đệ quy: (1) Tăng `chunk_size` từ 300 lên 600 để giữ trọn vẹn toàn bộ một điều khoản quy chế pháp quy (không bị xé đôi bảng biểu hay cặp số liệu '2 giờ' và '15 phút' như ở phòng học nhóm); (2) Tùy biến thứ tự separators ưu tiên thẻ tiêu đề Markdown `["\n## ", "\n### ", "\n\n", "\n", ". ", " ", ""]`; (3) Kết hợp kỹ thuật Header Injection (`[{title}]\n{chunk}`) bơm ngữ cảnh nguồn vào từng chunk con, giúp điểm số benchmark tăng vọt từ 4/10 lên 8/10.
- **Code snippet sử dụng:**
```python
from src.chunking import RecursiveChunker

# Khởi tạo chiến lược tách đệ quy tối ưu cho văn bản quy chế Markdown
chunker = RecursiveChunker(
    separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " ", ""],
    chunk_size=600,
)

# Chia nhỏ và áp dụng Header Injection
raw_chunks = chunker.chunk(document_body)
chunks = [f"[{document_title}]\n{c}" for c in raw_chunks]
```

**Thành viên 2 — [Thành viên 2]**
- **Loại chiến lược:** SentenceChunker (Tách theo ranh giới câu, `max_sentences_per_chunk=3`)
- **Mô tả & lý do chọn:** Tập trung bảo toàn tính hoàn chỉnh của ngữ pháp câu tiếng Việt, phù hợp với các điều khoản dài có cấu trúc câu phức tạp.
- **Code snippet:**
```python
from src.chunking import SentenceChunker
chunker = SentenceChunker(max_sentences_per_chunk=3)
chunks = chunker.chunk(document_body)
```

**Thành viên 3 — [Thành viên 3]**
- **Loại chiến lược:** FixedSizeChunker (Cửa sổ trượt kích thước cố định `chunk_size=300, overlap=50`)
- **Mô tả & lý do chọn:** Chiến lược đường cơ sở đơn giản, sử dụng overlap 50 ký tự để bù đắp phần ngữ cảnh bị ngắt ở biên mỗi chunk.
- **Code snippet:**
```python
from src.chunking import FixedSizeChunker
chunker = FixedSizeChunker(chunk_size=300, overlap=50)
chunks = chunker.chunk(document_body)
```

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Nguyễn Thái Dương | RecursiveChunker (`chunk_size=300`) | 10 / 10 | Giữ chuẩn ranh giới markdown, tính mạch lạc cao nhất, cô đọng nội dung | Cần tính toán kích thước chunk_size phù hợp với từng định dạng tài liệu |
| Thành viên 2 | SentenceChunker (`max_sentences=3`) | 8 / 10 | Đảm bảo câu ngữ pháp nguyên vẹn, không bao giờ ngắt ngang câu | Bỏ qua phân cấp tiêu đề markdown, đôi khi gộp các câu thuộc 2 mục khác nhau |
| Thành viên 3 | FixedSizeChunker (`300/50`) | 6 / 10 | Dễ triển khai, kiểm soát chặt chẽ dung lượng token/ký tự | Hay cắt ngang giữa từ hoặc mệnh đề số liệu quan trọng |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> **RecursiveChunker** là chiến lược tối ưu nhất cho bộ tài liệu Quy định & Dịch vụ Thư viện FPT. Lý do vì văn bản pháp quy có cấu trúc đề mục rõ ràng; `RecursiveChunker` tôn trọng cấu trúc phân tầng tự nhiên (`\n\n` -> `\n` -> câu), giữ cho mỗi điều khoản quy định được trọn vẹn trong một ngữ cảnh mạch lạc mà không bị pha loãng như các chunk quá lớn, giúp mô hình embedding vector nắm bắt chính xác các con số và hạn mức nghiệp vụ.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Sinh viên được mượn tối đa bao nhiêu tài liệu về nhà và thời hạn mượn sách tham khảo tiếng Việt, ngoại văn là bao lâu? | Sinh viên được mượn tối đa 10 tài liệu cùng lúc về nhà; sách tiếng Việt mượn 7 ngày; sách ngoại văn và song ngữ mượn 14 ngày. | `fpt-muon-sach-sinh-vien.md`, Mục 1 và Mục 3 |
| 2 | *(Cần filter student)* Hạn ngạch được phép mượn tài liệu về nhà tối đa là bao nhiêu cuốn cùng một lúc? | 10 tài liệu đối với sinh viên (nếu là cán bộ giảng viên thì được mượn tối đa 20 tài liệu). | `fpt-muon-sach-sinh-vien.md` (áp dụng `audience: student`) đối chiếu `fpt-muon-sach-giang-vien.md` |
| 3 | Mức phí phạt trả sách quá hạn mỗi ngày là bao nhiêu và có những phương thức thanh toán trực tuyến nào? | Phí phạt quá hạn là 5.000 VNĐ / tài liệu / ngày; có 2 phương thức thanh toán trực tuyến: qua ví FAP và qua cổng DNG (quét mã QR ngân hàng). | `fpt-phi-thu-vien.md`, Mục 1 và Mục 2 |
| 4 | Thời gian sử dụng phòng học nhóm tối đa là bao lâu mỗi ca và sau bao nhiêu phút không đến nhận phòng thì ca đặt sẽ bị hủy? | Thời gian sử dụng tối đa 2 giờ / ca (1 ca / nhóm / ngày); sau 15 phút kể từ giờ bắt đầu nếu nhóm không đến nhận phòng hoặc không đủ người tối thiểu thì ca đặt sẽ tự động bị hủy. | `fpt-phong-hoc-nhom.md`, Mục 2 |
| 5 | Mỗi cuốn sách được phép gia hạn tối đa mấy lượt và bạn đọc có thể thực hiện gia hạn qua những kênh nào? | Mỗi cuốn sách được phép gia hạn tối đa 4 lượt (nếu chưa có người đặt trước); gia hạn qua 4 kênh: cổng OPAC trực tuyến, gửi email, gọi điện thoại (024 6680 5912), hoặc nhắn tin qua Fanpage Thư viện FPTU. | `fpt-gia-han-tai-lieu.md`, Mục 1 và Mục 2 |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Hạn mức & thời hạn mượn sách SV | RecursiveChunker / SentenceChunker | Có (Top-1) | Trích xuất chính xác 10 tài liệu, 7 ngày, 14 ngày |
| 2 | Hạn ngạch mượn (cần filter) | Mọi chiến lược (kèm Metadata Filter) | Có (Top-1) | Bắt buộc phải có `audience: student` để loại trừ CBGV |
| 3 | Phạt quá hạn & cổng thanh toán | RecursiveChunker | Có (Top-1) | Chứa đầy đủ 5.000đ, ví FAP và cổng DNG |
| 4 | Quy định phòng học nhóm | FixedSizeChunker / RecursiveChunker | Có (Top-1) | Đầy đủ con số 2 giờ và hủy sau 15 phút |
| 5 | Lượt gia hạn & 4 kênh gia hạn | RecursiveChunker | Có (Top-1) | Trả về đủ 4 lượt và 4 kênh liên hệ |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Lọc bằng metadata cực kỳ hữu ích và quyết định tính chính xác ở Câu 2 (hỏi về hạn ngạch mượn tài liệu tối đa). Nếu không lọc theo `metadata_filter={"audience": "student"}`, độ tương đồng ngữ nghĩa sẽ kéo cả tài liệu của Cán bộ Giảng viên (`fpt-muon-sach-giang-vien.md`) vào top-k, khiến Agent trả lời nhầm thành 20 cuốn thay vì 10 cuốn cho sinh viên. Nhờ metadata pre-filtering, không gian tìm kiếm được cô lập chính xác về đối tượng sinh viên, loại bỏ hoàn toàn nhiễu từ các văn bản dành cho giảng viên/nhân viên.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
1. **Sự đánh đổi về kích thước và ranh giới chunk:** Cắt văn bản theo kích thước cố định (`FixedSizeChunker`) rất dễ cắt đôi câu và chia tách bảng số liệu quan trọng; trong khi `RecursiveChunker` bám sát ranh giới đề mục Markdown (`\n\n`), giữ trọn vẹn từng điều khoản quy chế độc lập giúp bảo toàn ngữ cảnh tốt nhất.
2. **Vai trò quyết định của Metadata Pre-filtering:** Đối với các câu hỏi về hạn mức mượn sách, hai tài liệu của sinh viên (10 cuốn) và giảng viên (20 cuốn) có từ vựng và chủ đề gần như tương đồng hoàn toàn. Tìm kiếm theo vector đơn thuần sẽ dễ nhầm lẫn; việc lọc trước bằng `audience: student` giúp khoanh vùng dữ liệu chính xác 100%.
3. **Phân tích Failure Case (Hạn chế của mô hình nhúng giả lập MockEmbedder):** Do `MockEmbedder` sử dụng hàm băm MD5 tạo vector giả lập bị ảnh hưởng bởi hiệu ứng tuyết lở (thay đổi 1 từ làm vector đảo hướng), độ tương đồng vector không phản ánh ngữ nghĩa thực tế. Muốn hệ thống RAG hoạt động tối ưu trong sản phẩm thật, cần triển khai các mô hình Sentence Transformers hoặc OpenAI Embeddings.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng chạy trên một bộ ngữ liệu quy chế thư viện chuẩn hóa, việc lựa chọn chiến lược chunking quyết định trực tiếp đến độ mạch lạc của thông tin được đưa vào context của LLM. `RecursiveChunker` vượt trội hơn hẳn nhờ việc tận dụng cấu trúc tự nhiên của văn bản Markdown, giúp câu trả lời của Agent luôn bám sát căn cứ dữ liệu (grounding) và không bị mất số liệu ở các điểm ngắt chunk.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ áp dụng kỹ thuật **Header Injection** (gắn tiêu đề phân cấp H1/H2 vào đầu mỗi chunk con) để đảm bảo dù chunk bị cắt nhỏ đến đâu vẫn mang đầy đủ ngữ cảnh nguồn. Đồng thời, nhóm sẽ tích hợp mô hình embedding chuyên biệt cho tiếng Việt để loại bỏ triệt để nhiễu số liệu từ hàm băm mock.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |

