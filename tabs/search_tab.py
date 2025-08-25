# tabs/search_tab.py
import streamlit as st
from utils.search import HybridRetriever
from utils.result_card import render_result_card

def render(docs, retriever):
    """
    Render-Funktion für die Suche in der Cloud-Version.
    """
    if not docs or retriever is None:
        st.warning("⚠️ Keine Dokumente oder Retriever verfügbar.")
        return

    # 🔘 Texteingabe für Suchanfrage
    query = st.text_area(
        "Was für ein Dokument suchen Sie?",
        key="query",
        height=100
    )

    # 🔎 Suche-Button
    if st.button("🔍 Suche") and query.strip():
        results = retriever.search(query, k=10, alpha=0.5)

        if not results:
            st.warning("⚠️ Keine relevanten Dokumente gefunden.")
            return

        st.write(f"{len(results[:3])} relevante Treffer gefunden:")

        for i, doc in enumerate(results[:3]):
            # Karte mit Snippet anzeigen
            render_result_card(doc, i, query)

            # Download-Button für Originaldokument
            source_file = doc.metadata.get("source")
            if source_file:
                file_path = f"docs/{source_file}"
                try:
                    with open(file_path, "rb") as f:
                        st.download_button(
                            label="📄 Dokument herunterladen",
                            data=f,
                            file_name=source_file,
                            mime="application/octet-stream"
                        )
                except FileNotFoundError:
                    st.warning(f"Datei '{source_file}' nicht gefunden.")
