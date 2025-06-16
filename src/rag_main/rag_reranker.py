from typing import List, Tuple
from langchain.schema import Document
from sentence_transformers import CrossEncoder


class RAGReranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = CrossEncoder(model_name)

    def rerank(self, query: str, docs: List[Document], top_k: int = 3) -> List[Document]:
        if not docs:
            return []

        pairs = [(query, doc.page_content) for doc in docs]
        scores = self.model.predict(pairs)

        scored_docs: List[Tuple[float, Document]] = list(zip(scores, docs))
        scored_docs.sort(key=lambda x: x[0], reverse=True)

        return [doc for _, doc in scored_docs[:top_k]]
