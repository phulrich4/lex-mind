# utils/search.py
from typing import List, Optional
import re
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

# Feste deutsche Stoppwörter
STOPWORDS = {
    "eine","und","für","der","die","das","mit","von","zur","zum",
    "im","des","den","dem","ist","sind","auf","an","in","als","bei","auch",
    "oder","nicht","wie","so","wir","sie","er","es","hat","haben","dass"
}

# -------------------------------
# InMemory Vectorstore
# -------------------------------
class InMemoryVectorStore:
    def __init__(self, documents: List[dict], embeddings: np.ndarray):
        self.documents = documents
        self.embeddings = embeddings

    @classmethod
    def from_documents(cls, docs, embedding_model):
        texts = [doc.page_content for doc in docs]
        embeddings = embedding_model.encode(texts, convert_to_numpy=True)
        return cls(docs, embeddings)

    def similarity_search_with_score(self, query: str, k: int = 5):
        query_emb = self.embedding_model.encode([query], convert_to_numpy=True)
        sims = cosine_similarity(query_emb, self.embeddings)[0]
        docs_scores = list(zip(self.documents, sims))
        docs_scores.sort(key=lambda x: x[1], reverse=True)
        return docs_scores[:k]

# -------------------------------
# Hybrid Retriever
# -------------------------------
class HybridRetriever:
    def __init__(self, vectorstore: InMemoryVectorStore, texts: List, embedding_model: SentenceTransformer):
        self.vectorstore = vectorstore
        self.texts = texts
        self.embedding_model = embedding_model

    def preprocess(self, text: str) -> list[str]:
        tokens = re.findall(r'\w+', text.lower())
        return [t for t in tokens if t not in STOPWORDS]

    def extract_snippet(self, chunk: str, query: str, max_len: int = 300):
        sentences = re.split(r'(?<=[.!?]) +', chunk)
        query_tokens = self.preprocess(query)
        scores = [sum(word in query_tokens for word in re.findall(r'\w+', s.lower())) for s in sentences]
        best_idx = int(np.argmax(scores)) if scores else 0
        snippet = sentences[best_idx] if sentences else chunk
        return snippet[:max_len] + ("…" if len(snippet) > max_len else "")

    def highlight_keywords(self, text: str, query: str, threshold: float = 0.75):
        words = list(set(re.findall(r'\w{4,}', text)))
        query_emb = self.embedding_model.encode([query], convert_to_numpy=True)
        word_embs = self.embedding_model.encode(words, convert_to_numpy=True)
        similarities = cosine_similarity(query_emb, word_embs)[0]

        synonym_map = {
            "Zession": ["Abtretung", "Zessionserklärung"],
            "Kapitalerhöhung": ["Kapitalband", "Erhöhung des Aktienkapitals"],
            "Dienstbarkeit": ["Leitungsrecht", "Wegrecht"],
            "Kaufrecht": ["Vorkaufsrecht", "Vorhandrecht"]
        }

        query_tokens = set(self.preprocess(query))
        extended_terms = set(query_tokens)
        for key, syns in synonym_map.items():
            if any(t.lower() in query.lower() for t in [key] + syns):
                extended_terms.update(s.lower() for s in [key] + syns)

        highlighted = text
        for word, sim in zip(words, similarities):
            if sim >= threshold or word.lower() in extended_terms:
                highlighted = re.sub(rf"\b({re.escape(word)})\b", r"<mark>\1</mark>", highlighted, flags=re.IGNORECASE)
        return highlighted

    def search(self, query: str, k: int = 3, alpha: float = 0.5, documents: Optional[List] = None, return_debug: bool = False):
        docs_to_search = documents if documents is not None else self.texts
        if not docs_to_search:
            return [] if not return_debug else ([], pd.DataFrame())

        embedding_results = self.vectorstore.similarity_search_with_score(query, k=len(docs_to_search))
        embedding_scores = {doc.page_content: score for doc, score in embedding_results}

        tokenized_corpus = [self.preprocess(doc.page_content) for doc in docs_to_search]
        bm25 = BM25Okapi(tokenized_corpus)
        bm25_scores = bm25.get_scores(self.preprocess(query))
        bm25_score_dict = {doc.page_content: bm25_scores[i] for i, doc in enumerate(docs_to_search)}

        results, debug_data = [], []
        for doc in docs_to_search:
            e_score = embedding_scores.get(doc.page_content, 0.0)
            b_score = bm25_score_dict.get(doc.page_content, 0.0)
            hybrid_score = alpha * e_score + (1 - alpha) * b_score
            if hybrid_score < 0.2 or (e_score == 0 and b_score == 0):
                continue
            snippet = self.extract_snippet(doc.page_content, query)
            highlighted_snippet = self.highlight_keywords(snippet, query)
            results.append((doc, hybrid_score))
            debug_data.append({
                "Snippet": snippet[:100],
                "BM25": round(b_score, 4),
                "Embedding": round(e_score, 4),
                "Hybrid": round(hybrid_score, 4)
            })

        results = sorted(results, key=lambda x: x[1], reverse=True)[:k]
        final_docs = [doc for doc, _ in results]
        if return_debug:
            return final_docs, pd.DataFrame(debug_data)
        return final_docs
