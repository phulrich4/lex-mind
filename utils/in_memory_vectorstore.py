# utils/in_memory_vectorstore.py
from typing import List
import numpy as np
from langchain.docstore.document import Document
from langchain.embeddings.base import Embeddings
from sklearn.metrics.pairwise import cosine_similarity

class InMemoryVectorStore:
    def __init__(self, documents: List[Document], embeddings: Embeddings):
        self.documents = documents
        self.embedding_model = embeddings
        # Berechne Embeddings aller Dokumente einmal
        self.doc_embeddings = np.array([embeddings.embed_query(doc.page_content) for doc in documents])

    @classmethod
    def from_documents(cls, documents: List[Document], embedding: Embeddings):
        return cls(documents, embedding)

    def similarity_search_with_score(self, query: str, k: int = 5):
        query_emb = self.embedding_model.embed_query(query)
        scores = cosine_similarity([query_emb], self.doc_embeddings)[0]
        top_idx = np.argsort(scores)[::-1][:k]
        return [(self.documents[i], float(scores[i])) for i in top_idx]
