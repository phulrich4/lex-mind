import streamlit as st
import os

def render(docs):
    st.subheader("Dokumentenübersicht")

    # Einzigartige Dokumente filtern
    seen = set()
    unique_docs = []
    for doc in docs:
        source = doc.metadata.get("source")
        if source not in seen:
            seen.add(source)
            unique_docs.append(doc)

    st.markdown(f"### 📄 {len(unique_docs)} Dokument(e) geladen:")

    for doc in unique_docs:
        name = os.path.basename(doc.metadata.get("source", "Unbekannt"))
        category = doc.metadata.get("category", "–")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"📄 **{name}**")
        with col2:
            st.write(f"📁 *Kategorie:* `{category}`")

