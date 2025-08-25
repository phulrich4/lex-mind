import streamlit as st
from utils.result_card import render_result_card

def render(docs, retriever):
    if not docs or not retriever:
        st.warning("Keine Dokumente oder Retriever verfügbar.")
        return

    query = st.text_area("Was für ein Dokument suchen Sie?", height=100)
    show_debug = st.checkbox("🔬 Score-Tabelle anzeigen (Debug-Modus)")

    spacer, button_col = st.columns([6, 1.5])
    with button_col:
        search = st.button("🔍 Suche", use_container_width=True)
        reset = st.button("🔁 Zurücksetzen", use_container_width=True)

    if reset:
        st.session_state.query = ""
        st.experimental_rerun()

    if search and query.strip():
        if show_debug:
            results, debug_df = retriever.search(query, k=10, alpha=0.5, return_debug=True)
        else:
            results = retriever.search(query, k=10, alpha=0.5)

        if not results:
            st.warning("⚠️ Keine relevanten Dokumente gefunden.")
        else:
            st.write(f"{len(results[:3])} relevante Treffer gefunden:")
            for i, doc in enumerate(results[:3]):
                render_result_card(doc, i, query, retriever.embedding_model)

            if show_debug:
                st.markdown("### 📊 Scoring-Tabelle")
                st.dataframe(debug_df, use_container_width=True)
