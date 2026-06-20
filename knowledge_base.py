from __future__ import annotations

from typing import Iterable
from typing import List

from medical_knowledge import MEDICAL_DOCUMENTS, MedicalDocument


def _tokenize(text: str) -> set[str]:
    return {word.strip(".,!?").lower() for word in text.split() if word.strip()}


class MedicalKnowledgeBase:
    def __init__(self, documents: List[MedicalDocument] | None = None) -> None:
        self.documents = documents or MEDICAL_DOCUMENTS
        self._texts = [doc.to_text() for doc in self.documents]
        self._embedding_model = None
        self._faiss_index = None
        self._embedding_matrix = None
        self._setup_vector_search()

    def _setup_vector_search(self) -> None:
        try:
            import faiss  # type: ignore
            import numpy as np  # type: ignore
            from sentence_transformers import SentenceTransformer  # type: ignore
        except ImportError:
            return

        try:
            model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
            embeddings = model.encode(self._texts)
            matrix = np.array(embeddings).astype("float32")
            index = faiss.IndexFlatL2(matrix.shape[1])
            index.add(matrix)
        except Exception:
            return

        self._embedding_model = model
        self._embedding_matrix = matrix
        self._faiss_index = index

    def _keyword_search(self, query: str, top_k: int) -> List[MedicalDocument]:
        query_tokens = _tokenize(query)
        scored = []
        for doc in self.documents:
            overlap = len(query_tokens & _tokenize(doc.to_text()))
            scored.append((overlap, doc))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [doc for _, doc in scored[:top_k]]

    def _vector_search(self, query: str, top_k: int) -> List[MedicalDocument]:
        if self._embedding_model is None or self._faiss_index is None:
            return []

        try:
            query_vector = self._embedding_model.encode([query]).astype("float32")
            _, indices = self._faiss_index.search(query_vector, top_k)
            return [self.documents[idx] for idx in indices[0] if 0 <= idx < len(self.documents)]
        except Exception:
            return []

    def search(self, query: str, top_k: int = 2) -> List[MedicalDocument]:
        vector_results = self._vector_search(query, top_k=top_k)
        if vector_results:
            return vector_results
        return self._keyword_search(query, top_k=top_k)

    def backend_name(self) -> str:
        if self._faiss_index is not None and self._embedding_model is not None:
            return "faiss"
        return "keyword"
