# utils/search.py
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple


class Document:
    """Minimaler Ersatz für LangChain Document"""
    def __init__(self, page_content: str, metadata: dict = None):
        self.page_content = page_content
        self.metadata = metadata or {}


class HybridRetriever:
    def __init__(self, embedding_model, docs: List[Document], debug: bool = False):
        self.embedding_model = embedding_model
        self.docs = docs
        self.debug = debug

        # 🟢 Precompute Embeddings für alle Dokumente
        if docs:
            self.doc_embeddings = self.embedding_model.encode(
                [doc.page_content for doc in docs], convert_to_numpy=True
            )
        else:
            self.doc_embeddings = np.array([])

        # 🟢 BM25 / TF-IDF vorbereiten
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.corpus = [doc.page_content for doc in docs]
        if self.corpus:
            self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus)
        else:
            self.tfidf_matrix = None

    def preprocess(self, text: str) -> List[str]:
        return re.findall(r"\w{4,}", text.lower())

    def search(self, query: str, k: int = 3, alpha: float = 0.5) -> List[Tuple[Document, float]]:
        """
        Hybrid-Suche: kombiniert Embeddings (Cosine Similarity) + TF-IDF.
        alpha: Gewichtung Embedding vs. BM25 (0=BM25 only, 1=Embeddings only)
        """
        scores_dict = {}

        # 🟢 Embedding-Suche
        if len(self.docs) > 0 and self.doc_embeddings.size > 0:
            try:
                query_emb = self.embedding_model.encode(query, convert_to_numpy=True)
                query_emb = np.array(query_emb, dtype=np.float32).reshape(1, -1)

                sims = cosine_similarity(query_emb, self.doc_embeddings)[0]
                for i, score in enumerate(sims):
                    scores_dict[self.docs[i]] = alpha * float(score)
            except Exception as e:
                print(f"[HybridRetriever] Embedding-Suche Fehler: {e}")

        # 🟢 BM25 / TF-IDF-Suche
        if self.tfidf_matrix is not None:
            try:
                query_vec = self.vectorizer.transform([query])
                scores = cosine_similarity(query_vec, self.tfidf_matrix)[0]
                for i, score in enumerate(scores):
                    scores_dict[self.docs[i]] = scores_dict.get(self.docs[i], 0) + (1 - alpha) * float(score)
            except Exception as e:
                print(f"[HybridRetriever] BM25-Suche Fehler: {e}")

        # 🟢 Top-k Ergebnisse sortiert zurückgeben
        results = sorted(scores_dict.items(), key=lambda x: x[1], reverse=True)[:k]
        return results

    def highlight_keywords(self, text: str, query: str, threshold: float = 0.75):
        try:
            words = list(set(re.findall(r'\w{4,}', text)))
            if not words:
                return text

            # Query-Embedding
            query_emb = self.embedding_model.encode(query, convert_to_numpy=True)
            query_emb = np.array(query_emb, dtype=np.float32).reshape(1, -1)

            # Wort-Embeddings
            word_embs = self.embedding_model.encode(words, convert_to_numpy=True)
            word_embs = np.array(word_embs, dtype=np.float32)
            if word_embs.ndim == 1:
                word_embs = word_embs.reshape(1, -1)

            if query_emb.shape[1] != word_embs.shape[1]:
                return text

            sims = cosine_similarity(query_emb, word_embs)[0]

            # Synonyme erweitern
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

            # Debugging-Ansicht
            if self.debug:
                import pandas as pd
                import streamlit as st
                df = pd.DataFrame({
                    "word": words,
                    "similarity": sims,
                    "highlighted": [sim >= threshold or w.lower() in extended_terms for w, sim in zip(words, sims)]
                })
                st.write("🔍 **Highlight-Debugging:**")
                st.dataframe(df.sort_values("similarity", ascending=False).reset_index(drop=True))

            # Wörter markieren
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
