# utils/search.py

from rank_bm25 import BM25Okapi
from typing import List, Optional
from langchain.docstore.document import Document
from langchain.vectorstores.faiss import FAISS
from langchain.embeddings import SentenceTransformerEmbeddings
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
import pandas as pd
import numpy as np
import re


def load_or_create_vectorstore(documents, index_path="data", model_name="all-MiniLM-L6-v2"):
    embeddings = SentenceTransformerEmbeddings(model_name=model_name, model_kwargs={"device": "cpu"})

    if FAISS.load_local:
        try:
            db = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
            return db
        except:
            pass

    db = FAISS.from_documents(documents, embeddings)
    db.save_local(index_path)
    return db

# ⛔ Stoppwörter (Deutsch + manuell erweitert)
STOPWORDS = set(stopwords.words("german")) | {"eine", "und", "für", "der", "die", "das", "mit", "von", "zur", "zum"}

class HybridRetriever:
    def __init__(self, faiss_index: FAISS, texts: List[Document], embedding_model: SentenceTransformerEmbeddings):
        self.faiss_index = faiss_index
        self.texts = texts
        self.embedding_model = embedding_model

    def preprocess(self, text: str) -> list[str]:
        tokens = re.findall(r'\w+', text.lower())
        return [word for word in tokens if word not in STOPWORDS]

    def extract_snippet(self, chunk: str, query: str, max_len: int = 300):
        sentences = re.split(r'(?<=[.!?]) +', chunk)
        query_tokens = self.preprocess(query)
        scores = [sum(word.lower() in query_tokens for word in re.findall(r'\w+', s)) for s in sentences]
        best_index = np.argmax(scores)
        snippet = sentences[best_index]
        return snippet[:max_len] + ("…" if len(snippet) > max_len else "")

    def highlight_keywords(self, text: str, query: str, threshold: float = 0.75):
        words = list(set(re.findall(r"\w{4,}", text)))
        query_embedding = self.embedding_model.embed_query(query)
        word_embeddings = [self.embedding_model.embed_query(w) for w in words]
        similarities = cosine_similarity([query_embedding], word_embeddings)[0]

        # Manuelle juristische Synonyme
        synonym_map = {
            "Zession": ["Abtretung", "Zessionserklärung"],
            "Kapitalerhöhung": ["Kapitalband", "Erhöhung des Aktienkapitals"],
            "Dienstbarkeit": ["Leitungsrecht", "Wegrecht"],
            "Kaufrecht": ["Vorkaufsrecht", "Vorhandrecht"],
        }

        # Wörter aus Query + bekannten Synonymen
        query_tokens = self.preprocess(query)
        extended_query_terms = set(query_tokens)
        for key, synonyms in synonym_map.items():
            if any(t in query.lower() for t in [key] + synonyms):
                extended_query_terms.update(s.lower() for s in synonyms + [key])

        highlighted = text
        for word, sim in zip(words, similarities):
            if sim >= threshold or word.lower() in extended_query_terms:
                highlighted = re.sub(rf"\b({re.escape(word)})\b", r"<mark>\1</mark>", highlighted, flags=re.IGNORECASE)

        return highlighted

    def search(self, query: str, k: int = 3, alpha: float = 0.5, documents: Optional[List[Document]] = None, return_debug: bool = False):
        docs_to_search = documents if documents is not None else self.texts
        if not docs_to_search:
            return [] if not return_debug else ([], pd.DataFrame())

        embedding_results = self.faiss_index.similarity_search_with_score(query, k=len(docs_to_search))
        embedding_scores = {doc.page_content: score for doc, score in embedding_results}

        tokenized_corpus = [self.preprocess(doc.page_content) for doc in docs_to_search]
        bm25 = BM25Okapi(tokenized_corpus)
        bm25_scores = bm25.get_scores(self.preprocess(query))
        bm25_score_dict = {
            doc.page_content: bm25_scores[i]
            for i, doc in enumerate(docs_to_search)
        }

        results = []
        debug_data = []

        for doc in docs_to_search:
            e_score = embedding_scores.get(doc.page_content, 0.0)
            b_score = bm25_score_dict.get(doc.page_content, 0.0)
            hybrid_score = alpha * e_score + (1 - alpha) * b_score

            if hybrid_score < 0.2 or (e_score == 0 and b_score == 0):
                continue

            snippet = self.extract_snippet(doc.page_content, query)
            highlighted_snippet = self.highlight_keywords(snippet, query)

            new_doc = Document(
                page_content=highlighted_snippet,
                metadata=doc.metadata
            )
            results.append((new_doc, hybrid_score))

            debug_data.append({
                "Ausschnitt": snippet[:100],
                "BM25-Score": round(b_score, 4),
                "Embedding-Score": round(e_score, 4),
                "Hybrid-Score": round(hybrid_score, 4)
            })

        results = sorted(results, key=lambda x: x[1], reverse=True)[:k]
        final_docs = [doc for doc, score in results]

        if return_debug:
            return final_docs, pd.DataFrame(debug_data)
        return final_docs

