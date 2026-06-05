from pathlib import Path
from src.chunking import SentenceChunker

text = next(
    Path("data/bocongan").glob("*.txt")
).read_text(
    encoding="utf-8",
    errors="ignore"
)

for n in [2,3,5,10]:

    chunks = SentenceChunker(
        max_sentences_per_chunk=n
    ).chunk(text)

    avg = sum(
        len(c)
        for c in chunks
    ) / len(chunks)

    print(
        f"{n=}",
        f"chunks={len(chunks)}",
        f"avg={avg:.2f}"
    )