# tabs/search_tab.py
import streamlit as st
from utils.search import HybridRetriever

def render(docs, retriever):
    """
    Cloud-Version der Suche:
    - Zeigt Treffer mit Snippet & Highlight
    - Zeigt Dateiname + Kategorie über dem Snippet
    - Ermöglicht Download des Originaldokuments
    """
    if not docs or retriever is None:
        st.warning("⚠️ Keine Dokumente oder Retriever verfügbar.")
        return

    query = st.text_area(
        "Was für ein Dokument suchen Sie?",
        key="query",
        height=100
    )

    if st.button("🔍 Suche") and query.strip():
        results = retriever.search(query, k=10, alpha=0.5)

        if not results:
            st.warning("⚠️ Keine relevanten Dokumente gefunden.")
            return

        st.write(f"{len(results[:3])} relevante Treffer gefunden:")

        for i, doc in enumerate(results[:3]):
