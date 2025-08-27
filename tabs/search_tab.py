# tabs/search_tab.py
import streamlit as st
from utils.result_card import render_result_card
from utils.search import HybridRetriever

def render(docs, retriever):
    if not docs or not retriever:
        st.warning("Keine Dokumente oder Retriever verfügbar.")
        return

    # Suchmodus fix auf Hybrid
    alpha = 0.5

    # Texteingabe für die Suchanfrage
    query = st.text_area(
        "Was für eine Vorlage suchen Sie?",
        key="query",
        height=100
    )

    search = st.button("🔍 Suche")

    if search and query.strip():
        results = retriever.get_relevant_documents(query)
        if not results:
            st.warning("⚠️ Keine relevanten Dokumente gefunden.")
        else:
            st.write(f"{len(results)} relevante Treffer gefunden:")
            for i, doc in enumerate(results):
                # Dateiname und Kategorie anzeigen
                filename = doc.metadata.get("source", "–")
                category = doc.metadata.get("category", "–")
                st.markdown(f"**{filename}**  |  Kategorie: *{category}*")

                # Snippet mit Highlight
                render_result_card(doc, i, query)

                # Download Button
                file_path = f"docs/{filename}"
                if st.button(f"📄 Download {filename}", key=f"download_{i}"):
                    with open(file_path, "rb") as f:
                        st.download_button(
                            label="Download",
                            data=f,
                            file_name=filename
                        )
