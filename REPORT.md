# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Hà Xuân Huy
**Nhóm:** [Tên nhóm]
**Ngày:** 05/06/2026

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**

High cosine similarity cho thấy hai vector embedding có hướng gần giống nhau trong không gian vector. Điều này thường biểu thị hai câu hoặc hai đoạn văn có nội dung và ý nghĩa tương đồng.

**Ví dụ HIGH similarity:**

* Sentence A: Python is a popular programming language.
* Sentence B: Python is widely used for software development.
* Tại sao tương đồng: Cả hai câu đều nói về Python và việc sử dụng Python trong lập trình.

**Ví dụ LOW similarity:**

* Sentence A: Python is a programming language.
* Sentence B: The weather is rainy today.
* Tại sao khác: Hai câu thuộc hai chủ đề hoàn toàn khác nhau.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**

Cosine similarity tập trung vào hướng của vector thay vì độ lớn của vector. Trong embedding, hướng thường phản ánh ý nghĩa ngữ nghĩa tốt hơn khoảng cách Euclidean.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**

Bước nhảy:

500 - 50 = 450

Số chunk:

ceil((10000 - 500) / 450) + 1

= ceil(9500 / 450) + 1

= 22 + 1

= 23

**Đáp án:** 23 chunks

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**

Overlap tăng làm bước nhảy giảm nên số lượng chunk tăng lên. Overlap lớn giúp giữ được ngữ cảnh giữa các chunk và giảm nguy cơ mất thông tin khi câu hoặc đoạn văn bị cắt ở ranh giới chunk.

---

## Part 3 — So Sánh Retrieval Strategy (Nhóm)

### Exercise 3.0 — Chuẩn Bị Tài Liệu

*Domain:* Hệ thống văn bản pháp luật Việt Nam

### Data Inventory

| #  | Tên tài liệu                           | Nguồn | Số ký tự  | Metadata đã gán    |
| -- | -------------------------------------- | ----- | --------- | ------------------ |
| 1  | Văn bản Bộ Tư pháp                     | VBPL  | ~100.000+ | slug, dvid, source |
| 2  | Văn bản Bộ Công an                     | VBPL  | ~100.000+ | slug, dvid, source |
| 3  | Văn bản Bộ Giáo dục và Đào tạo         | VBPL  | ~100.000+ | slug, dvid, source |
| 4  | Văn bản Bộ Tài chính                   | VBPL  | ~100.000+ | slug, dvid, source |
| 5  | Văn bản Bộ Y tế                        | VBPL  | ~100.000+ | slug, dvid, source |
| 6  | Văn bản Bộ Giao thông Vận tải          | VBPL  | ~100.000+ | slug, dvid, source |
| 7  | Văn bản Ngân hàng Nhà nước             | VBPL  | ~100.000+ | slug, dvid, source |
| 8  | Văn bản Tòa án nhân dân tối cao        | VBPL  | ~100.000+ | slug, dvid, source |
| 9  | Văn bản Viện kiểm sát nhân dân tối cao | VBPL  | ~100.000+ | slug, dvid, source |
| 10 | Văn bản Văn phòng Chính phủ            | VBPL  | ~100.000+ | slug, dvid, source |

### Metadata Schema

| Trường metadata | Kiểu   | Ví dụ                        |
| --------------- | ------ | ---------------------------- |
| slug            | string | botuphap                     |
| dvid            | string | 41                           |
| source          | string | vbpl.vn                      |
| search_url      | string | https://vbpl.vn/botuphap/... |

### Mô tả dữ liệu

Nhóm sử dụng dữ liệu được thu thập từ hệ thống Văn bản Pháp luật Việt Nam (VBPL). Bộ dữ liệu bao gồm các văn bản pháp luật được ban hành bởi nhiều cơ quan nhà nước khác nhau như Bộ Tư pháp, Bộ Công an, Bộ Giáo dục và Đào tạo, Bộ Tài chính, Bộ Y tế, Ngân hàng Nhà nước, Tòa án nhân dân tối cao và nhiều đơn vị khác.

Metadata được lưu cùng mỗi văn bản nhằm hỗ trợ retrieval theo nguồn ban hành. Điều này giúp hệ thống có thể lọc và truy xuất chính xác hơn khi người dùng đặt câu hỏi liên quan đến một lĩnh vực pháp luật cụ thể.

## 4. My Approach — Cá nhân (10 điểm)

### Chunking Functions

**SentenceChunker.chunk — approach**

