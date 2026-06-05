from __future__ import annotations

from typing import Any, Callable

from .chunking import _dot
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    A vector store for text chunks.

    Tries to use ChromaDB if available; falls back to an in-memory store.
    The embedding_fn parameter allows injection of mock embeddings for tests.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

        try:
            import chromadb  # noqa: F401

            # TODO: initialize chromadb client + collection
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        metadata = dict(doc.metadata)
        metadata["doc_id"] = doc.id

        return {
            "id": doc.id,
            "content": doc.content,
            "metadata": metadata,
            "embedding": self._embedding_fn(doc.content),
        }

    def _search_records(
        self,
        query: str,
        records: list[dict[str, Any]],
        top_k: int,
    ) -> list[dict[str, Any]]:

        query_embedding = self._embedding_fn(query)

        scored = []

        for record in records:
            score = _dot(
                query_embedding,
                record["embedding"]
            )

            result = dict(record)
            result["score"] = score

            scored.append(result)

        scored.sort(
            key=lambda x: x["score"],
            reverse=True,
        )

        return scored[:top_k]

    def add_documents(self, docs: list[Document]) -> None:

        if self._use_chroma and self._collection is not None:

            ids = []
            documents = []
            embeddings = []
            metadatas = []

            for doc in docs:

                metadata = dict(doc.metadata)
                metadata["doc_id"] = doc.id

                ids.append(doc.id)
                documents.append(doc.content)
                embeddings.append(
                    self._embedding_fn(doc.content)
                )
                metadatas.append(metadata)

            self._collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
            )

            return

        for doc in docs:
            self._store.append(
                self._make_record(doc)
            )

    def search(
        self,
        query: str,
        top_k: int = 5
    ) -> list[dict[str, Any]]:

        if self._use_chroma and self._collection is not None:

            query_embedding = self._embedding_fn(query)

            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
            )

            output = []

            docs = results.get(
                "documents",
                [[]]
            )[0]

            metas = results.get(
                "metadatas",
                [[]]
            )[0]

            for doc, meta in zip(docs, metas):
                output.append(
                    {
                        "content": doc,
                        "metadata": meta,
                    }
                )

            return output

        return self._search_records(
            query=query,
            records=self._store,
            top_k=top_k,
        )

    def get_collection_size(self) -> int:

        if self._use_chroma and self._collection is not None:
            return self._collection.count()

        return len(self._store)

    def search_with_filter(
        self,
        query: str,
        top_k: int = 3,
        metadata_filter: dict = None,
    ) -> list[dict]:

        if metadata_filter is None:
            metadata_filter = {}

        filtered = []

        for record in self._store:

            metadata = record.get(
                "metadata",
                {}
            )

            if all(
                metadata.get(k) == v
                for k, v in metadata_filter.items()
            ):
                filtered.append(record)

        return self._search_records(
            query=query,
            records=filtered,
            top_k=top_k,
        )

    def delete_document(
        self,
        doc_id: str
    ) -> bool:

        before = len(self._store)

        self._store = [
            r
            for r in self._store
            if r["metadata"].get("doc_id")
            != doc_id
        ]

        return len(self._store) < before
