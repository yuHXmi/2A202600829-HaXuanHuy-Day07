from pathlib import Path

import sys

sys.stdout.reconfigure(encoding="utf-8")

from src.chunking import SentenceChunker
from src.models import Document
from src.store import EmbeddingStore

chunker = SentenceChunker(
    max_sentences_per_chunk=5
)

docs = []

for path in Path("data/bocongan").glob("*.txt"):

    text = path.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    chunks = chunker.chunk(text)

    for i, chunk in enumerate(chunks):

        docs.append(
            Document(
                id=f"{path.stem}_{i}",
                content=chunk,
                metadata={
                    "source": path.name,
                    "chunk_index": i,
                    "strategy": "sentence_chunking"
                }
            )
        )

from src.embeddings import LocalEmbedder

embedder = LocalEmbedder()

store = EmbeddingStore(
    embedding_fn=embedder
)

store.add_documents(docs)

print(
    "Chunks stored:",
    store.get_collection_size()
)

queries = [
    "Theo Thông tư liên tịch về tội chứa chấp hoặc tiêu thụ tài sản do người khác phạm tội mà có, thế nào là tài sản/vật phạm pháp có giá trị lớn, rất lớn, đặc biệt lớn? ",
    "Hồ sơ đề nghị cấp, sửa đổi, bổ sung hộ chiếu phổ thông gồm những giấy tờ gì? Yêu cầu ảnh như thế nào?",
    "Chỉ tìm trong văn bản còn hiệu lực năm 2016: thời hạn giải quyết hồ sơ hộ chiếu tại Phòng Quản lý xuất nhập cảnh và tại Cục Quản lý xuất nhập cảnh là bao lâu?",
    "Nếu bị mất hộ chiếu, người dân phải trình báo trong thời hạn bao lâu và cần xuất trình giấy tờ gì? Nếu gửi đơn qua bưu điện thì cần điều kiện gì?",
    "Trong văn bản ban hành tiêu chuẩn quốc gia lĩnh vực an ninh, có bao nhiêu tiêu chuẩn được ban hành? Mã tiêu chuẩn của “Quy trình giám định ADN” và “Quy trình giám định dữ liệu số trong các thiết bị kết nối với máy vi tính” là gì?"
]


for query in queries:

    print("\n")
    print("=" * 60)

    print("QUERY:", query)

    results = store.search(
        query,
        top_k=3
    )

    for rank, result in enumerate(
        results,
        start=1
    ):

        print("\nTOP", rank)

        print(
            "Source:",
            result["metadata"]["source"]
        )

        print(
            result["content"][:500]
        )