# utils/search.py
from typing import List
import re
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi
from langchain.docstore.document import Document

# ------------------------------
# Stopwords (deutsch)
# ------------------------------
STOPWORDS = {
    "eine","und","für","der","die","das","mit","von","zur","zum","im","des",
    "den","dem","ist","sind","auf","an","in","als","bei","auch","oder","nicht",
    "wie","so","wir","sie","er","es","hat","haben","dass"
}

# ------------------------------
# InMemory VectorStore
# ------------------------------
class InMemoryVectorStore:
    def __init__(self, docs: List[Document], embedding_model):
        self.docs = docs
        self.embedding_model = embedding_model
        self.embeddings = embedding_model.encode(
            [doc.page_content for doc in docs], 
            convert_to_numpy=True
        )

    @classmethod
    def from_documents(cls, docs: List[Document], embedding_model):
        return cls(docs, embedding_model)

    def similarity_search_with_score(self, query, k=10):
        if not self.docs:
            return []
        query_emb = self.embedding_model.encode([query], convert_to_numpy=True)
        sims = cosine_similarity(query_emb, self.embeddings)[0]
        results = [(self.docs[i], float(sims[i])) for i in np.argsort(sims)[::-1][:k]]
        return results

# ------------------------------
# HybridRetriever
# ------------------------------
class HybridRetriever:
    def __init__(self, vectorstore: InMemoryVectorStore, texts: List[Document], embedding_model, debug: bool=False):
        self.vectorstore = vectorstore
        self.texts = texts
        self.embedding_model = embedding_model
        self.debug = debug

    def preprocess(self, text: str) -> list[str]:
        tokens = re.findall(r'\w+', text.lower())
        return [t for t in tokens if t not in STOPW]
