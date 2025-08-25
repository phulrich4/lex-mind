import streamlit as st
import os

def render(docs, retriever):
    if not docs or not retriever:
        st.warning("Keine Dokumente oder Retriever verfügbar.")
        return

    query = st.text_area("Was für eine Vorlage suchen Sie?", height=100)
    # show_debug = st.checkbox("🔬 Score-Tabelle anzeigen (Debug-Modus)")

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
                # Snippet mit Highlighting
                st.markdown(f"**{i+1}. {doc.metadata.get('source','Dokument')}**")
                st.markdown(doc.page_content, unsafe_allow_html=True)

                # Download-Button für das Original-Dokument
                source_file = os.path.join("docs", doc.metadata.get("source"))
                if os.path.exists(source_file):
                    with open(source_file, "rb") as f:
                        st.download_button(
                            label="📄 Dokument herunterladen",
                            data=f,
                            file_name=doc.metadata.get("source"),
                            mime="application/octet-stream"
                        )

            if show_debug:
                st.markdown("### 📊 Scoring-Tabelle")
                st.dataframe(debug_df, use_container_width=True)
