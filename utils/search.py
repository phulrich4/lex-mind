# utils/search.py
from typing import List, Tuple
import re
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
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
from sklearn.feature_extraction.text import TfidfVectorizer

class HybridRetriever:
    def __init__(self, vectorstore: InMemoryVectorStore, texts: List[Document], embedding_model, debug: bool=False):
        self.vectorstore = vectorstore
        self.texts = texts
        self.embedding_model = embedding_model
        self.debug = debug

        # TF-IDF vorbereiten
        self.vectorizer = TfidfVectorizer(stop_words=list(STOPWORDS))
        self.corpus = [doc.page_content for doc in texts]
        if self.corpus:
            self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus)
        else:
            self.tfidf_matrix = None

    def preprocess(self, text: str) -> list[str]:
        tokens = re.findall(r'\w+', text.lower())
        return [t for t in tokens if t not in STOPWORDS]

    def search(self, query: str, k: int = 5, alpha: float = 0.5) -> List[Tuple[Document, float]]:
        """
        Hybrid-Suche: kombiniert Embeddings + TF-IDF.
        alpha = Gewichtung (0 = nur TF-IDF, 1 = nur Embedding)
        """
        results: List[Tuple[Document, float]] = []

        # --- Embedding-Suche ---
        if self.vectorstore:
            for doc, score in self.vectorstore.similarity_search_with_score(query, k=k*2):
                results.append((doc, alpha * score))

        # --- TF-IDF-Suche ---
        if self.tfidf_matrix is not None:
            query_vec = self.vectorizer.transform([query])
            scores = cosine_similarity(query_vec, self.tfidf_matrix)[0]
            for idx in np.argsort(scores)[::-1][:k*2]:
                doc = self.texts[idx]
                score = float(scores[idx]) * (1 - alpha)

                # vorhandene Dokumente summieren
                found = False
                for i, (d, s) in enumerate(results):
                    if d == doc:
                        results[i] = (d, s + score)
                        found = True
                        break
                if not found:
                    results.append((doc, score))

        # --- Sortieren und Top-k zurückgeben ---
        results = sorted(results, key=lambda x: x[1], reverse=True)[:k]
        return results
