# utils/search.py
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from typing import List, Tuple


class HybridRetriever:
    def __init__(self, embedding_model, vectorstore: FAISS, docs: List[Document], debug: bool = False):
        self.embedding_model = embedding_model
        self.vectorstore = vectorstore
        self.docs = docs
        self.debug = debug

        # BM25 / TF-IDF vorbereiten
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
        Hybrid-Suche: kombiniert Embeddings (Vektorsuche) + TF-IDF (BM25-ähnlich).
        alpha: Gewichtung Embedding vs. BM25 (0=BM25 only, 1=Embeddings only)
        """
        results = []

        # Embedding-Suche
        embedding_results = []
        if self.vectorstore:
            try:
                embedding_results = self.vectorstore.similarity_search_with_score(query, k=k * 2)
            except Exception as e:
                print(f"[HybridRetriever] Embedding-Suche Fehler: {e}")

        # BM25 / TF-IDF-Suche
        bm25_results = []
        if self.tfidf_matrix is not None:
            try:
                query_vec = self.vectorizer.transform([query])
                scores = cosine_similarity(query_vec, self.tfidf_matrix)[0]
                bm25_results = [(self.docs[i], float(scores[i])) for i in np.argsort(scores)[::-1][:k * 2]]
            except Exception as e:
                print(f"[HybridRetriever] BM25-Suche Fehler: {e}")

        # Scores kombinieren
        all_docs = {}
        for doc, score in embedding_results:
            all_docs[doc] = all_docs.get(doc, 0) + alpha * score
        for doc, score in bm25_results:
            all_docs[doc] = all_docs.get(doc, 0) + (1 - alpha) * score

        # Top-k Ergebnisse sortiert zurückgeben
        results = sorted(all_docs.items(), key=lambda x: x[1], reverse=True)[:k]
        return results

    def highlight_keywords(self, text: str, query: str, threshold: float = 0.75):
        try:
            # Kandidatenwörter (mind. 4 Zeichen, um Rauschen zu vermeiden)
            words = list(set(re.findall(r'\w{4,}', text)))
            if not words:
                return text  # nichts zu highlighten

            # Query-Embedding robust bauen
            query_emb = self.embedding_model.encode(query, convert_to_numpy=True)
            query_emb = np.array(query_emb, dtype=np.float32)
            if query_emb.ndim == 1:
                query_emb = query_emb.reshape(1, -1)

            # Wort-Embeddings robust bauen
            word_embs = self.embedding_model.encode(words, convert_to_numpy=True)
            word_embs = np.array(word_embs, dtype=np.float32)

            # Spezialfall: nur ein Wort → (1, d)
            if word_embs.ndim == 1:
                word_embs = word_embs.reshape(1, -1)

            # Wenn Dimensionen nicht passen → abbrechen
            if query_emb.shape[1] != word_embs.shape[1]:
                return text

            # Cosine Similarity (Fehler sicher abfangen)
            try:
                sims = cosine_similarity(query_emb, word_embs)[0]
            except Exception as inner_e:
                print(f"[highlight_keywords] Cosine Error: {inner_e}")
                return text

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

            # Debug-Ausgabe (falls aktiviert)
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
            # Fallback: unverändert zurückgeben
            print(f"[highlight_keywords] Fehler: {e}")
            return text
