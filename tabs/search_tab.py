# tabs/search_tab.py
import streamlit as st
from utils.result_card import render_result_card
from utils.search import HybridRetriever

def render(docs, retriever: HybridRetriever):
    if not docs or not retriever:
        st.warning("Keine Dokumente oder Retriever verfügbar.")
        return

    # Gewichtung zwischen Embedding- und Keyword-Suche (0 = nur BM25, 1 = nur Embedding)
    alpha = 0.5

    # Texteingabe für die Suchanfrage
    query = st.text_area(
        "Was für eine Vorlage suchen Sie?",
        key="query",
        height=100
    )

    # Button für Suche
    search = st.button("🔍 Suche")

    if search and query.strip():
        # HybridRetriever: eigene .search() Methode nutzen
        results = retriever.search(query, k=10, alpha=alpha)

        # --- Logging ins Session State ---
        st.session_state.search_queries.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "query": query.strip(),
            "results_count": len(results)

        if not results:
            st.warning("⚠️ Keine relevanten Dokumente gefunden.")
        else:
            st.write(f"{len(results)} relevante Treffer gefunden:")

            for i, (doc, score) in enumerate(results):
                # Dateiname und Kategorie anzeigen
                filename = doc.metadata.get("source", "–")
                category = doc.metadata.get("category", "–")
                st.markdown(f"**{filename}**  |  Kategorie: *{category}*  |  Score: {score:.3f}")

                render_result_card(doc, i, query)

                # Download Button
                file_path = f"docs/{filename}"
                try:
                    with open(file_path, "rb") as f:
                        st.download_button(
                            label=f"📄 Download {filename}",
                            data=f,
                            file_name=filename,
                            key=f"download_{i}"
                        )
                except FileNotFoundError:
                    st.error(f"Datei {filename} nicht gefunden.")