Em sử dụng biểu thức chính quy để tách văn bản theo các dấu kết thúc câu như ".", "!" và "?". Sau khi tách, các câu được gom thành từng nhóm với số lượng tối đa bằng `max_sentences_per_chunk`.

**RecursiveChunker.chunk / _split — approach**

Thuật toán thực hiện chia văn bản theo thứ tự ưu tiên của các separator như đoạn văn, dòng, câu và khoảng trắng. Nếu một phần vẫn vượt quá `chunk_size`, hàm tiếp tục gọi đệ quy với separator tiếp theo cho đến khi kích thước phù hợp hoặc phải cắt theo ký tự.

### EmbeddingStore

**add_documents + search — approach**

Mỗi document được chuyển thành embedding thông qua embedding function rồi lưu cùng metadata trong vector store. Khi tìm kiếm, query được embed và độ tương đồng được tính bằng phép nhân vô hướng giữa embedding của query và embedding của từng document.

**search_with_filter + delete_document — approach**

`search_with_filter` lọc trước theo metadata rồi mới thực hiện tìm kiếm tương đồng trên tập kết quả đã lọc. `delete_document` loại bỏ toàn bộ record có `doc_id` tương ứng khỏi vector store.

### KnowledgeBaseAgent

**answer — approach**

Agent truy xuất top-k document liên quan từ vector store, ghép các document này thành context rồi chèn vào prompt cùng câu hỏi của người dùng. Prompt hoàn chỉnh được gửi cho LLM để sinh câu trả lời theo mô hình RAG.

### Test Results

```bash
pytest tests/ -v
```

Kết quả:

* Tổng số test: 42
* Số test pass: 42
* Số test fail: 0

**Số tests pass:** 42 / 42



## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | | | high / low | | |
| 2 | | | high / low | | |
| 3 | | | high / low | | |
| 4 | | | high / low | | |
| 5 | | | high / low | | |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> *Viết 2-3 câu:*

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân của bạn trong package `src`. **5 queries phải trùng với các thành viên cùng nhóm.**

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | Theo Thông tư liên tịch về tội chứa chấp hoặc tiêu thụ tài sản do người khác phạm tội mà có, thế nào là tài sản/vật phạm pháp có giá trị lớn, rất lớn, đặc biệt lớn? | Giá trị lớn: từ 50 triệu đến dưới 200 triệu đồng. Rất lớn: từ 200 triệu đến dưới 500 triệu đồng. Đặc biệt lớn: từ 500 triệu đồng trở lên. Nguồn: data/bocongan/100152.txt, Điều 2, khoản 4-6. |
| 2 | Hồ sơ đề nghị cấp, sửa đổi, bổ sung hộ chiếu phổ thông gồm những giấy tờ gì? Yêu cầu ảnh như thế nào? | Hồ sơ gồm: 01 tờ khai mẫu X01; 02 ảnh mới chụp cỡ 4cm x 6cm, mặt nhìn thẳng, đầu để trần, không đeo kính màu, phông nền trắng. Trẻ em dưới 09 tuổi cấp chung hộ chiếu với cha hoặc mẹ thì nộp 02 ảnh cỡ 3cm x 4cm. Trẻ em dưới 14 tuổi nộp thêm bản sao hoặc bản chụp có chứng thực giấy khai sinh, nếu không chứng thực thì xuất trình bản chính để đối chiếu. Nguồn: data/bocongan/118633.txt, Điều 6. |
| 3 | Chỉ tìm trong văn bản còn hiệu lực năm 2016: thời hạn giải quyết hồ sơ hộ chiếu tại Phòng Quản lý xuất nhập cảnh và tại Cục Quản lý xuất nhập cảnh là bao lâu? | Với hồ sơ nộp tại Phòng Quản lý xuất nhập cảnh: không quá 08 ngày làm việc kể từ ngày nhận đủ hồ sơ hợp lệ. Với hồ sơ nộp tại Cục Quản lý xuất nhập cảnh: không quá 05 ngày làm việc. Trường hợp cần hộ chiếu gấp thì giải quyết sớm nhất trong thời hạn quy định. Nguồn: data/bocongan/118633.txt, Điều 8. Nên chạy filter metadata: status = Còn hiệu lực, filter_year = 2016. |
| 4 | Nếu bị mất hộ chiếu, người dân phải trình báo trong thời hạn bao lâu và cần xuất trình giấy tờ gì? Nếu gửi đơn qua bưu điện thì cần điều kiện gì? | Trong 48 giờ kể từ khi phát hiện mất hộ chiếu, người bị mất phải trình báo với cơ quan Quản lý xuất nhập cảnh nơi gần nhất theo mẫu X08 để hủy giá trị sử dụng của hộ chiếu đã mất. Khi trình báo cần xuất trình CMND hoặc thẻ CCCD còn giá trị. Nếu gửi đơn qua bưu điện thì đơn phải có xác nhận của Trưởng Công an phường, xã, thị trấn nơi người đó thường trú hoặc tạm trú. Nguồn: data/bocongan/118633.txt, Điều 9. |
| 5 | Trong văn bản ban hành tiêu chuẩn quốc gia lĩnh vực an ninh, có bao nhiêu tiêu chuẩn được ban hành? Mã tiêu chuẩn của “Quy trình giám định ADN” và “Quy trình giám định dữ liệu số trong các thiết bị kết nối với máy vi tính” là gì? | Văn bản ban hành 27 tiêu chuẩn quốc gia trong lĩnh vực an ninh. “Quy trình giám định ADN” có mã TCVN - AN: 035:2013. “Quy trình giám định dữ liệu số trong các thiết bị kết nối với máy vi tính” có mã TCVN - AN: 041:2013. Nguồn: data/bocongan/103191.txt, Điều 1. |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Bao nhiêu queries trả về chunk relevant trong top-3?** __ / 5

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> *Viết 2-3 câu:*

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> *Viết 2-3 câu:*

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | / 5 |
| Document selection | Nhóm | / 10 |
| Chunking strategy | Nhóm | / 15 |
| My approach | Cá nhân | / 10 |
| Similarity predictions | Cá nhân | / 5 |
| Results | Cá nhân | / 10 |
| Core implementation (tests) | Cá nhân | / 30 |
| Demo | Nhóm | / 5 |
| **Tổng** | | **/ 100** |







