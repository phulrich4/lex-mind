# tabs/search_tab.py
import streamlit as st
from utils.result_card import render_result_card
from utils.search import HybridRetriever
from datetime import datetime

def render(docs, retriever: HybridRetriever):
    if not docs or not retriever:
        st.warning("Keine Dokumente oder Retriever verfügbar.")
        return

    alpha = 0.5  # Gewichtung Embedding vs. BM25

    # Suchfeld
    query = st.text_area(
        "Was für eine Vorlage suchen Sie?",
        key="query",
        height=100
    )

    # Suche starten
    search = st.button("🔍 Suche")

    if search and query.strip():
        results = retriever.search(query, k=10, alpha=alpha)

        # Logging
        st.session_state.search_queries.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "query": query.strip(),
            "results_count": len(results)
        })

        if not results:
            st.warning("⚠️ Keine relevanten Dokumente gefunden.")
        else:
            st.write(f"{len(results)} relevante Treffer gefunden:")

            for i, (doc, score) in enumerate(results):
                render_result_card(doc, i, query, retriever.embedding_model, score)
