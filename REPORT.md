# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Hà Xuân Huy
**Nhóm:** UET
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
## 2. Document Selection (Nhóm)

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

# 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh

## Baseline Analysis

Kết quả chạy `ChunkingStrategyComparator().compare()` trên 3 tài liệu pháp luật:

| Tài liệu | Strategy           | Chunk Count | Avg Length | Preserves Context? |
| -------- | ------------------ | ----------: | ---------: | ------------------ |
| All      | SentenceChunker(2) |          34 |     315.65 | Trung bình         |
| All      | SentenceChunker(3) |          23 |     467.09 | Tốt                |
| All      | SentenceChunker(5) |          14 |     768.00 | Khá tốt            |

## Strategy Của Tôi

**Loại:** SentenceChunker (max_sentences_per_chunk = 3)

### Mô tả cách hoạt động

SentenceChunker thực hiện tách văn bản dựa trên ranh giới câu thay vì độ dài ký tự cố định. Sau khi tách văn bản thành các câu riêng lẻ bằng biểu thức chính quy, thuật toán sẽ gom nhiều câu liên tiếp thành một chunk. Trong bài thực hành này, mỗi chunk chứa tối đa 3 câu.

Cách tiếp cận này giúp giữ nguyên cấu trúc ngữ nghĩa của câu, tránh việc một câu bị cắt đôi như khi sử dụng FixedSizeChunker.

### Tại sao tôi chọn strategy này cho domain nhóm?

Domain của nhóm là hệ thống hỏi đáp văn bản pháp luật Việt Nam. Trong các văn bản pháp luật, nội dung thường được trình bày thành các câu dài và có nhiều mối liên hệ ngữ nghĩa giữa các câu liên tiếp.

SentenceChunker giúp giữ nguyên câu hoàn chỉnh nên embedding thu được phản ánh ý nghĩa tốt hơn so với việc cắt theo số ký tự cố định. Ngoài ra, phương pháp này dễ triển khai và không cần các luật xử lý đặc biệt cho từng loại văn bản.

## So Sánh Với Thành Viên Khác

| Thành viên | Strategy         | Retrieval Score (/10) | Điểm mạnh                                                                                    | Điểm yếu                                                                                        |
| ---------- | ---------------- | --------------------- | -------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Tùng       | FixedSizeChunker | 4.0                   | Dễ triển khai, tốc độ xử lý nhanh, kích thước chunk đồng đều                                 | Dễ cắt giữa điều luật hoặc khoản luật, làm mất ngữ cảnh pháp lý và giảm chất lượng retrieval    |
| Huy        | SentenceChunker  | 6.0                   | Giữ nguyên cấu trúc câu, nội dung dễ đọc và dễ hiểu hơn FixedSizeChunker                     | Một điều luật dài có thể bị chia thành nhiều câu riêng biệt, làm mất mối liên hệ giữa các khoản |
| Dương      | RecursiveChunker | 8.0                   | Cân bằng tốt giữa độ dài chunk và ngữ cảnh, hạn chế việc cắt nội dung ở vị trí không phù hợp | Chưa tận dụng được cấu trúc đặc thù của văn bản pháp luật như Chương, Điều, Khoản               |
| Đạt        | RecursiveChunker | 8.5                   | Giữ được nhiều ngữ cảnh hơn SentenceChunker, linh hoạt với các văn bản có độ dài khác nhau   | Chất lượng phụ thuộc nhiều vào tham số chunk size và chunk overlap                              |

### Strategy nào tốt nhất cho domain này? Tại sao?

Đối với domain pháp luật Việt Nam, Legal-Aware Hierarchical Chunking vẫn là lựa chọn tốt nhất vì tận dụng được cấu trúc chương, điều và khoản của văn bản luật.

Tuy nhiên, trong phạm vi bài lab này, SentenceChunker là một giải pháp cân bằng giữa độ đơn giản và chất lượng retrieval. So với FixedSizeChunker, phương pháp này bảo toàn ngữ nghĩa tốt hơn và giảm nguy cơ cắt giữa câu.

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



# 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A                                      | Sentence B                                            | Dự đoán | Actual Score | Đúng? |
| ---- | ----------------------------------------------- | ----------------------------------------------------- | ------- | ------------ | ----- |
| 1    | The cat is sleeping on the sofa.                | A cat is resting on a couch.                          | High    | 4.8          | ✓     |
| 2    | I enjoy playing football on weekends.           | I like playing soccer during the weekend.             | High    | 4.7          | ✓     |
| 3    | The weather is sunny today.                     | I bought a new laptop yesterday.                      | Low     | 0.5          | ✓     |
| 4    | The company announced record profits this year. | The business reported its highest earnings this year. | High    | 4.5          | ✓     |
| 5    | She is reading a novel in the library.          | He drove his car to the supermarket.                  | Low     | 0.3          | ✓     |

## Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?

Kết quả bất ngờ nhất là các cặp câu số 1 và số 2. Mặc dù chúng sử dụng những từ khác nhau như "sofa" và "couch" hoặc "football" và "soccer", mô hình vẫn đánh giá độ tương đồng rất cao. Điều này cho thấy embeddings không chỉ dựa trên việc so khớp từ khóa mà còn học được ý nghĩa ngữ nghĩa của câu, giúp nhận diện các cách diễn đạt khác nhau nhưng mang cùng nội dung.


# 6. Results — Cá nhân (10 điểm)

## Baseline Analysis

Để đánh giá chất lượng retrieval, em sử dụng 5 benchmark queries của nhóm trên tập văn bản pháp luật Việt Nam. Hệ thống sử dụng SentenceChunker kết hợp embedding model `sentence-transformers/all-MiniLM-L6-v2`.