## Part 3 — So Sánh Retrieval Strategy (Nhóm)

### Exercise 3.0 — Chuẩn Bị Tài Liệu

**Domain:** Hệ thống văn bản pháp luật Việt Nam

### Data Inventory

| #  | Tên tài liệu                           | Nguồn | Số ký tự  | Metadata đã gán    |
| -- | -------------------------------------- | ----- | --------- | ------------------ |
| 1  | Văn bản Bộ Tư pháp                     | VBPL  | ~100.000+ | slug, dvid, source |
| 2  | Văn bản Bộ Công an                     | VBPL  | ~100.000+ | slug, dvid, source |
| 3  | Văn bản Bộ Giáo dục và Đào tạo         | VBPL  | ~100.000+ | slug, dvid, source |
| 4  | Văn bản Bộ Tài chính                   | VBPL  | ~100.000+ | slug, dvid, source |
| 5  | Văn bản Bộ Y tế                        | VBPL  | ~100.000+ | slug, dvid, source |
| 6  | Văn bản Bộ Giao thông Vận tải          | VBPL  | ~100.000+ | slug, dvid, source |
| 7  | Văn bản Ngân hàng Nhà nước             | VBPL  | ~100.000+ | slug, dvid, source |
| 8  | Văn bản Tòa án nhân dân tối cao        | VBPL  | ~100.000+ | slug, dvid, source |
| 9  | Văn bản Viện kiểm sát nhân dân tối cao | VBPL  | ~100.000+ | slug, dvid, source |
| 10 | Văn bản Văn phòng Chính phủ            | VBPL  | ~100.000+ | slug, dvid, source |

### Metadata Schema

| Trường metadata | Kiểu   | Ví dụ                        |
| --------------- | ------ | ---------------------------- |
| slug            | string | botuphap                     |
| dvid            | string | 41                           |
| source          | string | vbpl.vn                      |
| search_url      | string | https://vbpl.vn/botuphap/... |

### Mô tả dữ liệu

Nhóm sử dụng dữ liệu được thu thập từ hệ thống Văn bản Pháp luật Việt Nam (VBPL). Bộ dữ liệu bao gồm các văn bản pháp luật được ban hành bởi nhiều cơ quan nhà nước khác nhau như Bộ Tư pháp, Bộ Công an, Bộ Giáo dục và Đào tạo, Bộ Tài chính, Bộ Y tế, Ngân hàng Nhà nước, Tòa án nhân dân tối cao và nhiều đơn vị khác.

Metadata được lưu cùng mỗi văn bản nhằm hỗ trợ retrieval theo nguồn ban hành. Điều này giúp hệ thống có thể lọc và truy xuất chính xác hơn khi người dùng đặt câu hỏi liên quan đến một lĩnh vực pháp luật cụ thể.
