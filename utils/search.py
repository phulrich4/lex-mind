# utils/search.py

from typing import List, Optional
import re
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi
from langchain.docstore.document import Document
from langchain_core.vectorstores.in_memory import InMemoryVectorStore
from langchain_community.embeddings import SentenceTransformerEmbeddings

# ⛔ Feste deutsche Stoppwörter (kein NLTK Download nötig)
STOPWORDS = {
    "eine","und","für","der","die","das","mit","von","zur","zum",
    "im","des","den","dem","ist","sind","auf","an","in","als","bei","auch",
    "oder","nicht","wie","so","wir","sie","er","es","hat","haben","dass"
}

# -------------------------------
# Vectorstore erstellen
# -------------------------------
def load_or_create_vectorstore(documents: List[Document], model_name="all-MiniLM-L6-v2"):
    embeddings = SentenceTransformerEmbeddings(model_name=model_name, model_kwargs={"device": "cpu"})
    db = InMemoryVectorStore.from_documents(documents, embeddings)
    return db


# -------------------------------
# Hybrid Retriever: FAISS + BM25
# -------------------------------
class HybridRetriever:
    def __init__(self, vectorstore: InMemoryVectorStore, texts: List[Document], embedding_model: SentenceTransformerEmbeddings):
        self.vectorstore = vectorstore
        self.texts = texts
        self.embedding_model = embedding_model

    # Tokenizer & Stopwords
    def preprocess(self, text: str) -> list[str]:
        tokens = re.findall(r'\w+', text.lower())
        return [t for t in tokens if t not in STOPWORDS]

    # Beste Satz-Snippet für Query extrahieren
    def extract_snippet(self, chunk: str, query: str, max_len: int = 300):
        sentences = re.split(r'(?<=[.!?]) +', chunk)
        query_tokens = self.preprocess(query)
        scores = [sum(word in query_tokens for word in re.findall(r'\w+', s.lower())) for s in sentences]
        best_idx = int(np.argmax(scores)) if scores else 0
        snippet = sentences[best_idx] if sentences else chunk
        return snippet[:max_len] + ("…" if len(snippet) > max_len else "")

    # Semantisches Highlighting inkl. Synonyme
    def highlight_keywords(self, text: str, query: str, threshold: float = 0.75):
        words = list(set(re.findall(r'\w{4,}', text)))
        query_embedding = self.embedding_model.embed_query(query)
        word_embeddings = [self.embedding_model.embed_query(w) for w in words]
        similarities = cosine_similarity([query_embedding], word_embeddings)[0]

        # Juristische Synonyme
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

    # Suche durchführen
    def search(self, query: str, k: int = 3, alpha: float = 0.5, documents: Optional[List[Document]] = None, return_debug: bool = False):
        docs_to_search = documents if documents is not None else self.texts
        if not docs_to_search:
            return [] if not return_debug else ([], pd.DataFrame())

        # Embedding Scores via FAISS
        embedding_results = self.vectorstore.similarity_search_with_relevance_scores(query, k=len(docs_to_search))
        embedding_scores = {doc.page_content: score for doc, score in embedding_results}

        # BM25 Scores
        tokenized_corpus = [self.preprocess(doc.page_content) for doc in docs_to_search]
        bm25 = BM25Okapi(tokenized_corpus)
        bm25_scores = bm25.get_scores(self.preprocess(query))
        bm25_score_dict = {doc.page_content: bm25_scores[i] for i, doc in enumerate(docs_to_search)}

        # Hybrid Score & Snippet
        results, debug_data = [], []
        for doc in docs_to_search:
            e_score = embedding_scores.get(doc.page_content, 0.0)
            b_score = bm25_score_dict.get(doc.page_content, 0.0)
            hybrid_score = alpha * e_score + (1 - alpha) * b_score
            if hybrid_score < 0.2 or (e_score == 0 and b_score == 0):
                continue
            snippet = self.extract_snippet(doc.page_content, query)
            highlighted_snippet = self.highlight_keywords(snippet, query)
            results.append((Document(page_content=highlighted_snippet, metadata=doc.metadata), hybrid_score))
            debug_data.append({
                "Snippet": snippet[:100],
                "BM25": round(b_score, 4),
                "Embedding": round(e_score, 4),
                "Hybrid": round(hybrid_score, 4)
            })

        # Top-k Ergebnisse
        results = sorted(results, key=lambda x: x[1], reverse=True)[:k]
        final_docs = [doc for doc, _ in results]
        if return_debug:
            return final_docs, pd.DataFrame(debug_data)
        return final_docs
