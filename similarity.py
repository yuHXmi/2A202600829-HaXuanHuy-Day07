# similarity_demo.py

from src.chunking import compute_similarity
from src.embeddings import MockEmbedder

pairs = [
    (
        "Cấp lại căn cước công dân",
        "Làm lại CCCD"
    ),
    (
        "Đăng ký cư trú",
        "Khai báo nơi ở"
    ),
    (
        "Hôm nay trời mưa",
        "Thuật toán PPO"
    ),
]

for a, b in pairs:

    score = compute_similarity(
        MockEmbedder(a),
        MockEmbedder(b)
    )

    print(a)
    print(b)
    print(score)
    print()