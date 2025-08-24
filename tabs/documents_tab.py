import streamlit as st
import os

def render(docs):
    # Einzigartige Dokumente filtern
    seen = set()
    unique_docs = []
    for doc in docs:
        source = doc.metadata.get("source")
        if source not in seen:
            seen.add(source)
            unique_docs.append(doc)

    # Titel mit Anzahl
    st.subheader(f"Dokumentenübersicht – Total {len(unique_docs)} Vorlagen")

    # Dokumentliste
    for doc in unique_docs:
        name = os.path.basename(doc.metadata.get("source", "Unbekannt"))
        category = doc.metadata.get("category", "–")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"📄 **{name}**")
        with col2:
            st.write(f"📁 *Kategorie:* `{category}`")


