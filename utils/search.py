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
        return [t for t in tokens if t not in STOPWORDS]

    def extract_snippet(self, chunk: str, query: str, max_len: int = 300):
        sentences = re.split(r'(?<=[.!?]) +', chunk)
        query_tokens = self.preprocess(query)
        scores = [
            sum(word in query_tokens for word in re.findall(r'\w+', s.lower())) 
            for s in sentences
        ]
        best_idx = int(np.argmax(scores)) if scores else 0
        snippet = sentences[best_idx] if sentences else chunk
        return snippet[:max_len] + ("…" if len(snippet) > max_len else "")

    def highlight_keywords(self, text: str, query: str, threshold: float = 0.75):
        try:
            # Wörter im Text
            words = list(set(re.findall(r'\w{4,}', text)))
            if not words:
                return text

            # Query-Embedding
            query_emb = self.embedding_model.encode(query, convert_to_numpy=True)
            query_emb = np.array(query_emb, dtype=np.float32)
            if query_emb.ndim == 1:
                query_emb = query_emb.reshape(1, -1)

            # Wort-Embeddings
            word_embs = self.embedding_model.encode(words, convert_to_numpy=True)
            word_embs = np.array(word_embs, dtype=np.float32)
            if word_embs.ndim == 1:
                word_embs = word_embs.reshape(1, -1)

            if query_emb.shape[1] != word_embs.shape[1]:
                return text

            sims = cosine_similarity(query_emb, word_embs)[0]

            # Synonyme
            synonym_map = {
                "Zession": ["Abtretung", "Zessionserklärung"],
                "Kapitalerhöhung": ["Kapitalband", "Erhöhung des Aktienkapitals"],
                "Dienstbarkeit": ["Leitungsrecht", "Wegrecht"],
                "Kaufrecht": ["Vorkaufsrecht", "Vorhandrecht"]
            }
            extended_terms = set([w.lower() for w in self.preprocess(query)])
            for key, syns in synonym_map.items():
                if any(t.lower() in query.lower() for t in [key] + syns):
                    extended_terms.update([s.lower() for s in [key] + syns])

            highlighted = text
            for word, sim in zip(words, sims):
                if sim >= threshold or word.lower() in extended_terms:
                    highlighted = re.sub(
                        rf"\b({re.escape(word)})\b",
                        r"<mark>\1</mark>",
                        highlighted,
                        flags=re.IGNORECASE
                    )
            return highlighted

        except Exception as e:
            print(f"[highlight_keywords] Fehler: {e}")
            return text

    def search(self, query: str, k: int = 3, alpha: float = 0.5, return_debug: bool=False):
        # Embedding-Scores
        embedding_results = self.vectorstore.similarity_search_with_score(query, k=len(self.texts))
        embedding_scores = {doc.page_content: s
