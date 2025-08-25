# tabs/search_tab.py
import streamlit as st
from utils.search import HybridRetriever
from utils.result_card import render_result_card

def render(docs, retriever):
    # 🔹 Kategorie-Filter fix auf "Alle"
    selected_category = "Alle"

    # ✏️ Texteingabe für die Suchanfrage
    query = st.text_area(
        "Was für ein Dokument suchen Sie?",
        key="query",
        height=100
    )

    # 🔘 Such-Button rechts
    spacer, button_col = st.columns([6, 1.5])
    with button_col:
        search = st.button("🔍 Suche", use_container_width=True)

    if search and query.strip():
        # Suche ausführen (HybridRetriever)
        results = retriever.search(query, k=10, alpha=0.5)

        if not results:
            st.warning("⚠️ Keine relevanten Dokumente gefunden.")
            return

        st.write(f"{len(results[:3])} relevante Treffer gefunden:")

        for i, doc in enumerate(results[:3]):
            # Render Result Card
            render_result_card(doc, i, query)

            # Download Button für Originaldokument
            source_file = doc.metadata.get("source")
            if source_file:
                with open(f"docs/{source_file}", "rb") as f:
                    st.download_button(
                        label="📄 Dokument herunterladen",
                        data=f,
                        file_name=source_file,
                        mime="application/octet-stream"
                    )