### Cấu hình

```python
chunker = SentenceChunker(
    max_sentences_per_chunk=3
)
```

## Đánh Giá Trên Bộ 5 Query

| # | Query                                | Top-1 Score | Đánh giá    |
| - | ------------------------------------ | ----------- | ----------- |
| 1 | Giá trị lớn, rất lớn, đặc biệt lớn   | 0.8241      | ❌ Sai       |
| 2 | Hồ sơ cấp, sửa đổi hộ chiếu          | 0.7939      | ⚠️ Một phần |
| 3 | Thời hạn giải quyết hồ sơ hộ chiếu   | 0.8006      | ❌ Sai       |
| 4 | Trình báo mất hộ chiếu               | 0.7949      | ❌ Sai       |
| 5 | Tiêu chuẩn quốc gia lĩnh vực an ninh | 0.8290      | ❌ Sai       |

## Kết Quả Retrieval

| # | Query                              | Top-1 Retrieved Chunk                 | Score  | Relevant? |
| - | ---------------------------------- | ------------------------------------- | ------ | --------- |
| 1 | Giá trị lớn, rất lớn, đặc biệt lớn | Điều khoản hiệu lực thi hành thông tư | 0.8241 | ❌         |
| 2 | Hồ sơ hộ chiếu                     | Quy định về yếu tố nhân thân          | 0.7939 | ⚠️        |
| 3 | Thời hạn giải quyết hồ sơ hộ chiếu | Quy định về cư trú                    | 0.8006 | ❌         |
| 4 | Mất hộ chiếu                       | Chế độ gửi thư của người bị tạm giam  | 0.7949 | ❌         |
| 5 | Tiêu chuẩn an ninh                 | Thi hành án tử hình                   | 0.8290 | ❌         |

## Thống Kê

| Chỉ số                | Giá trị |
| --------------------- | ------- |
| Tổng số query         | 5       |
| Top-1 đúng hoàn toàn  | 0       |
| Top-1 đúng một phần   | 1       |
| Top-1 sai             | 4       |
| Recall@1              | 0%      |
| Recall@1 (partial)    | 20%     |
| Similarity trung bình | 0.8085  |

## Nhận Xét

Kết quả cho thấy SentenceChunker giúp bảo toàn cấu trúc câu tốt hơn FixedSizeChunker, tuy nhiên chất lượng retrieval vẫn còn hạn chế trên tập dữ liệu pháp luật.

Mặc dù các giá trị cosine similarity đều khá cao (0.79–0.83), nhiều chunk được truy xuất không chứa đáp án thực tế. Điều này cho thấy embedding model đang gặp khó khăn trong việc phân biệt các khái niệm pháp lý chuyên biệt.

Ngoài ra, việc chỉ sử dụng dense retrieval mà không có bước reranking khiến nhiều chunk chứa từ khóa tương tự nhưng không liên quan vẫn được xếp hạng cao.

## Kết Luận

SentenceChunker là một lựa chọn đơn giản và hiệu quả hơn FixedSizeChunker trong việc bảo toàn ngữ nghĩa của văn bản. Tuy nhiên, với domain pháp luật Việt Nam, phương pháp này vẫn chưa đủ để đạt chất lượng retrieval cao.

Trong tương lai, hệ thống có thể được cải thiện bằng cách:

* Sử dụng embedding model mạnh hơn như BGE-M3 hoặc Qwen3-Embedding-8B.
* Kết hợp reranker sau bước retrieval.
* Chunk theo cấu trúc điều luật thay vì chỉ dựa trên câu.
* Sử dụng metadata filtering để giới hạn phạm vi tìm kiếm.

Retrieval Score ước lượng: **6.5/10**.

## 7. What I Learned (5 điểm — Demo)

### Điều hay nhất tôi học được từ thành viên khác trong nhóm

Qua quá trình thảo luận và so sánh kết quả, tôi nhận thấy việc thiết kế chiến lược chunking ảnh hưởng rất lớn đến chất lượng retrieval của hệ thống RAG. Một số thành viên đã thử các phương pháp dựa trên cấu trúc văn bản thay vì chỉ dựa trên độ dài chunk, giúp bảo toàn ngữ cảnh tốt hơn khi truy xuất thông tin từ văn bản pháp luật.

### Điều hay nhất tôi học được từ nhóm khác (qua demo)

Từ phần demo của các nhóm khác, tôi học được cách kết hợp metadata filtering với vector search để thu hẹp không gian tìm kiếm trước khi thực hiện retrieval. Cách tiếp cận này giúp giảm số lượng kết quả không liên quan và tăng khả năng tìm đúng văn bản chứa đáp án, đặc biệt đối với các bộ dữ liệu lớn.

### Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?

Nếu thực hiện lại dự án, tôi sẽ xây dựng chiến lược chunking dựa trên cấu trúc pháp lý như chương, điều và khoản thay vì chỉ dựa trên câu hoặc kích thước chunk cố định. Ngoài ra, tôi sẽ bổ sung metadata về trạng thái hiệu lực, năm ban hành và cơ quan ban hành để hỗ trợ filtering hiệu quả hơn, đồng thời thử nghiệm các embedding model mạnh hơn như BGE-M3 hoặc Qwen3-Embedding-8B.

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | 10 / 10 |
| Chunking strategy | Nhóm | 13 / 15 |
| My approach | Cá nhân | 10 / 10 |
| Similarity predictions | Cá nhân | 5 / 5 |
| Results | Cá nhân | 8 / 10 |
| Core implementation (tests) | Cá nhân | 30 / 30 |
| Demo | Nhóm | 5 / 5 |
| **Tổng** | | **86 / 100** |






